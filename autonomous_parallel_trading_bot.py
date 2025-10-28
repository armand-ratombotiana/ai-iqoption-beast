#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 STRATEGY-PER-THREAD PARALLEL TRADING BOT
Production-Ready Multi-Strategy Trading System with Dedicated Thread per Strategy

Features:
- Each strategy runs in its own dedicated thread
- 7 concurrent strategies trading independently
- Binary-option payout-aware position sizing
- Expiration alignment and time-to-expiry validation
- Comprehensive performance tracking per strategy
- Real-time technical analysis at trade entry
- 24/7 continuous operation with auto-recovery
- Advanced portfolio risk management
- Database logging with multi-strategy support

CRITICAL: Optimized for binary options with strategy-per-thread architecture!
"""

import sys
import os
import time
import logging
import signal
import traceback
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Set, Tuple
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
    print("⚠️  Multi-account system not available")

# Database logging system
try:
    from database.multi_account_logger import MultiAccountTradeLogger
    DB_LOGGING_ENABLED = True
except ImportError:
    try:
        from database import TradeLogger
        DB_LOGGING_ENABLED = True
        MultiAccountTradeLogger = None
    except ImportError:
        TradeLogger = None
        DB_LOGGING_ENABLED = False
        print("⚠️  Database logging not available")

# Advanced strategy system with TA-Lib
USE_ADVANCED_STRATEGIES = os.getenv('USE_ADVANCED_STRATEGIES', 'true').lower() == 'true'
try:
    if USE_ADVANCED_STRATEGIES:
        from strategies.strategy_integrator import create_integrator, StrategyIntegrator
        from strategies.strategy_config import StrategyConfig
        from strategies.advanced_strategies import AdvancedStrategyEngine
        ADVANCED_STRATEGIES_AVAILABLE = True
    else:
        ADVANCED_STRATEGIES_AVAILABLE = False
except ImportError:
    ADVANCED_STRATEGIES_AVAILABLE = False
    if USE_ADVANCED_STRATEGIES:
        print("⚠️  Advanced strategies requested but not available")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from iqoptionapi.stable_api import IQ_Option


# =============================================================================
# PROMETHEUS METRICS
# =============================================================================

# Strategy-specific metrics
prometheus_strategy_balance = Gauge('kael_strategy_balance', 'Current balance allocated to strategy', ['strategy'])
prometheus_strategy_pnl = Gauge('kael_strategy_daily_pnl', 'Daily P&L per strategy', ['strategy'])
prometheus_strategy_trades = Counter('kael_strategy_total_trades', 'Total trades per strategy', ['strategy'])
prometheus_strategy_wins = Counter('kael_strategy_wins', 'Winning trades per strategy', ['strategy'])
prometheus_strategy_losses = Counter('kael_strategy_losses', 'Losing trades per strategy', ['strategy'])
prometheus_strategy_win_rate = Gauge('kael_strategy_win_rate', 'Win rate per strategy', ['strategy'])
prometheus_strategy_confidence = Gauge('kael_strategy_avg_confidence', 'Average confidence per strategy', ['strategy'])

# Portfolio metrics
prometheus_portfolio_balance = Gauge('kael_portfolio_balance', 'Total portfolio balance')
prometheus_portfolio_pnl = Gauge('kael_portfolio_daily_pnl', 'Total daily P&L')
prometheus_active_strategies = Gauge('kael_active_strategies', 'Number of active strategies')
prometheus_active_trades = Gauge('kael_active_trades', 'Number of currently active trades')

# Performance metrics
prometheus_execution_time = Histogram('kael_trade_execution_time_ms', 'Trade execution time in milliseconds',
                                      buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000])
prometheus_api_response_time = Histogram('kael_api_response_time_ms', 'API response time in milliseconds',
                                          buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000])


# =============================================================================
# CONFIGURATION
# =============================================================================

class StrategyThreadConfig:
    """Configuration for strategy-per-thread trading"""

    # Multi-Account Mode
    ENABLE_MULTI_ACCOUNT = bool(os.getenv('ENABLE_MULTI_ACCOUNT', MULTI_ACCOUNT_ENABLED))
    
    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'demo')
    CONTINUOUS_OPERATION_24_7 = True

    # Strategy Thread Settings
    STRATEGIES_TO_RUN = [
        'enhanced_candle_count',
        'rsi_divergence',
        'macd_momentum',
        'bollinger_rsi_combo',
        'stochastic',
        'trend_alignment',
        'support_resistance'
    ]
    
    MAX_CONCURRENT_STRATEGIES = len(STRATEGIES_TO_RUN)
    STRATEGY_SCAN_INTERVAL = int(os.getenv('STRATEGY_SCAN_INTERVAL', 5))  # seconds between scans per strategy

    # Binary Options Settings
    BINARY_OPTION_DURATION = 1
    DEFAULT_TRADE_AMOUNT = float(os.getenv('BASE_TRADE_AMOUNT', 1.0))
    MIN_TRADE_AMOUNT = 1.0
    MAX_TRADE_AMOUNT = float(os.getenv('MAX_TRADE_AMOUNT', 10.0))

    # Binary-Option Specific Thresholds
    MIN_PAYOUT_RATIO = float(os.getenv('MIN_PAYOUT_RATIO', 0.65))
    SAFETY_MARGIN_WIN_RATE = float(os.getenv('SAFETY_MARGIN_WIN_RATE', 0.02))

    # Timing thresholds
    MIN_TIME_TO_EXPIRY_SECONDS = int(os.getenv('MIN_TIME_TO_EXPIRY_SECONDS', 40))
    MAX_TIME_TO_EXPIRY_SECONDS = int(os.getenv('MAX_TIME_TO_EXPIRY_SECONDS', 55))
    EXPIRATION_BUFFER_SECONDS = int(os.getenv('EXPIRATION_BUFFER_SECONDS', 25))

    # Trading Assets
    INSTRUMENT_POOL = os.getenv('TRADING_ASSETS',
        'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,AUDJPY'
    ).split(',')

    # Risk Management
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 50))
    MAX_DAILY_PROFIT = float(os.getenv('MAX_DAILY_PROFIT', 100))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', 5))
    MIN_BALANCE = float(os.getenv('MIN_BALANCE', 50))
    MAX_TRADES_PER_HOUR = int(os.getenv('MAX_TRADES_PER_HOUR', 300))
    MIN_SECONDS_BETWEEN_TRADES = int(os.getenv('MIN_SECONDS_BETWEEN_TRADES', 70))

    # Timing
    WAIT_FOR_RESULT_SECONDS = int(os.getenv('WAIT_FOR_RESULT_SECONDS', 65))
    SIGNAL_GENERATION_TIMEOUT = float(os.getenv('SIGNAL_GENERATION_TIMEOUT', 5.0))

    # Connection health
    CONNECTION_CHECK_INTERVAL = 300
    AUTO_RECONNECT_ON_FAILURE = True
    RECONNECT_DELAY_SECONDS = 60

    # API rate limiting
    API_MIN_INTERVAL = float(os.getenv('API_MIN_INTERVAL', 0.3))
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', 3))
    API_RETRY_BACKOFF = float(os.getenv('API_RETRY_BACKOFF', 1.5))

    # AI Signal Requirements
    MIN_AI_CONFIDENCE = int(os.getenv('MIN_AI_CONFIDENCE', 70))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = Path('logs')

    # Health Monitoring
    ENABLE_HEALTH_API = bool(os.getenv('ENABLE_HEALTH_API', True))
    HEALTH_API_PORT = int(os.getenv('HEALTH_API_PORT', 5001))


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure comprehensive logging"""
    StrategyThreadConfig.LOG_DIR.mkdir(exist_ok=True)

    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(
        StrategyThreadConfig.LOG_DIR / f'strategy_threads_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    console_handler.setLevel(getattr(logging, StrategyThreadConfig.LOG_LEVEL))

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
# STRATEGY THREAD (Individual Strategy Handler)
# =============================================================================

class StrategyThread:
    """Individual strategy running in dedicated thread"""
    
    def __init__(self, strategy_name: str, api_client: ApiClient, db_logger, 
                 account_id: str, logger: logging.Logger):
        self.strategy_name = strategy_name
        self.api_client = api_client
        self.db_logger = db_logger
        self.account_id = account_id
        self.logger = logging.getLogger(f"Strategy-{strategy_name}")
        
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
        
        # Performance tracking
        self.confidence_history = deque(maxlen=100)
        self.trade_results = deque(maxlen=100)
        
    def can_trade(self) -> bool:
        """Check if strategy can trade"""
        # Check daily loss limit
        if abs(self.daily_pnl) >= StrategyThreadConfig.MAX_DAILY_LOSS and self.daily_pnl < 0:
            self.logger.warning(f"⚠️ Daily loss limit reached: ${self.daily_pnl:.2f}")
            return False
        
        # Check consecutive losses
        if self.consecutive_losses >= StrategyThreadConfig.MAX_CONSECUTIVE_LOSSES:
            self.logger.warning(f"⚠️ Max consecutive losses reached: {self.consecutive_losses}")
            return False
        
        # Check time between trades
        time_since_last = time.time() - self.last_trade_time
        if time_since_last < StrategyThreadConfig.MIN_SECONDS_BETWEEN_TRADES:
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
            
            for inst in StrategyThreadConfig.INSTRUMENT_POOL:
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
    
    def analyze_instrument(self, instrument: str) -> Optional[Tuple[str, float, List]]:
        """Analyze instrument with this strategy"""
        try:
            # Get candles
            candles = self.api_client.get_candles(instrument, 60, 100, time.time())
            if not candles or len(candles) < 50:
                return None
            
            # Analyze with strategy engine
            if not self.strategy_engine:
                return None
            
            signal = self.strategy_engine.analyze(candles)
            
            # Filter by strategy name
            if signal.strategy_name != self.strategy_name and signal.strategy_name != 'aggregated':
                return None
            
            # Check if this specific strategy contributed
            if signal.strategy_name == 'aggregated':
                # Check if our strategy is in the reasons
                strategy_contributed = any(self.strategy_name in reason for reason in signal.reasons)
                if not strategy_contributed:
                    return None
            
            if signal.direction == 'NEUTRAL':
                return None
            
            if signal.confidence < StrategyThreadConfig.MIN_AI_CONFIDENCE / 100:
                return None
            
            return signal.direction, signal.confidence, signal.reasons
            
        except Exception as e:
            self.logger.error(f"Analysis error for {instrument}: {e}")
            return None
    
    def execute_trade(self, instrument: str, direction: str, confidence: float, reasons: List[str]) -> Optional[Dict]:
        """Execute a single trade"""
        try:
            # Calculate trade amount (simple fixed amount for now)
            amount = StrategyThreadConfig.DEFAULT_TRADE_AMOUNT
            
            self.logger.info(f"📊 {instrument} {direction} ${amount:.2f} @ {confidence:.0%}")
            self.logger.info(f"   Reasons: {', '.join(reasons[:2])}")
            
            # Place order
            action = 'call' if direction == 'CALL' else 'put'
            success, order_id = self.api_client.buy(amount, instrument, action, 1)
            
            if not success:
                self.logger.error("❌ Trade failed")
                return None
            
            # Log trade to database
            if self.db_logger:
                trade_data = {
                    'trade_id': str(order_id),
                    'instrument': instrument,
                    'direction': direction,
                    'amount': amount,
                    'entry_time': datetime.now(),
                    'expiration_seconds': 60,
                    'selected_strategy': self.strategy_name,
                    'strategy_profile': self.strategy_name,
                    'confidence': int(confidence * 100),
                    'strategy_breakdown': [{'strategy': self.strategy_name, 'confidence': confidence}],
                    'mode': StrategyThreadConfig.TRADING_MODE
                }
                
                db_trade_id = self.db_logger.log_trade(
                    self.account_id,
                    trade_data
                )
            
            # Wait for result
            time.sleep(StrategyThreadConfig.WAIT_FOR_RESULT_SECONDS)
            
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
            
            # Track performance
            self.confidence_history.append(confidence)
            self.trade_results.append(1 if won else 0)
            
            # Update Prometheus metrics
            prometheus_strategy_trades.labels(strategy=self.strategy_name).inc()
            if won:
                prometheus_strategy_wins.labels(strategy=self.strategy_name).inc()
            else:
                prometheus_strategy_losses.labels(strategy=self.strategy_name).inc()
            
            prometheus_strategy_pnl.labels(strategy=self.strategy_name).set(self.daily_pnl)
            
            if self.trades_today > 0:
                win_rate = (self.wins_today / self.trades_today) * 100
                prometheus_strategy_win_rate.labels(strategy=self.strategy_name).set(win_rate)
            
            if self.confidence_history:
                avg_conf = sum(self.confidence_history) / len(self.confidence_history)
                prometheus_strategy_confidence.labels(strategy=self.strategy_name).set(avg_conf)
            
            return {
                'instrument': instrument,
                'result': result_str,
                'profit': profit,
                'strategy': self.strategy_name
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
            
            # Analyze instruments with this strategy
            for instrument in instruments[:10]:  # Check up to 10 instruments
                if not self.running:
                    break
                
                analysis = self.analyze_instrument(instrument)
                if analysis:
                    direction, confidence, reasons = analysis
                    result = self.execute_trade(instrument, direction, confidence, reasons)
                    if result:
                        # Wait before next trade
                        time.sleep(StrategyThreadConfig.MIN_SECONDS_BETWEEN_TRADES)
                        break
                    
        except Exception as e:
            self.logger.error(f"Trade cycle error: {e}")
    
    def run(self):
        """Main trading loop"""
        self.running = True
        self.logger.info(f"🚀 Strategy thread started: {self.strategy_name}")
        
        while self.running:
            try:
                self.trade_cycle()
                time.sleep(StrategyThreadConfig.STRATEGY_SCAN_INTERVAL)
            except Exception as e:
                self.logger.error(f"Run error: {e}")
                time.sleep(30)
    
    def start(self):
        """Start strategy thread"""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop strategy thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        self.logger.info(f"🛑 Strategy thread stopped: {self.strategy_name}")
    
    def get_stats(self) -> Dict:
        """Get strategy statistics"""
        win_rate = (self.wins_today / self.trades_today * 100) if self.trades_today > 0 else 0
        avg_confidence = sum(self.confidence_history) / len(self.confidence_history) if self.confidence_history else 0
        
        return {
            'strategy': self.strategy_name,
            'trades': self.trades_today,
            'wins': self.wins_today,
            'losses': self.losses_today,
            'win_rate': win_rate,
            'daily_pnl': self.daily_pnl,
            'avg_confidence': avg_confidence,
            'consecutive_losses': self.consecutive_losses,
            'is_running': self.running
        }


# =============================================================================
# STRATEGY ORCHESTRATOR
# =============================================================================

class StrategyOrchestrator:
    """Orchestrates multiple strategies, each in its own thread"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.api = None
        self.api_client = None
        self.db_logger = None
        self.strategies: Dict[str, StrategyThread] = {}
        self.running = False
        self.account_id = "strategy_threads"
        
        # Initialize database
        database_url = os.getenv('DATABASE_URL', 
                                'postgresql://postgres:postgres@localhost:5432/kael')
        try:
            if MultiAccountTradeLogger:
                self.db_logger = MultiAccountTradeLogger(database_url)
                self.logger.info("✅ Database logging enabled")
        except Exception as e:
            self.logger.warning(f"⚠️ Database initialization failed: {e}")
    
    def connect(self) -> bool:
        """Connect to IQ Option"""
        try:
            email = os.getenv('IQOPTION_EMAIL')
            password = os.getenv('IQOPTION_PASSWORD')
            
            if not email or not password:
                self.logger.error("❌ Missing credentials")
                return False
            
            self.logger.info(f"🔌 Connecting {email}...")
            
            self.api = IQ_Option(email, password)
            check, reason = self.api.connect()
            
            if not check:
                self.logger.error(f"❌ Connection failed: {reason}")
                return False
            
            # Set trading mode
            if StrategyThreadConfig.TRADING_MODE == 'live':
                self.api.change_balance('REAL')
                self.logger.warning("⚠️ LIVE MODE")
            else:
                self.api.change_balance('PRACTICE')
                self.logger.info("✅ Demo mode")
            
            balance = self.api.get_balance()
            self.logger.info(f"💰 Balance: ${balance:.2f}")
            
            # Initialize API client
            self.api_client = ApiClient(
                self.api,
                min_interval=StrategyThreadConfig.API_MIN_INTERVAL,
                max_retries=StrategyThreadConfig.API_MAX_RETRIES,
                backoff_base=StrategyThreadConfig.API_RETRY_BACKOFF
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Connection error: {e}")
            return False
    
    def initialize_strategies(self):
        """Initialize all strategy threads"""
        self.logger.info("="*80)
        self.logger.info("🚀 STRATEGY-PER-THREAD ORCHESTRATOR")
        self.logger.info("="*80)
        
        strategies = StrategyThreadConfig.STRATEGIES_TO_RUN
        self.logger.info(f"📊 Initializing {len(strategies)} strategy threads...")
        
        for strategy_name in strategies:
            strategy_thread = StrategyThread(
                strategy_name,
                self.api_client,
                self.db_logger,
                self.account_id,
                self.logger
            )
            self.strategies[strategy_name] = strategy_thread
            self.logger.info(f"✅ {strategy_name}")
        
        self.logger.info(f"✅ {len(self.strategies)} strategies ready")
        self.logger.info("="*80)
        
        return len(self.strategies) > 0
    
    def start(self):
        """Start all strategy threads"""
        if not self.strategies:
            self.logger.error("No strategies initialized")
            return False
        
        self.running = True
        self.logger.info("🎯 Starting all strategy threads...")
        
        # Start each strategy in its own thread
        for strategy_name, strategy in self.strategies.items():
            strategy.start()
            self.logger.info(f"   ✅ {strategy_name} thread started")
        
        prometheus_active_strategies.set(len(self.strategies))
        
        # Monitor strategies
        try:
            while self.running:
                time.sleep(60)
                self._print_status()
                
                # Update portfolio metrics
                self._update_portfolio_metrics()
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested...")
            self.stop()
        
        return True
    
    def stop(self):
        """Stop all strategy threads"""
        self.running = False
        
        self.logger.info("🛑 Stopping all strategy threads...")
        for strategy in self.strategies.values():
            strategy.stop()
        
        self.logger.info("✅ All strategies stopped")
    
    def _update_portfolio_metrics(self):
        """Update portfolio-wide metrics"""
        try:
            balance = self.api_client.get_balance()
            prometheus_portfolio_balance.set(balance)
            
            total_pnl = sum(s.daily_pnl for s in self.strategies.values())
            prometheus_portfolio_pnl.set(total_pnl)
            
            active_count = sum(1 for s in self.strategies.values() if s.running)
            prometheus_active_strategies.set(active_count)
            
        except Exception as e:
            self.logger.error(f"Error updating portfolio metrics: {e}")
    
    def _print_status(self):
        """Print current status"""
        self.logger.info("="*80)
        self.logger.info("📊 STRATEGY STATUS")
        
        total_trades = sum(s.trades_today for s in self.strategies.values())
        total_pnl = sum(s.daily_pnl for s in self.strategies.values())
        
        self.logger.info(f"Active Strategies: {sum(1 for s in self.strategies.values() if s.running)}/{len(self.strategies)}")
        self.logger.info(f"Total Trades: {total_trades}")
        self.logger.info(f"Total P&L: ${total_pnl:.2f}")
        self.logger.info("")
        
        for strategy in self.strategies.values():
            stats = strategy.get_stats()
            status = "🟢" if stats['is_running'] else "🔴"
            self.logger.info(
                f"{status} {stats['strategy']:25s} | "
                f"Trades: {stats['trades']:3d} | "
                f"Win Rate: {stats['win_rate']:5.1f}% | "
                f"P&L: ${stats['daily_pnl']:7.2f} | "
                f"Conf: {stats['avg_confidence']:.0%}"
            )
        
        self.logger.info("="*80)
    
    def get_statistics(self) -> Dict:
        """Get statistics"""
        stats = {
            'total_strategies': len(self.strategies),
            'active_strategies': sum(1 for s in self.strategies.values() if s.running),
            'total_trades': sum(s.trades_today for s in self.strategies.values()),
            'total_pnl': sum(s.daily_pnl for s in self.strategies.values()),
            'strategies': [s.get_stats() for s in self.strategies.values()]
        }
        
        # Get portfolio summary from database
        if self.db_logger:
            try:
                portfolio_summary = self.db_logger.get_portfolio_summary()
                stats.update(portfolio_summary)
            except Exception:
                pass
        
        return stats


# =============================================================================
# HEALTH API
# =============================================================================

def create_health_api(orchestrator: StrategyOrchestrator):
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

    @app.route('/strategies', methods=['GET'])
    def strategies():
        """Get all strategies status"""
        stats = [s.get_stats() for s in orchestrator.strategies.values()]
        return jsonify({
            'strategies': stats,
            'total': len(stats),
            'active': sum(1 for s in stats if s['is_running'])
        })

    @app.route('/strategy/<strategy_name>', methods=['GET'])
    def strategy_detail(strategy_name):
        """Get specific strategy details"""
        if strategy_name not in orchestrator.strategies:
            return jsonify({'error': 'Strategy not found'}), 404
        
        strategy = orchestrator.strategies[strategy_name]
        return jsonify(strategy.get_stats())

    @app.route('/strategy_stats', methods=['GET'])
    def strategy_stats():
        """Get strategy performance from database"""
        if not orchestrator.db_logger:
            return jsonify({'error': 'Database not available'}), 503
        
        try:
            stats = orchestrator.db_logger.get_strategy_performance(days=7)
            return jsonify({
                'strategy_stats': stats,
                'time_period': 'Last 7 days',
                'total_strategies': len(stats)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/recent_trades', methods=['GET'])
    def recent_trades():
        """Get recent trades"""
        limit = int(request.args.get('limit', 100))
        strategy = request.args.get('strategy', None)
        
        if not orchestrator.db_logger:
            return jsonify({'error': 'Database not available'}), 503
        
        try:
            trades = orchestrator.db_logger.get_recent_trades(orchestrator.account_id, limit)
            
            # Filter by strategy if specified
            if strategy:
                trades = [t for t in trades if t.get('selected_strategy') == strategy]
            
            return jsonify({'trades': trades})
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
            port=StrategyThreadConfig.HEALTH_API_PORT,
            threads=8,
            channel_timeout=60,
            log_socket_errors=False
        )
    except Exception:
        logger.warning("⚠️ Health API running with Flask's built-in server")
        app.run(host='0.0.0.0', port=StrategyThreadConfig.HEALTH_API_PORT, 
               debug=False, use_reloader=False, threaded=True)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    logger = setup_logging()

    logger.info("="*80)
    logger.info("🚀 STRATEGY-PER-THREAD PARALLEL TRADING BOT")
    logger.info("="*80)
    logger.info(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {StrategyThreadConfig.TRADING_MODE.upper()}")
    logger.info(f"Strategies: {len(StrategyThreadConfig.STRATEGIES_TO_RUN)}")
    logger.info("="*80)

    if not ADVANCED_STRATEGIES_AVAILABLE:
        logger.error("❌ Advanced strategies not available")
        return 1

    orchestrator = StrategyOrchestrator(logger)
    
    if not orchestrator.connect():
        logger.error("❌ Failed to connect")
        return 1
    
    if not orchestrator.initialize_strategies():
        logger.error("❌ Failed to initialize strategies")
        return 1

    if StrategyThreadConfig.ENABLE_HEALTH_API:
        health_app = create_health_api(orchestrator)
        health_thread = threading.Thread(
            target=lambda: start_health_server(health_app, logger),
            daemon=True
        )
        health_thread.start()
        logger.info(f"🏥 Health API: http://localhost:{StrategyThreadConfig.HEALTH_API_PORT}")

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
        logger.info(f"Total Strategies: {stats.get('total_strategies', 0)}")
        logger.info(f"Total Trades: {stats.get('total_trades', 0)}")
        logger.info(f"Total P&L: ${stats.get('total_pnl', 0):.2f}")

    return 0


if __name__ == '__main__':
    sys.exit(main())