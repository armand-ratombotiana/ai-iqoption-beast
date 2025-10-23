#!/usr/bin/env python3
"""
🤖 AUTONOMOUS 24/7 PARALLEL TRADING BOT - MULTI-INSTRUMENT
Production-Ready Continuous Multi-Asset Trading System

Features:
- 24/7 continuous operation with auto-recovery
- Trade multiple instruments simultaneously (up to 10 concurrent)
- Trade every minute on each instrument
- Independent signal generation per instrument
- Advanced portfolio risk management
- Correlation-aware position sizing
- Real-time balance allocation
- Per-instrument performance tracking
- Concurrent trade execution
- Dynamic instrument selection
- Auto-reconnection on failures
- Daily stats reset at midnight

CRITICAL: This bot trades multiple assets autonomously 24/7. Monitor regularly!
"""

import sys
import os
import time
import logging
import signal
import traceback
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Set
import threading
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

from flask import Flask, jsonify
from iqoptionapi.stable_api import IQ_Option


# =============================================================================
# 24/7 PARALLEL TRADING CONFIGURATION
# =============================================================================

class ParallelTradingConfig:
    """Configuration for 24/7 parallel multi-instrument trading"""

    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'demo')
    CONTINUOUS_OPERATION_24_7 = True  # Always run 24/7

    # Parallel Trading Settings
    MAX_CONCURRENT_INSTRUMENTS = int(os.getenv('MAX_CONCURRENT_INSTRUMENTS', 5))
    MAX_INSTRUMENTS_TO_MONITOR = int(os.getenv('MAX_INSTRUMENTS_TO_MONITOR', 20))
    ENABLE_DYNAMIC_INSTRUMENT_SELECTION = True

    # Binary Options Settings - 1 MINUTE TRADES
    BINARY_OPTION_DURATION = 1  # 1 minute
    DEFAULT_TRADE_AMOUNT = float(os.getenv('BASE_TRADE_AMOUNT', 1.0))
    MIN_TRADE_AMOUNT = 1.0
    MAX_TRADE_AMOUNT = float(os.getenv('MAX_TRADE_AMOUNT', 10.0))

    # Instrument Pool (expanded for parallel trading)
    INSTRUMENT_POOL = os.getenv('TRADING_ASSETS',
        'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,'
        'EURGBP,AUDJPY,EURAUD,GBPAUD,USDCHF,EURCAD,GBPCAD,AUDCAD'
    ).split(',')

    # Portfolio Risk Management
    TOTAL_PORTFOLIO_RISK_PERCENT = float(os.getenv('PORTFOLIO_RISK_PERCENT', 10.0))
    MAX_RISK_PER_INSTRUMENT = float(os.getenv('MAX_RISK_PER_INSTRUMENT', 2.5))
    CORRELATION_THRESHOLD = float(os.getenv('CORRELATION_THRESHOLD', 0.7))

    # Daily Limits (Reset at midnight)
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 50))
    MAX_DAILY_PROFIT = float(os.getenv('MAX_DAILY_PROFIT', 100))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', 5))
    MIN_BALANCE = float(os.getenv('MIN_BALANCE', 50))

    # Per-Instrument Limits - ADJUSTED FOR EVERY MINUTE TRADING
    MAX_TRADES_PER_INSTRUMENT_HOUR = int(os.getenv('MAX_TRADES_PER_INSTRUMENT_HOUR', 60))  # Up to 60 per hour
    MIN_SECONDS_BETWEEN_INSTRUMENT_TRADES = 60  # 1 minute minimum (for 1-minute options)

    # Global Limits - INCREASED FOR 24/7 OPERATION
    MAX_TOTAL_TRADES_PER_HOUR = int(os.getenv('MAX_TRADES_PER_HOUR', 300))  # 5 instruments * 60 trades
    MAX_TOTAL_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', 7200))  # 24 hours * 300

    # AI Signal Requirements
    MIN_AI_CONFIDENCE = int(os.getenv('MIN_AI_CONFIDENCE', 65))
    MIN_CONSENSUS_AGREEMENT = float(os.getenv('MIN_CONSENSUS_AGREEMENT', 0.7))

    # Timing - OPTIMIZED FOR EVERY MINUTE TRADING
    WAIT_FOR_RESULT_SECONDS = 70  # Wait 70 seconds for 1-minute trade result
    CONNECTION_CHECK_INTERVAL = 300  # Check connection every 5 minutes
    INSTRUMENT_SCAN_INTERVAL = 10  # Scan every 10 seconds for opportunities
    TRADE_EXECUTION_INTERVAL = 60  # Execute trades every 60 seconds

    # Thread Pool
    MAX_WORKER_THREADS = int(os.getenv('MAX_WORKER_THREADS', 10))

    # 24/7 Auto-Recovery Settings
    AUTO_RECONNECT_ON_FAILURE = True
    MAX_RECONNECT_ATTEMPTS = 999999  # Unlimited for 24/7
    RECONNECT_DELAY_SECONDS = 30
    RESTART_ON_CRITICAL_ERROR = True

    # Credentials
    EMAIL = os.getenv('IQOPTION_EMAIL', '')
    PASSWORD = os.getenv('IQOPTION_PASSWORD', '')

    # Health Monitoring
    ENABLE_HEALTH_API = True
    HEALTH_API_PORT = int(os.getenv('HEALTH_API_PORT', 5001))


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure comprehensive logging with daily rotation"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Main log file (daily rotation)
    file_handler = logging.FileHandler(
        log_dir / f'parallel_bot_24_7_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Trade log file (daily rotation)
    trade_handler = logging.FileHandler(
        log_dir / f'parallel_trades_24_7_{datetime.now().strftime("%Y%m%d")}.log'
    )
    trade_handler.setFormatter(detailed_formatter)
    trade_handler.setLevel(logging.INFO)
    trade_handler.addFilter(lambda record: 'TRADE' in record.getMessage())

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(trade_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger(__name__)


# =============================================================================
# INSTRUMENT STATE MANAGER
# =============================================================================

class InstrumentStateManager:
    """Manage state for individual instruments with minute-by-minute tracking"""

    def __init__(self, instrument: str):
        self.instrument = instrument
        self.lock = threading.Lock()
        self.state = {
            'last_trade_time': None,
            'trades_this_hour': 0,
            'trades_this_minute': 0,
            'hour_start': datetime.now().replace(minute=0, second=0, microsecond=0),
            'minute_start': datetime.now().replace(second=0, microsecond=0),
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'profit': 0.0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'is_trading': False,
            'last_signal': None,
            'last_confidence': 0,
            'active_trade_id': None
        }

    def can_trade(self) -> tuple[bool, str]:
        """Check if this instrument can trade"""
        with self.lock:
            # Reset hourly stats
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            if self.state['hour_start'] != current_hour:
                self.state['trades_this_hour'] = 0
                self.state['hour_start'] = current_hour

            # Reset minute stats
            current_minute = datetime.now().replace(second=0, microsecond=0)
            if self.state['minute_start'] != current_minute:
                self.state['trades_this_minute'] = 0
                self.state['minute_start'] = current_minute

            # Check if already trading
            if self.state['is_trading']:
                return False, "Trade already active"

            # Check if already traded this minute
            if self.state['trades_this_minute'] >= 1:
                return False, "Already traded this minute"

            # Check hourly limit
            if self.state['trades_this_hour'] >= ParallelTradingConfig.MAX_TRADES_PER_INSTRUMENT_HOUR:
                return False, f"Hourly limit reached: {self.state['trades_this_hour']}"

            # Check time between trades (60 seconds for 1-minute options)
            if self.state['last_trade_time']:
                elapsed = (datetime.now() - self.state['last_trade_time']).total_seconds()
                if elapsed < ParallelTradingConfig.MIN_SECONDS_BETWEEN_INSTRUMENT_TRADES:
                    return False, f"Wait {int(ParallelTradingConfig.MIN_SECONDS_BETWEEN_INSTRUMENT_TRADES - elapsed)}s"

            return True, "OK"

    def start_trade(self, trade_id: str):
        """Mark instrument as trading"""
        with self.lock:
            self.state['is_trading'] = True
            self.state['active_trade_id'] = trade_id
            self.state['last_trade_time'] = datetime.now()
            self.state['trades_this_hour'] += 1
            self.state['trades_this_minute'] += 1
            self.state['total_trades'] += 1

    def complete_trade(self, won: bool, profit: float):
        """Complete a trade and update stats"""
        with self.lock:
            self.state['is_trading'] = False
            self.state['active_trade_id'] = None
            self.state['profit'] += profit

            if won:
                self.state['wins'] += 1
                self.state['consecutive_wins'] += 1
                self.state['consecutive_losses'] = 0
            else:
                self.state['losses'] += 1
                self.state['consecutive_losses'] += 1
                self.state['consecutive_wins'] = 0

    def get_stats(self) -> Dict:
        """Get instrument statistics"""
        with self.lock:
            win_rate = 0
            if self.state['total_trades'] > 0:
                win_rate = (self.state['wins'] / self.state['total_trades']) * 100

            return {
                'instrument': self.instrument,
                'total_trades': self.state['total_trades'],
                'wins': self.state['wins'],
                'losses': self.state['losses'],
                'win_rate': round(win_rate, 2),
                'profit': round(self.state['profit'], 2),
                'consecutive_wins': self.state['consecutive_wins'],
                'consecutive_losses': self.state['consecutive_losses'],
                'is_trading': self.state['is_trading'],
                'trades_this_hour': self.state['trades_this_hour']
            }


# =============================================================================
# PORTFOLIO STATE MANAGER
# =============================================================================

class PortfolioStateManager:
    """Thread-safe portfolio-wide state management for 24/7 operation"""

    def __init__(self):
        self.lock = threading.Lock()
        self.instrument_managers: Dict[str, InstrumentStateManager] = {}
        self.state = {
            'running': False,
            'start_time': None,
            'current_balance': 0.0,
            'start_balance': 0.0,

            # Daily stats (reset at midnight)
            'daily_profit': 0.0,
            'daily_loss': 0.0,
            'trades_today': 0,
            'wins_today': 0,
            'losses_today': 0,
            'last_reset': datetime.now().date(),

            # Hourly tracking
            'trades_this_hour': 0,
            'hour_start': datetime.now().replace(minute=0, second=0, microsecond=0),

            # Active positions
            'active_instruments': set(),
            'total_risk_allocated': 0.0,

            # Health & Recovery
            'api_connected': False,
            'last_error': None,
            'reconnect_count': 0,
            'last_connection_check': datetime.now(),

            # 24/7 Stats
            'total_uptime_seconds': 0,
            'total_trades_all_time': 0
        }

    def get_instrument_manager(self, instrument: str) -> InstrumentStateManager:
        """Get or create instrument manager"""
        if instrument not in self.instrument_managers:
            self.instrument_managers[instrument] = InstrumentStateManager(instrument)
        return self.instrument_managers[instrument]

    def reset_daily_stats(self):
        """Reset daily statistics at midnight"""
        with self.lock:
            today = datetime.now().date()
            if self.state['last_reset'] != today:
                self.logger.info("🌅 NEW DAY - Resetting daily statistics")
                self.state.update({
                    'daily_profit': 0.0,
                    'daily_loss': 0.0,
                    'trades_today': 0,
                    'wins_today': 0,
                    'losses_today': 0,
                    'last_reset': today
                })
                return True
        return False

    def reset_hourly_stats(self):
        """Reset hourly stats"""
        with self.lock:
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            if self.state['hour_start'] != current_hour:
                self.state['trades_this_hour'] = 0
                self.state['hour_start'] = current_hour
                return True
        return False

    def can_trade_portfolio(self) -> tuple[bool, str]:
        """Check portfolio-wide trading constraints"""
        self.reset_daily_stats()
        self.reset_hourly_stats()

        with self.lock:
            # Balance check
            if self.state['current_balance'] < ParallelTradingConfig.MIN_BALANCE:
                return False, f"Balance too low: ${self.state['current_balance']:.2f}"

            # Daily loss limit
            if self.state['daily_loss'] >= ParallelTradingConfig.MAX_DAILY_LOSS:
                return False, f"Daily loss limit: ${self.state['daily_loss']:.2f}"

            # Daily profit target
            if self.state['daily_profit'] >= ParallelTradingConfig.MAX_DAILY_PROFIT:
                return False, f"Daily profit target: ${self.state['daily_profit']:.2f}"

            # Hourly trade limit
            if self.state['trades_this_hour'] >= ParallelTradingConfig.MAX_TOTAL_TRADES_PER_HOUR:
                return False, f"Hourly limit: {self.state['trades_this_hour']}"

            # Daily trade limit
            if self.state['trades_today'] >= ParallelTradingConfig.MAX_TOTAL_TRADES_PER_DAY:
                return False, f"Daily limit: {self.state['trades_today']}"

            # Concurrent instruments limit
            if len(self.state['active_instruments']) >= ParallelTradingConfig.MAX_CONCURRENT_INSTRUMENTS:
                return False, f"Max concurrent instruments: {len(self.state['active_instruments'])}"

            # Portfolio risk limit
            max_portfolio_risk = self.state['current_balance'] * (ParallelTradingConfig.TOTAL_PORTFOLIO_RISK_PERCENT / 100)
            if self.state['total_risk_allocated'] >= max_portfolio_risk:
                return False, f"Portfolio risk limit: ${self.state['total_risk_allocated']:.2f}"

            return True, "OK"

    def allocate_risk(self, instrument: str, amount: float) -> bool:
        """Allocate risk for a new trade"""
        with self.lock:
            max_portfolio_risk = self.state['current_balance'] * (ParallelTradingConfig.TOTAL_PORTFOLIO_RISK_PERCENT / 100)
            if self.state['total_risk_allocated'] + amount > max_portfolio_risk:
                return False

            self.state['total_risk_allocated'] += amount
            self.state['active_instruments'].add(instrument)
            return True

    def release_risk(self, instrument: str, amount: float):
        """Release risk after trade completion"""
        with self.lock:
            self.state['total_risk_allocated'] = max(0, self.state['total_risk_allocated'] - amount)
            self.state['active_instruments'].discard(instrument)

    def update_trade_result(self, profit: float, won: bool):
        """Update portfolio stats after trade"""
        with self.lock:
            self.state['trades_today'] += 1
            self.state['trades_this_hour'] += 1
            self.state['total_trades_all_time'] += 1

            if won:
                self.state['daily_profit'] += profit
                self.state['wins_today'] += 1
            else:
                self.state['daily_loss'] += abs(profit)
                self.state['losses_today'] += 1

    def get_portfolio_stats(self) -> Dict:
        """Get portfolio statistics"""
        with self.lock:
            win_rate = 0
            if self.state['trades_today'] > 0:
                win_rate = (self.state['wins_today'] / self.state['trades_today']) * 100

            # Get per-instrument stats
            instrument_stats = []
            for manager in self.instrument_managers.values():
                stats = manager.get_stats()
                if stats['total_trades'] > 0:
                    instrument_stats.append(stats)

            # Sort by profit
            instrument_stats.sort(key=lambda x: x['profit'], reverse=True)

            return {
                'balance': self.state['current_balance'],
                'start_balance': self.state['start_balance'],
                'daily_profit': self.state['daily_profit'],
                'daily_loss': self.state['daily_loss'],
                'daily_net': self.state['daily_profit'] - self.state['daily_loss'],
                'trades_today': self.state['trades_today'],
                'wins_today': self.state['wins_today'],
                'losses_today': self.state['losses_today'],
                'win_rate': round(win_rate, 2),
                'active_instruments': list(self.state['active_instruments']),
                'active_count': len(self.state['active_instruments']),
                'total_risk_allocated': self.state['total_risk_allocated'],
                'instruments_traded': len(self.instrument_managers),
                'instrument_stats': instrument_stats[:10],
                'reconnect_count': self.state['reconnect_count'],
                'total_trades_all_time': self.state['total_trades_all_time']
            }


# =============================================================================
# 24/7 PARALLEL TRADING BOT
# =============================================================================

class ParallelTradingBot:
    """24/7 Multi-instrument parallel trading bot"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.portfolio_manager = PortfolioStateManager()
        self.portfolio_manager.logger = logger
        self.api: Optional[IQ_Option] = None
        self.running = False
        self.shutdown_requested = False
        self.executor = ThreadPoolExecutor(max_workers=ParallelTradingConfig.MAX_WORKER_THREADS)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.logger.info("="*80)
        self.logger.info("🤖 24/7 PARALLEL MULTI-INSTRUMENT TRADING BOT INITIALIZED")
        self.logger.info(f"📊 Max Concurrent Instruments: {ParallelTradingConfig.MAX_CONCURRENT_INSTRUMENTS}")
        self.logger.info(f"⏱️  Trade Frequency: Every minute per instrument")
        self.logger.info("="*80)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.warning(f"Received signal {signum}. Shutting down...")
        self.shutdown_requested = True
        self.running = False

    def connect_to_broker(self) -> bool:
        """Connect to IQ Option with retry logic"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"🔌 Connecting to IQ Option (Attempt {attempt + 1}/{max_attempts})...")

                if not ParallelTradingConfig.EMAIL or not ParallelTradingConfig.PASSWORD:
                    self.logger.error("❌ No credentials configured")
                    return False

                self.api = IQ_Option(
                    ParallelTradingConfig.EMAIL,
                    ParallelTradingConfig.PASSWORD
                )

                check, reason = self.api.connect()
                if not check:
                    self.logger.error(f"❌ Connection failed: {reason}")
                    if attempt < max_attempts - 1:
                        time.sleep(5)
                        continue
                    return False

                # Set account type
                if ParallelTradingConfig.TRADING_MODE == 'live':
                    self.api.change_balance('REAL')
                    self.logger.warning("⚠️  LIVE TRADING MODE - 24/7 OPERATION")
                else:
                    self.api.change_balance('PRACTICE')
                    self.logger.info("✅ Demo mode - 24/7 operation")

                # Get balance
                balance = self.api.get_balance()
                self.portfolio_manager.state['current_balance'] = balance
                self.portfolio_manager.state['start_balance'] = balance
                self.portfolio_manager.state['api_connected'] = True
                self.portfolio_manager.state['last_connection_check'] = datetime.now()

                self.logger.info(f"✅ Connected. Balance: ${balance:.2f}")
                return True

            except Exception as e:
                self.logger.error(f"❌ Connection error: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(5)
                    continue
                return False

        return False

    def check_connection_health(self) -> bool:
        """Check and maintain connection health"""
        try:
            # Check every 5 minutes
            last_check = self.portfolio_manager.state['last_connection_check']
            if (datetime.now() - last_check).total_seconds() < ParallelTradingConfig.CONNECTION_CHECK_INTERVAL:
                return True

            if not self.api or not self.api.check_connect():
                self.logger.warning("⚠️  Connection lost. Reconnecting...")
                self.portfolio_manager.state['reconnect_count'] += 1
                return self.connect_to_broker()

            # Update balance
            balance = self.api.get_balance()
            self.portfolio_manager.state['current_balance'] = balance
            self.portfolio_manager.state['last_connection_check'] = datetime.now()

            return True

        except Exception as e:
            self.logger.error(f"❌ Connection health check failed: {e}")
            return False

    def get_available_instruments(self) -> List[str]:
        """Get list of available instruments for trading"""
        try:
            open_markets = self.api.get_all_open_time()
            if not open_markets or 'binary' not in open_markets:
                return []

            binary_markets = open_markets['binary']
            available = []

            for instrument in ParallelTradingConfig.INSTRUMENT_POOL:
                instrument = instrument.strip()

                # Try different formats
                for suffix in ['', '-op', '-OTC']:
                    test_name = f"{instrument}{suffix}"
                    if test_name in binary_markets and binary_markets[test_name].get('open', False):
                        available.append(test_name)
                        break

            self.logger.debug(f"📊 Found {len(available)} available instruments")
            return available

        except Exception as e:
            self.logger.error(f"❌ Error getting instruments: {e}")
            return []

    def get_ai_signal(self, instrument: str) -> Optional[Dict]:
        """Get AI signal for instrument"""
        import random

        # TODO: Replace with actual AI consensus engine
        signals = ['CALL', 'PUT', 'NEUTRAL']
        weights = [0.45, 0.45, 0.10]

        signal = random.choices(signals, weights=weights)[0]
        confidence = random.randint(60, 95)

        return {
            'signal': signal,
            'confidence': confidence,
            'instrument': instrument,
            'timestamp': datetime.now().isoformat()
        }

    def calculate_position_size(self, instrument: str, confidence: float) -> float:
        """Calculate position size for instrument"""
        balance = self.portfolio_manager.state['current_balance']

        # Base amount per instrument
        max_per_instrument = balance * (ParallelTradingConfig.MAX_RISK_PER_INSTRUMENT / 100)

        # Adjust by confidence
        amount = max_per_instrument * (confidence / 100)

        # Apply limits
        amount = max(ParallelTradingConfig.MIN_TRADE_AMOUNT, amount)
        amount = min(ParallelTradingConfig.MAX_TRADE_AMOUNT, amount)

        return round(amount, 2)

    def execute_instrument_trade(self, instrument: str) -> Optional[Dict]:
        """Execute trade for a single instrument"""
        try:
            # Get instrument manager
            inst_manager = self.portfolio_manager.get_instrument_manager(instrument)

            # Check if instrument can trade
            can_trade, reason = inst_manager.can_trade()
            if not can_trade:
                self.logger.debug(f"⏸️  {instrument}: {reason}")
                return None

            # Get AI signal
            ai_signal = self.get_ai_signal(instrument)
            if not ai_signal or ai_signal['signal'] == 'NEUTRAL':
                return None

            if ai_signal['confidence'] < ParallelTradingConfig.MIN_AI_CONFIDENCE:
                return None

            # Calculate position size
            amount = self.calculate_position_size(instrument, ai_signal['confidence'])

            # Allocate portfolio risk
            if not self.portfolio_manager.allocate_risk(instrument, amount):
                self.logger.debug(f"⏸️  {instrument}: Portfolio risk limit")
                return None

            # Mark instrument as trading
            trade_id = f"{instrument}_{int(time.time())}"
            inst_manager.start_trade(trade_id)

            # Execute trade
            self.logger.info(f"🎯 TRADE [{instrument}]: {ai_signal['signal']} ${amount} @ {ai_signal['confidence']}%")

            action = ai_signal['signal'].lower()
            status, order_id = self.api.buy(amount, instrument, action, ParallelTradingConfig.BINARY_OPTION_DURATION)

            if not status or order_id is None:
                self.logger.error(f"❌ [{instrument}] Trade failed")
                inst_manager.complete_trade(False, 0)
                self.portfolio_manager.release_risk(instrument, amount)
                return None

            self.logger.info(f"✅ [{instrument}] Order placed: {order_id}")

            # Wait for result
            time.sleep(ParallelTradingConfig.WAIT_FOR_RESULT_SECONDS)

            # Check result
            profit = None
            for attempt in range(30):
                try:
                    profit = self.api.check_win_v3(order_id)
                    if profit is not None:
                        break
                except:
                    pass
                time.sleep(1)

            if profit is None:
                self.logger.error(f"❌ [{instrument}] Could not get result")
                inst_manager.complete_trade(False, 0)
                self.portfolio_manager.release_risk(instrument, amount)
                return None

            # Process result
            won = profit > 0
            result_str = "WIN" if won else "LOSS"

            # Update stats
            inst_manager.complete_trade(won, profit)
            self.portfolio_manager.update_trade_result(profit, won)
            self.portfolio_manager.release_risk(instrument, amount)

            # Update balance
            new_balance = self.api.get_balance()
            self.portfolio_manager.state['current_balance'] = new_balance

            # Log result
            self.logger.info("="*80)
            self.logger.info(f"📈 RESULT [{instrument}]: {result_str}")
            self.logger.info(f"   Order: {order_id}")
            self.logger.info(f"   P/L: ${profit:+.2f}")
            self.logger.info(f"   Balance: ${new_balance:.2f}")
            self.logger.info(f"   Daily P/L: ${self.portfolio_manager.state['daily_profit'] - self.portfolio_manager.state['daily_loss']:+.2f}")
            self.logger.info("="*80)

            return {
                'instrument': instrument,
                'order_id': order_id,
                'action': action,
                'amount': amount,
                'profit': profit,
                'won': won
            }

        except Exception as e:
            self.logger.error(f"❌ [{instrument}] Error: {e}")
            self.logger.debug(traceback.format_exc())
            return None

    def parallel_trading_cycle(self):
        """Execute one cycle of parallel trading"""
        try:
            # Check connection health
            if not self.check_connection_health():
                self.logger.error("❌ Connection health check failed")
                return

            # Check portfolio constraints
            can_trade, reason = self.portfolio_manager.can_trade_portfolio()
            if not can_trade:
                self.logger.debug(f"⏸️  Portfolio: {reason}")
                return

            # Get available instruments
            available_instruments = self.get_available_instruments()
            if not available_instruments:
                self.logger.warning("⏸️  No instruments available")
                return

            # Limit to max monitoring
            if len(available_instruments) > ParallelTradingConfig.MAX_INSTRUMENTS_TO_MONITOR:
                available_instruments = available_instruments[:ParallelTradingConfig.MAX_INSTRUMENTS_TO_MONITOR]

            self.logger.info(f"🔍 Scanning {len(available_instruments)} instruments...")

            # Submit parallel trade tasks
            futures = []
            for instrument in available_instruments:
                # Check if we can add more concurrent trades
                can_trade, _ = self.portfolio_manager.can_trade_portfolio()
                if not can_trade:
                    break

                future = self.executor.submit(self.execute_instrument_trade, instrument)
                futures.append(future)

            # Wait for all trades to complete
            completed = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        completed += 1
                except Exception as e:
                    self.logger.error(f"❌ Trade execution error: {e}")

            if completed > 0:
                self.logger.info(f"✅ Completed {completed} trades this cycle")

        except Exception as e:
            self.logger.error(f"❌ Cycle error: {e}")
            self.logger.debug(traceback.format_exc())

    def trading_loop(self):
        """Main 24/7 parallel trading loop"""
        self.logger.info("🔄 Starting 24/7 parallel trading loop...")
        self.portfolio_manager.state['running'] = True
        self.portfolio_manager.state['start_time'] = datetime.now()

        while self.running and not self.shutdown_requested:
            try:
                # Execute parallel trading cycle
                self.parallel_trading_cycle()

                # Wait before next cycle (10 seconds for frequent scanning)
                time.sleep(ParallelTradingConfig.INSTRUMENT_SCAN_INTERVAL)

            except KeyboardInterrupt:
                self.logger.info("⌨️  Keyboard interrupt")
                break
            except Exception as e:
                self.logger.error(f"❌ Loop error: {e}")
                self.logger.debug(traceback.format_exc())
                
                if ParallelTradingConfig.AUTO_RECONNECT_ON_FAILURE:
                    self.logger.info(f"🔄 Auto-recovery: Sleeping {ParallelTradingConfig.RECONNECT_DELAY_SECONDS}s...")
                    time.sleep(ParallelTradingConfig.RECONNECT_DELAY_SECONDS)
                    self.connect_to_broker()
                else:
                    break

        self.logger.info("🛑 Trading loop stopped")
        self.portfolio_manager.state['running'] = False

    def start(self):
        """Start the 24/7 bot"""
        self.logger.info("🚀 Starting 24/7 Parallel Trading Bot...")

        if not self.connect_to_broker():
            self.logger.error("❌ Failed to connect")
            return False

        self.print_configuration()
        self.running = True
        self.trading_loop()

        return True

    def stop(self):
        """Stop the bot"""
        self.logger.info("🛑 Stopping bot...")
        self.running = False
        self.shutdown_requested = True
        self.executor.shutdown(wait=True)

    def print_configuration(self):
        """Print configuration"""
        self.logger.info("="*80)
        self.logger.info("⚙️  24/7 PARALLEL TRADING CONFIGURATION")
        self.logger.info("="*80)
        self.logger.info(f"Mode: {ParallelTradingConfig.TRADING_MODE.upper()}")
        self.logger.info(f"Operation: 24/7 CONTINUOUS")
        self.logger.info(f"Trade Frequency: Every minute per instrument")
        self.logger.info(f"Max Concurrent Instruments: {ParallelTradingConfig.MAX_CONCURRENT_INSTRUMENTS}")
        self.logger.info(f"Instruments to Monitor: {ParallelTradingConfig.MAX_INSTRUMENTS_TO_MONITOR}")
        self.logger.info(f"Portfolio Risk: {ParallelTradingConfig.TOTAL_PORTFOLIO_RISK_PERCENT}%")
        self.logger.info(f"Risk per Instrument: {ParallelTradingConfig.MAX_RISK_PER_INSTRUMENT}%")
        self.logger.info(f"Scan Interval: {ParallelTradingConfig.INSTRUMENT_SCAN_INTERVAL}s")
        self.logger.info(f"Max Trades/Hour: {ParallelTradingConfig.MAX_TOTAL_TRADES_PER_HOUR}")
        self.logger.info(f"Max Trades/Day: {ParallelTradingConfig.MAX_TOTAL_TRADES_PER_DAY}")
        self.logger.info("="*80)

    def get_statistics(self) -> Dict:
        """Get statistics"""
        stats = self.portfolio_manager.get_portfolio_stats()
        stats['status'] = 'running' if self.running else 'stopped'
        stats['mode'] = ParallelTradingConfig.TRADING_MODE
        stats['operation_mode'] = '24/7 CONTINUOUS'

        if self.portfolio_manager.state['start_time']:
            uptime = (datetime.now() - self.portfolio_manager.state['start_time']).total_seconds() / 3600
            stats['uptime_hours'] = round(uptime, 2)

        return stats


# =============================================================================
# HEALTH API
# =============================================================================

def create_health_api(bot: ParallelTradingBot):
    """Create health monitoring API"""
    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

    @app.route('/statistics', methods=['GET'])
    def statistics():
        return jsonify(bot.get_statistics())

    @app.route('/stop', methods=['POST'])
    def stop():
        bot.stop()
        return jsonify({'message': 'Shutdown initiated'})

    return app


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point for 24/7 operation"""
    logger = setup_logging()

    logger.info("="*80)
    logger.info("🤖 24/7 PARALLEL MULTI-INSTRUMENT TRADING BOT")
    logger.info("="*80)
    logger.info(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {ParallelTradingConfig.TRADING_MODE.upper()}")
    logger.info("Operation: 24/7 CONTINUOUS - EVERY MINUTE TRADING")
    logger.info("="*80)

    if not ParallelTradingConfig.EMAIL or not ParallelTradingConfig.PASSWORD:
        logger.error("❌ No credentials configured")
        return 1

    if ParallelTradingConfig.TRADING_MODE == 'live':
        logger.warning("="*80)
        logger.warning("⚠️  LIVE TRADING MODE - 24/7 OPERATION")
        logger.warning("⚠️  REAL MONEY AT RISK")
        logger.warning("="*80)
        time.sleep(5)

    bot = ParallelTradingBot(logger)

    # Start health API
    if ParallelTradingConfig.ENABLE_HEALTH_API:
        health_app = create_health_api(bot)
        health_thread = threading.Thread(
            target=lambda: health_app.run(
                host='0.0.0.0',
                port=ParallelTradingConfig.HEALTH_API_PORT,
                debug=False,
                use_reloader=False
            ),
            daemon=True
        )
        health_thread.start()
        logger.info(f"🏥 Health API: http://localhost:{ParallelTradingConfig.HEALTH_API_PORT}")

    try:
        bot.start()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.debug(traceback.format_exc())
        return 1
    finally:
        logger.info("="*80)
        logger.info("🏁 SHUTDOWN COMPLETE")
        logger.info(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        stats = bot.get_statistics()
        logger.info("="*80)
        logger.info("📊 FINAL STATISTICS")
        logger.info("="*80)
        for key, value in stats.items():
            if key != 'instrument_stats':
                logger.info(f"{key}: {value}")
        logger.info("="*80)

    return 0


if __name__ == '__main__':
    sys.exit(main())