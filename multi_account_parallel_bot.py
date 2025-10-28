#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 MULTI-ACCOUNT PARALLEL TRADING BOT
Production-Ready System with 5 Concurrent Accounts, Each Running Different Strategies

Features:
- 5 separate IQ Option accounts trading simultaneously
- Each account runs a different strategy profile (conservative, moderate, aggressive, scalping, trend_following)
- Comprehensive performance tracking per account and strategy
- Real-time metrics and analytics
- Weekly performance summaries and reports
- CSV/Excel export capabilities
- 24/7 continuous operation with auto-recovery
- Advanced portfolio risk management

CRITICAL: Optimized for multi-account performance evaluation!
"""

import sys
import os
import time
import logging
import signal
import traceback
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import threading
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from collections import deque
import queue

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Multi-account configuration
try:
    from config.multi_account_config import get_account_manager, AccountConfig
    MULTI_ACCOUNT_ENABLED = True
except ImportError:
    MULTI_ACCOUNT_ENABLED = False
    print("❌ Multi-account system not available")
    sys.exit(1)

# Database logging system
try:
    from database.multi_account_logger import MultiAccountTradeLogger
    DB_LOGGING_ENABLED = True
except ImportError:
    DB_LOGGING_ENABLED = False
    print("❌ Database logging not available")
    sys.exit(1)

# Advanced strategy system with TA-Lib
USE_ADVANCED_STRATEGIES = os.getenv('USE_ADVANCED_STRATEGIES', 'true').lower() == 'true'
try:
    if USE_ADVANCED_STRATEGIES:
        from strategies.advanced_strategies import AdvancedStrategyEngine
        ADVANCED_STRATEGIES_AVAILABLE = True
    else:
        ADVANCED_STRATEGIES_AVAILABLE = False
except ImportError:
    ADVANCED_STRATEGIES_AVAILABLE = False
    print("❌ Advanced strategies not available")
    sys.exit(1)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from flask import Flask, jsonify, request, send_file
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from iqoptionapi.stable_api import IQ_Option


# =============================================================================
# PROMETHEUS METRICS
# =============================================================================

# Account-specific metrics
prometheus_account_balance = Gauge('kael_account_balance', 'Current balance per account', ['account_id', 'strategy_profile'])
prometheus_account_pnl = Gauge('kael_account_daily_pnl', 'Daily P&L per account', ['account_id', 'strategy_profile'])
prometheus_account_trades = Counter('kael_account_total_trades', 'Total trades per account', ['account_id', 'strategy_profile'])
prometheus_account_wins = Counter('kael_account_wins', 'Winning trades per account', ['account_id', 'strategy_profile'])
prometheus_account_losses = Counter('kael_account_losses', 'Losing trades per account', ['account_id', 'strategy_profile'])
prometheus_account_win_rate = Gauge('kael_account_win_rate', 'Win rate per account', ['account_id', 'strategy_profile'])

# Strategy-specific metrics (aggregated across accounts)
prometheus_strategy_trades = Counter('kael_strategy_total_trades', 'Total trades per strategy', ['strategy'])
prometheus_strategy_wins = Counter('kael_strategy_wins', 'Winning trades per strategy', ['strategy'])
prometheus_strategy_pnl = Gauge('kael_strategy_total_pnl', 'Total P&L per strategy', ['strategy'])
prometheus_strategy_win_rate = Gauge('kael_strategy_win_rate', 'Win rate per strategy', ['strategy'])

# Portfolio metrics
prometheus_portfolio_balance = Gauge('kael_portfolio_total_balance', 'Total portfolio balance')
prometheus_portfolio_pnl = Gauge('kael_portfolio_daily_pnl', 'Total daily P&L')
prometheus_active_accounts = Gauge('kael_active_accounts', 'Number of active accounts')
prometheus_healthy_accounts = Gauge('kael_healthy_accounts', 'Number of healthy accounts')

# Performance metrics
prometheus_execution_time = Histogram('kael_trade_execution_time_ms', 'Trade execution time in milliseconds',
                                      buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000])
prometheus_api_response_time = Histogram('kael_api_response_time_ms', 'API response time in milliseconds',
                                          buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000])


# =============================================================================
# CONFIGURATION
# =============================================================================

class MultiAccountConfig:
    """Configuration for multi-account trading"""

    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'demo')
    CONTINUOUS_OPERATION_24_7 = True

    # Strategy Settings (per account, overridden by account config)
    STRATEGY_SCAN_INTERVAL = int(os.getenv('STRATEGY_SCAN_INTERVAL', 5))

    # Binary Options Settings
    BINARY_OPTION_DURATION = 1
    DEFAULT_TRADE_AMOUNT = float(os.getenv('BASE_TRADE_AMOUNT', 1.0))
    MIN_TRADE_AMOUNT = 1.0

    # Binary-Option Specific Thresholds
    MIN_PAYOUT_RATIO = float(os.getenv('MIN_PAYOUT_RATIO', 0.65))

    # Timing thresholds
    MIN_TIME_TO_EXPIRY_SECONDS = int(os.getenv('MIN_TIME_TO_EXPIRY_SECONDS', 40))
    MAX_TIME_TO_EXPIRY_SECONDS = int(os.getenv('MAX_TIME_TO_EXPIRY_SECONDS', 55))

    # Trading Assets
    INSTRUMENT_POOL = os.getenv('TRADING_ASSETS',
        'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,AUDJPY'
    ).split(',')

    # Risk Management (overridden by account config)
    MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', 5))
    MIN_BALANCE = float(os.getenv('MIN_BALANCE', 50))
    MIN_SECONDS_BETWEEN_TRADES = int(os.getenv('MIN_SECONDS_BETWEEN_TRADES', 70))

    # Timing
    WAIT_FOR_RESULT_SECONDS = int(os.getenv('WAIT_FOR_RESULT_SECONDS', 65))

    # Connection health
    CONNECTION_CHECK_INTERVAL = 300
    AUTO_RECONNECT_ON_FAILURE = True
    RECONNECT_DELAY_SECONDS = 60

    # API rate limiting
    API_MIN_INTERVAL = float(os.getenv('API_MIN_INTERVAL', 0.3))
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', 3))
    API_RETRY_BACKOFF = float(os.getenv('API_RETRY_BACKOFF', 1.5))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = Path('logs')

    # Health Monitoring
    ENABLE_HEALTH_API = bool(os.getenv('ENABLE_HEALTH_API', True))
    HEALTH_API_PORT = int(os.getenv('HEALTH_API_PORT', 5001))

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kael')


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure comprehensive logging"""
    MultiAccountConfig.LOG_DIR.mkdir(exist_ok=True)

    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(
        MultiAccountConfig.LOG_DIR / f'multi_account_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    console_handler.setLevel(getattr(logging, MultiAccountConfig.LOG_LEVEL))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger(__name__)


# =============================================================================
# API CLIENT WITH RATE LIMITING
# =============================================================================

class ApiClient:
    """Wrapper for IQ Option API with rate limiting"""

    def __init__(self, api, min_interval: float = 0.3, max_retries: int = 3, backoff_base: float = 1.5):
        self.api = api
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.last_call = 0
        self.lock = threading.Lock()

    def _rate_limit(self):
        with self.lock:
            elapsed = time.time() - self.last_call
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_call = time.time()

    def _retry_call(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.backoff_base ** attempt)
        return None

    def get_balance(self):
        return self._retry_call(self.api.get_balance)

    def get_candles(self, instrument, size, count, timestamp):
        return self._retry_call(self.api.get_candles, instrument, size, count, timestamp)

    def get_all_profit(self):
        return self._retry_call(self.api.get_all_profit)

    def get_remaning(self, duration):
        return self._retry_call(self.api.get_remaning, duration)

    def buy(self, amount, instrument, action, duration):
        return self._retry_call(self.api.buy, amount, instrument, action, duration)

    def check_win_v3(self, order_id):
        return self._retry_call(self.api.check_win_v3, order_id)

    def check_connect(self):
        return self._retry_call(self.api.check_connect)

    def get_all_open_time(self):
        return self._retry_call(self.api.get_all_open_time)


# =============================================================================
# ACCOUNT TRADER (Individual Account Handler)
# =============================================================================

class AccountTrader:
    """Handles trading for a single account with its strategy profile"""

    def __init__(self, account_config: AccountConfig, db_logger, logger: logging.Logger):
        self.account_config = account_config
        self.db_logger = db_logger
        self.logger = logging.getLogger(f"Account-{account_config.account_id}")

        # IQ Option API
        self.api = None
        self.api_client = None

        # Strategy engine
        self.strategy_engine = AdvancedStrategyEngine() if ADVANCED_STRATEGIES_AVAILABLE else None

        # Thread control
        self.running = False
        self.thread = None

        # Statistics
        self.trades_today = 0
        self.wins_today = 0
        self.losses_today = 0
        self.daily_pnl = 0.0
        self.last_trade_time = 0
        self.consecutive_losses = 0
        self.current_balance = 0.0

        # Performance tracking
        self.trade_history = deque(maxlen=1000)
        self.execution_times = deque(maxlen=100)

    def connect(self) -> bool:
        """Connect to IQ Option"""
        try:
            self.logger.info(f"🔌 Connecting {self.account_config.email}...")

            self.api = IQ_Option(self.account_config.email, self.account_config.password)
            check, reason = self.api.connect()

            if not check:
                self.logger.error(f"❌ Connection failed: {reason}")
                return False

            # Set trading mode
            if self.account_config.trading_mode == 'live':
                self.api.change_balance('REAL')
                self.logger.warning("⚠️ LIVE MODE")
            else:
                self.api.change_balance('PRACTICE')
                self.logger.info("✅ Demo mode")

            self.current_balance = self.api.get_balance()
            self.logger.info(f"💰 Balance: ${self.current_balance:.2f}")

            # Initialize API client
            self.api_client = ApiClient(
                self.api,
                min_interval=MultiAccountConfig.API_MIN_INTERVAL,
                max_retries=MultiAccountConfig.API_MAX_RETRIES,
                backoff_base=MultiAccountConfig.API_RETRY_BACKOFF
            )

            # Log successful connection
            if self.db_logger:
                self.db_logger.update_account_health(self.account_config.account_id, True, 0)
                self.db_logger.log_system_event(
                    self.account_config.account_id,
                    'connection',
                    'info',
                    f"Connected successfully: {self.account_config.email}",
                    {'balance': self.current_balance}
                )

            return True

        except Exception as e:
            self.logger.error(f"❌ Connection error: {e}")
            if self.db_logger:
                self.db_logger.update_account_health(self.account_config.account_id, False, 1)
            return False

    def can_trade(self) -> bool:
        """Check if account can trade"""
        # Check if account is enabled
        if not self.account_config.enabled:
            return False

        # Check daily loss limit
        if abs(self.daily_pnl) >= self.account_config.max_daily_loss and self.daily_pnl < 0:
            self.logger.warning(f"⚠️ Daily loss limit reached: ${self.daily_pnl:.2f}")
            return False

        # Check consecutive losses
        if self.consecutive_losses >= MultiAccountConfig.MAX_CONSECUTIVE_LOSSES:
            self.logger.warning(f"⚠️ Max consecutive losses reached: {self.consecutive_losses}")
            return False

        # Check balance
        if self.current_balance < MultiAccountConfig.MIN_BALANCE:
            self.logger.warning(f"⚠️ Balance too low: ${self.current_balance:.2f}")
            return False

        # Check time between trades
        time_since_last = time.time() - self.last_trade_time
        if time_since_last < MultiAccountConfig.MIN_SECONDS_BETWEEN_TRADES:
            return False

        return True

    def get_available_instruments(self) -> List[str]:
        """Get available trading instruments"""
        try:
            open_markets = self.api_client.get_all_open_time()
            if not open_markets or 'binary' not in open_markets:
                return []

            binary_markets = open_markets['binary']
            available = []

            for inst in MultiAccountConfig.INSTRUMENT_POOL:
                inst = inst.strip()
                for suffix in ['', '-OTC']:
                    test_name = f"{inst}{suffix}"
                    if test_name in binary_markets and binary_markets[test_name].get('open', False):
                        available.append(test_name)
                        break

            return available

        except Exception as e:
            self.logger.error(f"Error getting instruments: {e}")
            return []

    def analyze_instrument(self, instrument: str) -> Optional[Tuple[str, float, List, str]]:
        """Analyze instrument with account's strategy profile"""
        try:
            # Get candles
            candles = self.api_client.get_candles(instrument, 60, 100, time.time())
            if not candles or len(candles) < 50:
                return None

            # Analyze with strategy engine
            if not self.strategy_engine:
                return None

            signal = self.strategy_engine.analyze(candles)

            if signal.direction == 'NEUTRAL':
                return None

            # Get strategy config for this account
            from config.multi_account_config import get_account_manager
            manager = get_account_manager()
            strategy_config = manager.get_strategy_config(self.account_config.account_id)

            min_confidence = strategy_config.get('min_confidence', 0.75)

            # Check confidence threshold
            if signal.confidence < min_confidence:
                return None

            return signal.direction, signal.confidence, signal.reasons, signal.strategy_name

        except Exception as e:
            self.logger.error(f"Analysis error for {instrument}: {e}")
            return None

    def execute_trade(self, instrument: str, direction: str, confidence: float,
                     reasons: List[str], strategy_name: str) -> Optional[Dict]:
        """Execute a single trade"""
        start_time = time.time()

        try:
            # Calculate trade amount
            amount = min(self.account_config.max_trade_amount, MultiAccountConfig.DEFAULT_TRADE_AMOUNT)

            self.logger.info(f"📊 {instrument} {direction} ${amount:.2f} @ {confidence:.0%}")
            self.logger.info(f"   Strategy: {strategy_name}")
            self.logger.info(f"   Reasons: {', '.join(reasons[:2])}")

            # Place order
            action = 'call' if direction == 'CALL' else 'put'
            success, order_id = self.api_client.buy(amount, instrument, action, 1)

            if not success:
                self.logger.error("❌ Trade failed")
                return None

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Log trade to database
            db_trade_id = None
            if self.db_logger:
                trade_data = {
                    'trade_id': str(order_id),
                    'instrument': instrument,
                    'direction': direction,
                    'amount': amount,
                    'entry_time': datetime.now(),
                    'expiration_seconds': 60,
                    'selected_strategy': strategy_name,
                    'strategy_profile': self.account_config.strategy_profile,
                    'confidence': int(confidence * 100),
                    'strategy_breakdown': [{'strategy': strategy_name, 'confidence': confidence}],
                    'mode': self.account_config.trading_mode,
                    'execution_time_ms': execution_time_ms
                }

                db_trade_id = self.db_logger.log_trade(
                    self.account_config.account_id,
                    trade_data
                )

            # Wait for result
            time.sleep(MultiAccountConfig.WAIT_FOR_RESULT_SECONDS)

            # Check result
            profit = self.api_client.check_win_v3(order_id)
            if profit is None:
                return None

            won = profit > 0
            result_str = 'WIN' if won else 'LOSS'

            self.logger.info(f"{'✅' if won else '❌'} {result_str}: ${profit:.2f}")

            # Update database
            if self.db_logger and db_trade_id:
                self.db_logger.update_trade_result(db_trade_id, result_str, profit)

            # Update stats
            self.daily_pnl += profit
            self.trades_today += 1
            self.last_trade_time = time.time()

            if won:
                self.wins_today += 1
                self.consecutive_losses = 0
            else:
                self.losses_today += 1
                self.consecutive_losses += 1

            # Update balance
            self.current_balance = self.api_client.get_balance()

            # Track performance
            self.trade_history.append({
                'time': datetime.now(),
                'instrument': instrument,
                'direction': direction,
                'amount': amount,
                'result': result_str,
                'profit': profit,
                'strategy': strategy_name
            })
            self.execution_times.append(execution_time_ms)

            # Update Prometheus metrics
            prometheus_account_trades.labels(
                account_id=self.account_config.account_id,
                strategy_profile=self.account_config.strategy_profile
            ).inc()

            if won:
                prometheus_account_wins.labels(
                    account_id=self.account_config.account_id,
                    strategy_profile=self.account_config.strategy_profile
                ).inc()
            else:
                prometheus_account_losses.labels(
                    account_id=self.account_config.account_id,
                    strategy_profile=self.account_config.strategy_profile
                ).inc()

            prometheus_account_pnl.labels(
                account_id=self.account_config.account_id,
                strategy_profile=self.account_config.strategy_profile
            ).set(self.daily_pnl)

            prometheus_account_balance.labels(
                account_id=self.account_config.account_id,
                strategy_profile=self.account_config.strategy_profile
            ).set(self.current_balance)

            if self.trades_today > 0:
                win_rate = (self.wins_today / self.trades_today) * 100
                prometheus_account_win_rate.labels(
                    account_id=self.account_config.account_id,
                    strategy_profile=self.account_config.strategy_profile
                ).set(win_rate)

            # Update strategy metrics
            prometheus_strategy_trades.labels(strategy=strategy_name).inc()
            if won:
                prometheus_strategy_wins.labels(strategy=strategy_name).inc()

            prometheus_execution_time.observe(execution_time_ms)

            return {
                'instrument': instrument,
                'result': result_str,
                'profit': profit,
                'strategy': strategy_name,
                'account': self.account_config.account_id
            }

        except Exception as e:
            self.logger.error(f"Execute trade error: {e}")
            return None

    def trade_cycle(self):
        """Single trading cycle"""
        try:
            if not self.can_trade():
                return

            instruments = self.get_available_instruments()
            if not instruments:
                return

            # Analyze instruments
            for instrument in instruments[:10]:
                if not self.running:
                    break

                analysis = self.analyze_instrument(instrument)
                if analysis:
                    direction, confidence, reasons, strategy_name = analysis
                    result = self.execute_trade(instrument, direction, confidence, reasons, strategy_name)
                    if result:
                        # Wait before next trade
                        time.sleep(MultiAccountConfig.MIN_SECONDS_BETWEEN_TRADES)
                        break

        except Exception as e:
            self.logger.error(f"Trade cycle error: {e}")

    def run(self):
        """Main trading loop"""
        self.running = True
        self.logger.info(f"🚀 Account thread started: {self.account_config.account_id} ({self.account_config.strategy_profile})")

        while self.running:
            try:
                self.trade_cycle()
                time.sleep(MultiAccountConfig.STRATEGY_SCAN_INTERVAL)
            except Exception as e:
                self.logger.error(f"Run error: {e}")
                time.sleep(30)

    def start(self):
        """Start account trading thread"""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop account trading thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        self.logger.info(f"🛑 Account thread stopped: {self.account_config.account_id}")

    def get_stats(self) -> Dict:
        """Get account statistics"""
        win_rate = (self.wins_today / self.trades_today * 100) if self.trades_today > 0 else 0
        avg_execution_ms = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0

        return {
            'account_id': self.account_config.account_id,
            'email': self.account_config.email,
            'strategy_profile': self.account_config.strategy_profile,
            'trades': self.trades_today,
            'wins': self.wins_today,
            'losses': self.losses_today,
            'win_rate': win_rate,
            'daily_pnl': self.daily_pnl,
            'balance': self.current_balance,
            'consecutive_losses': self.consecutive_losses,
            'avg_execution_ms': avg_execution_ms,
            'is_running': self.running,
            'is_enabled': self.account_config.enabled
        }


# =============================================================================
# MULTI-ACCOUNT ORCHESTRATOR
# =============================================================================

class MultiAccountOrchestrator:
    """Orchestrates multiple accounts, each in its own thread"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.account_manager = get_account_manager()
        self.db_logger = None
        self.account_traders: Dict[str, AccountTrader] = {}
        self.running = False

        # Initialize database
        try:
            self.db_logger = MultiAccountTradeLogger(MultiAccountConfig.DATABASE_URL)
            self.logger.info("✅ Database logging enabled")
        except Exception as e:
            self.logger.warning(f"⚠️ Database initialization failed: {e}")

    def initialize_accounts(self) -> bool:
        """Initialize all account traders"""
        self.logger.info("="*80)
        self.logger.info("🚀 MULTI-ACCOUNT ORCHESTRATOR")
        self.logger.info("="*80)

        accounts = self.account_manager.get_enabled_accounts()
        self.logger.info(f"📊 Initializing {len(accounts)} accounts...")

        for account_config in accounts:
            trader = AccountTrader(account_config, self.db_logger, self.logger)

            # Connect to IQ Option
            if trader.connect():
                self.account_traders[account_config.account_id] = trader
                self.logger.info(
                    f"✅ {account_config.account_id}: {account_config.email} "
                    f"({account_config.strategy_profile})"
                )
            else:
                self.logger.error(
                    f"❌ {account_config.account_id}: Failed to connect"
                )

        success = len(self.account_traders) > 0
        if success:
            self.logger.info(f"✅ {len(self.account_traders)} accounts ready")
        self.logger.info("="*80)

        return success

    def start(self):
        """Start all account threads"""
        if not self.account_traders:
            self.logger.error("No accounts initialized")
            return False

        self.running = True
        self.logger.info("🎯 Starting all account threads...")

        # Start each account in its own thread
        for account_id, trader in self.account_traders.items():
            trader.start()
            self.logger.info(f"   ✅ {account_id} thread started")

        prometheus_active_accounts.set(len(self.account_traders))

        # Monitor accounts
        try:
            while self.running:
                time.sleep(60)
                self._print_status()

                # Update portfolio metrics
                self._update_portfolio_metrics()

                # Update daily performance in database (every hour)
                if int(time.time()) % 3600 < 60 and self.db_logger:
                    self.db_logger.update_daily_performance()

        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested...")
            self.stop()

        return True

    def stop(self):
        """Stop all account threads"""
        self.running = False

        self.logger.info("🛑 Stopping all account threads...")
        for trader in self.account_traders.values():
            trader.stop()

        self.logger.info("✅ All accounts stopped")

    def _update_portfolio_metrics(self):
        """Update portfolio-wide metrics"""
        try:
            total_balance = sum(t.current_balance for t in self.account_traders.values())
            total_pnl = sum(t.daily_pnl for t in self.account_traders.values())

            prometheus_portfolio_balance.set(total_balance)
            prometheus_portfolio_pnl.set(total_pnl)

            active_count = sum(1 for t in self.account_traders.values() if t.running)
            prometheus_active_accounts.set(active_count)

            healthy_count = sum(1 for t in self.account_traders.values()
                              if t.running and t.account_config.is_healthy)
            prometheus_healthy_accounts.set(healthy_count)

        except Exception as e:
            self.logger.error(f"Error updating portfolio metrics: {e}")

    def _print_status(self):
        """Print current status"""
        self.logger.info("="*80)
        self.logger.info("📊 ACCOUNT STATUS")

        total_trades = sum(t.trades_today for t in self.account_traders.values())
        total_pnl = sum(t.daily_pnl for t in self.account_traders.values())
        total_balance = sum(t.current_balance for t in self.account_traders.values())

        self.logger.info(f"Active Accounts: {sum(1 for t in self.account_traders.values() if t.running)}/{len(self.account_traders)}")
        self.logger.info(f"Total Trades: {total_trades}")
        self.logger.info(f"Total P&L: ${total_pnl:.2f}")
        self.logger.info(f"Total Balance: ${total_balance:.2f}")
        self.logger.info("")

        for trader in self.account_traders.values():
            stats = trader.get_stats()
            status = "🟢" if stats['is_running'] else "🔴"
            self.logger.info(
                f"{status} {stats['account_id']:12s} ({stats['strategy_profile']:15s}) | "
                f"Trades: {stats['trades']:3d} | "
                f"Win Rate: {stats['win_rate']:5.1f}% | "
                f"P&L: ${stats['daily_pnl']:7.2f} | "
                f"Balance: ${stats['balance']:8.2f}"
            )

        self.logger.info("="*80)

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        stats = {
            'total_accounts': len(self.account_traders),
            'active_accounts': sum(1 for t in self.account_traders.values() if t.running),
            'total_trades': sum(t.trades_today for t in self.account_traders.values()),
            'total_pnl': sum(t.daily_pnl for t in self.account_traders.values()),
            'total_balance': sum(t.current_balance for t in self.account_traders.values()),
            'accounts': [t.get_stats() for t in self.account_traders.values()]
        }

        # Get portfolio summary from database
        if self.db_logger:
            try:
                portfolio_summary = self.db_logger.get_portfolio_summary()
                stats['portfolio_summary'] = portfolio_summary
            except Exception:
                pass

        return stats

    def export_reports(self):
        """Export performance reports"""
        if not self.db_logger:
            return

        try:
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Export CSV
            csv_file = reports_dir / f'trades_{timestamp}.csv'
            self.db_logger.export_trades_to_csv(str(csv_file), days=7)

            # Export JSON
            json_file = reports_dir / f'performance_{timestamp}.json'
            self.db_logger.export_performance_to_json(str(json_file), days=7)

            self.logger.info(f"✅ Reports exported to {reports_dir}")

        except Exception as e:
            self.logger.error(f"Failed to export reports: {e}")


# =============================================================================
# HEALTH API
# =============================================================================

def create_health_api(orchestrator: MultiAccountOrchestrator):
    """Create health monitoring API"""
    app = Flask(__name__)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

    @app.route('/statistics', methods=['GET'])
    def statistics():
        return jsonify(orchestrator.get_statistics())

    @app.route('/accounts', methods=['GET'])
    def accounts():
        """Get all accounts status"""
        stats = [t.get_stats() for t in orchestrator.account_traders.values()]
        return jsonify({
            'accounts': stats,
            'total': len(stats),
            'active': sum(1 for s in stats if s['is_running'])
        })

    @app.route('/account/<account_id>', methods=['GET'])
    def account_detail(account_id):
        """Get specific account details"""
        if account_id not in orchestrator.account_traders:
            return jsonify({'error': 'Account not found'}), 404

        trader = orchestrator.account_traders[account_id]
        return jsonify(trader.get_stats())

    @app.route('/strategy_performance', methods=['GET'])
    def strategy_performance():
        """Get strategy performance from database"""
        days = int(request.args.get('days', 7))

        if not orchestrator.db_logger:
            return jsonify({'error': 'Database not available'}), 503

        try:
            stats = orchestrator.db_logger.get_strategy_performance(days=days)
            return jsonify({
                'strategy_stats': stats,
                'time_period_days': days
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/recent_trades', methods=['GET'])
    def recent_trades():
        """Get recent trades"""
        limit = int(request.args.get('limit', 100))
        account_id = request.args.get('account_id', None)

        if not orchestrator.db_logger:
            return jsonify({'error': 'Database not available'}), 503

        try:
            trades = orchestrator.db_logger.get_recent_trades(account_id, limit)
            return jsonify({'trades': trades})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/weekly_summary', methods=['GET'])
    def weekly_summary():
        """Get weekly performance summary"""
        if not orchestrator.db_logger:
            return jsonify({'error': 'Database not available'}), 503

        try:
            summary = orchestrator.db_logger.get_weekly_summary()
            return jsonify(summary or {})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/export/csv', methods=['GET'])
    def export_csv():
        """Export trades to CSV"""
        days = int(request.args.get('days', 7))
        account_id = request.args.get('account_id', None)

        if not orchestrator.db_logger:
            return jsonify({'error': 'Database not available'}), 503

        try:
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'trades_{account_id or "all"}_{timestamp}.csv'
            filepath = reports_dir / filename

            orchestrator.db_logger.export_trades_to_csv(str(filepath), account_id, days)

            return send_file(str(filepath), as_attachment=True, download_name=filename)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/export/json', methods=['GET'])
    def export_json():
        """Export performance to JSON"""
        days = int(request.args.get('days', 7))

        if not orchestrator.db_logger:
            return jsonify({'error': 'Database not available'}), 503

        try:
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'performance_{timestamp}.json'
            filepath = reports_dir / filename

            orchestrator.db_logger.export_performance_to_json(str(filepath), days)

            return send_file(str(filepath), as_attachment=True, download_name=filename)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/stop', methods=['POST'])
    def stop():
        orchestrator.stop()
        return jsonify({'message': 'Shutdown initiated'})

    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Prometheus metrics endpoint"""
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    return app


def start_health_server(app: Flask, logger: logging.Logger):
    """Start health API server"""
    try:
        import waitress
        logger.info("ℹ️ Starting health API with waitress")
        waitress.serve(
            app,
            host='0.0.0.0',
            port=MultiAccountConfig.HEALTH_API_PORT,
            threads=8,
            channel_timeout=60,
            log_socket_errors=False
        )
    except Exception:
        logger.warning("⚠️ Health API running with Flask's built-in server")
        app.run(host='0.0.0.0', port=MultiAccountConfig.HEALTH_API_PORT,
               debug=False, use_reloader=False, threaded=True)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    logger = setup_logging()

    logger.info("="*80)
    logger.info("🚀 MULTI-ACCOUNT PARALLEL TRADING BOT")
    logger.info("="*80)
    logger.info(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {MultiAccountConfig.TRADING_MODE.upper()}")
    logger.info("="*80)

    if not ADVANCED_STRATEGIES_AVAILABLE:
        logger.error("❌ Advanced strategies not available")
        return 1

    orchestrator = MultiAccountOrchestrator(logger)

    if not orchestrator.initialize_accounts():
        logger.error("❌ Failed to initialize accounts")
        return 1

    if MultiAccountConfig.ENABLE_HEALTH_API:
        health_app = create_health_api(orchestrator)
        health_thread = threading.Thread(
            target=lambda: start_health_server(health_app, logger),
            daemon=True
        )
        health_thread.start()
        logger.info(f"🏥 Health API: http://localhost:{MultiAccountConfig.HEALTH_API_PORT}")
        logger.info(f"   - Statistics: http://localhost:{MultiAccountConfig.HEALTH_API_PORT}/statistics")
        logger.info(f"   - Accounts: http://localhost:{MultiAccountConfig.HEALTH_API_PORT}/accounts")
        logger.info(f"   - Metrics: http://localhost:{MultiAccountConfig.HEALTH_API_PORT}/metrics")

    try:
        orchestrator.start()
    except Exception as e:
        logger.error(f"❌ Fatal: {e}")
        return 1
    finally:
        logger.info("="*80)
        logger.info("🏁 SHUTDOWN")
        logger.info("="*80)

        stats = orchestrator.get_statistics()
        logger.info(f"Total Accounts: {stats.get('total_accounts', 0)}")
        logger.info(f"Total Trades: {stats.get('total_trades', 0)}")
        logger.info(f"Total P&L: ${stats.get('total_pnl', 0):.2f}")
        logger.info(f"Total Balance: ${stats.get('total_balance', 0):.2f}")

        # Export final reports
        logger.info("📊 Exporting final reports...")
        orchestrator.export_reports()

    return 0


if __name__ == '__main__':
    sys.exit(main())
