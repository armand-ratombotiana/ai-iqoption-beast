#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 BINARY-OPTION OPTIMIZED 24/7 PARALLEL TRADING BOT
Production-Ready Continuous Multi-Asset Trading System with Binary-Option Specifics

Features:
- Binary-option payout-aware position sizing
- Expiration alignment and time-to-expiry validation
- Noise filtering with neutral thresholds
- Dynamic calibration based on historical performance
- Real-time technical analysis at trade entry
- 24/7 continuous operation with auto-recovery
- Trade multiple instruments simultaneously
- Advanced portfolio risk management
- Fictitious $100 balance tracking for realistic testing

CRITICAL: Optimized for binary options with payout/expiration awareness!
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

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Database logging system (PROJECT_FOCUS_GUIDELINES: "Log everything")
try:
    from database import TradeLogger
    DB_LOGGING_ENABLED = True
except ImportError:
    TradeLogger = None
    DB_LOGGING_ENABLED = False
    print("⚠️  Database logging not available")

# Advanced strategy system with TA-Lib
USE_ADVANCED_STRATEGIES = os.getenv('USE_ADVANCED_STRATEGIES', 'true').lower() == 'true'
try:
    if USE_ADVANCED_STRATEGIES:
        from strategies.strategy_integrator import create_integrator
        ADVANCED_STRATEGIES_AVAILABLE = True
    else:
        ADVANCED_STRATEGIES_AVAILABLE = False
except ImportError:
    ADVANCED_STRATEGIES_AVAILABLE = False
    if USE_ADVANCED_STRATEGIES:
        print("⚠️  Advanced strategies requested but not available")

# Add src to path
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

from flask import Flask, jsonify, request
from iqoptionapi.stable_api import IQ_Option


# =============================================================================
# BINARY-OPTION SPECIFIC DATA STRUCTURES
# =============================================================================

@dataclass
class BinaryOptionContext:
    """Binary option specific context for trade decisions"""
    payout_ratio: Optional[float] = None
    min_required_win_rate: Optional[float] = None
    breakeven_win_rate: Optional[float] = None
    expected_value: Optional[float] = None
    time_to_expiry_seconds: Optional[int] = None
    expiration_aligned: bool = False
    timing_risk: bool = False
    noise_level: float = 0.0
    signal_strength: float = 0.0
    meets_payout_threshold: bool = False
    meets_timing_threshold: bool = False
    meets_noise_threshold: bool = False
    tradeable: bool = False
    rejection_reason: Optional[str] = None


@dataclass
class CalibrationMetrics:
    """Calibration metrics for adaptive thresholds"""
    instrument: str
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    avg_payout: float = 0.0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    sharpe_ratio: float = 0.0
    kelly_fraction: float = 0.0
    confidence_calibration: float = 1.0  # Multiplier for confidence
    noise_threshold: float = 0.3  # Dynamic noise threshold
    neutral_threshold: float = 0.6  # Dynamic neutral threshold
    last_calibration: datetime = field(default_factory=datetime.now)
    profit_history: deque = field(default_factory=lambda: deque(maxlen=100))


# =============================================================================
# ENHANCED CONFIGURATION WITH BINARY-OPTION SPECIFICS
# =============================================================================

class ParallelTradingConfig:
    """Configuration for binary-option optimized parallel trading"""

    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'demo')
    CONTINUOUS_OPERATION_24_7 = True

    # FICTITIOUS BALANCE TESTING - Set to $100 for realistic testing
    ENABLE_FICTITIOUS_BALANCE = bool(os.getenv('ENABLE_FICTITIOUS_BALANCE', True))
    FICTITIOUS_START_BALANCE = float(os.getenv('FICTITIOUS_START_BALANCE', 100.0))

    # Parallel Trading Settings - OPTIMIZED to reduce queue delays
    MAX_CONCURRENT_INSTRUMENTS = int(os.getenv('MAX_CONCURRENT_INSTRUMENTS', 3))  # Reduced from 5 to 3
    MAX_INSTRUMENTS_TO_MONITOR = int(os.getenv('MAX_INSTRUMENTS_TO_MONITOR', 20))
    ENABLE_DYNAMIC_INSTRUMENT_SELECTION = True
    MAX_PARALLEL_EXECUTIONS = 3  # Limit simultaneous trade executions to prevent timing failures

    # Binary Options Settings - 1 MINUTE TRADES
    BINARY_OPTION_DURATION = 1  # 1 minute
    DEFAULT_TRADE_AMOUNT = float(os.getenv('BASE_TRADE_AMOUNT', 1.0))
    MIN_TRADE_AMOUNT = 1.0
    MAX_TRADE_AMOUNT = float(os.getenv('MAX_TRADE_AMOUNT', 10.0))

    # Binary-Option Specific Thresholds - OPTIMIZED for balance
    MIN_PAYOUT_RATIO = float(os.getenv('MIN_PAYOUT_RATIO', 0.65))  # 65% minimum payout (was 70%)
    SAFETY_MARGIN_WIN_RATE = float(os.getenv('SAFETY_MARGIN_WIN_RATE', 0.02))  # 2% safety margin

    # Timing thresholds for expiration alignment
    MIN_TIME_TO_EXPIRY_SECONDS = int(os.getenv('MIN_TIME_TO_EXPIRY_SECONDS', 40))
    MAX_TIME_TO_EXPIRY_SECONDS = int(os.getenv('MAX_TIME_TO_EXPIRY_SECONDS', 55))
    EXPIRATION_BUFFER_SECONDS = int(os.getenv('EXPIRATION_BUFFER_SECONDS', 25))

    # Noise filtering
    NOISE_THRESHOLD = float(os.getenv('NOISE_THRESHOLD', 0.3))
    NEUTRAL_THRESHOLD = float(os.getenv('NEUTRAL_THRESHOLD', 0.6))

    # Dynamic calibration
    ENABLE_DYNAMIC_CALIBRATION = bool(os.getenv('ENABLE_DYNAMIC_CALIBRATION', True))
    MIN_TRADES_FOR_CALIBRATION = int(os.getenv('MIN_TRADES_FOR_CALIBRATION', 10))
    CALIBRATION_INTERVAL_TRADES = int(os.getenv('CALIBRATION_INTERVAL_TRADES', 5))

    # Kelly sizing
    ENABLE_KELLY_SIZING = bool(os.getenv('ENABLE_KELLY_SIZING', True))
    KELLY_FRACTION = float(os.getenv('KELLY_FRACTION', 0.25))
    MAX_KELLY_POSITION = float(os.getenv('MAX_KELLY_POSITION', 10.0))

    # Martingale
    MARTINGALE_ENABLED = bool(os.getenv('MARTINGALE_ENABLED', False))
    MARTINGALE_BASE_MULTIPLIER = float(os.getenv('MARTINGALE_BASE_MULTIPLIER', 2.0))
    MARTINGALE_MAX_DOUBLINGS = int(os.getenv('MARTINGALE_MAX_DOUBLINGS', 3))

    # Trading Assets
    INSTRUMENT_POOL = os.getenv('TRADING_ASSETS',
        'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,AUDJPY,EURAUD,GBPAUD,USDCHF,EURCAD,GBPCAD,AUDCAD'
    ).split(',')

    # Risk Management
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 50))
    MAX_DAILY_PROFIT = float(os.getenv('MAX_DAILY_PROFIT', 100))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', 5))
    MIN_BALANCE = float(os.getenv('MIN_BALANCE', 50))
    MAX_TRADES_PER_HOUR = int(os.getenv('MAX_TRADES_PER_HOUR', 300))
    MAX_TOTAL_TRADES_PER_HOUR = int(os.getenv('MAX_TOTAL_TRADES_PER_HOUR', 300))
    MAX_TOTAL_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', 7200))
    MAX_TRADES_PER_INSTRUMENT_HOUR = int(os.getenv('MAX_TRADES_PER_INSTRUMENT_HOUR', 60))
    MIN_SECONDS_BETWEEN_INSTRUMENT_TRADES = int(os.getenv('MIN_SECONDS_BETWEEN_INSTRUMENT_TRADES', 70))

    # Portfolio risk
    TOTAL_PORTFOLIO_RISK_PERCENT = float(os.getenv('PORTFOLIO_RISK_PERCENT', 10.0))
    MAX_RISK_PER_INSTRUMENT = float(os.getenv('MAX_RISK_PER_INSTRUMENT', 2.5))

    # Timing
    INSTRUMENT_SCAN_INTERVAL = int(os.getenv('INSTRUMENT_SCAN_INTERVAL', 3))
    WAIT_FOR_RESULT_SECONDS = int(os.getenv('WAIT_FOR_RESULT_SECONDS', 65))
    SIGNAL_GENERATION_TIMEOUT = float(os.getenv('SIGNAL_GENERATION_TIMEOUT', 5.0))

    # Worker threads
    MAX_WORKER_THREADS = int(os.getenv('MAX_WORKER_THREADS', 15))

    # Connection health
    CONNECTION_CHECK_INTERVAL = 300
    AUTO_RECONNECT_ON_FAILURE = True
    RECONNECT_DELAY_SECONDS = 60

    # Market data caching
    MARKET_DATA_CACHE_SECONDS = 30

    # API rate limiting
    API_MIN_INTERVAL = float(os.getenv('API_MIN_INTERVAL', 0.3))
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', 3))
    API_RETRY_BACKOFF = float(os.getenv('API_RETRY_BACKOFF', 1.5))

    # AI Signal Requirements
    MIN_AI_CONFIDENCE = int(os.getenv('MIN_AI_CONFIDENCE', 60))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = Path('logs')

    # API Credentials
    EMAIL = os.getenv('IQOPTION_EMAIL', '')
    PASSWORD = os.getenv('IQOPTION_PASSWORD', '')

    # Health Monitoring
    ENABLE_HEALTH_API = bool(os.getenv('ENABLE_HEALTH_API', True))
    HEALTH_API_PORT = int(os.getenv('HEALTH_API_PORT', 5001))


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure comprehensive logging"""
    ParallelTradingConfig.LOG_DIR.mkdir(exist_ok=True)

    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(
        ParallelTradingConfig.LOG_DIR / f'parallel_bot_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    console_handler.setLevel(getattr(logging, ParallelTradingConfig.LOG_LEVEL))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger(__name__)


# =============================================================================
# BINARY OPTION CALCULATOR
# =============================================================================

class BinaryOptionCalculator:
    """Binary option calculations for win rates and expected value"""

    @staticmethod
    def calculate_breakeven_win_rate(payout_ratio: float) -> float:
        """Calculate breakeven win rate for given payout"""
        return 1.0 / (1.0 + payout_ratio)

    @staticmethod
    def calculate_required_win_rate(payout_ratio: float, safety_margin: float = 0.02) -> float:
        """Calculate required win rate with safety margin"""
        breakeven = BinaryOptionCalculator.calculate_breakeven_win_rate(payout_ratio)
        return breakeven + safety_margin

    @staticmethod
    def calculate_expected_value(win_rate: float, payout_ratio: float, amount: float = 1.0) -> float:
        """Calculate expected value of a trade"""
        return (win_rate * payout_ratio * amount) - ((1 - win_rate) * amount)

    @staticmethod
    def calculate_kelly_fraction(win_rate: float, payout_ratio: float) -> float:
        """Calculate Kelly fraction for position sizing"""
        if payout_ratio <= 0:
            return 0.0
        return max(0, (win_rate * (1 + payout_ratio) - 1) / payout_ratio)

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio from returns"""
        if not returns or len(returns) < 2:
            return 0.0
        import statistics
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        if std_return == 0:
            return 0.0
        return (mean_return - risk_free_rate) / std_return


# =============================================================================
# API CLIENT WITH RATE LIMITING
# =============================================================================

class ApiClient:
    """Wrapper for IQ Option API with rate limiting and retries"""

    def __init__(self, api, min_interval: float = 0.3, max_retries: int = 3, backoff_base: float = 1.5):
        self.api = api
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.last_call = 0
        self.lock = threading.Lock()

    def _rate_limit(self):
        """Enforce minimum interval between API calls"""
        with self.lock:
            elapsed = time.time() - self.last_call
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_call = time.time()

    def _retry_call(self, func, *args, **kwargs):
        """Retry API call with exponential backoff"""
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
# INSTRUMENT STATE MANAGER
# =============================================================================

class InstrumentStateManager:
    """Thread-safe state manager for individual instruments"""

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
            'active_trade_id': None,
            'last_execution_time_ms': 0,
            'last_payout_ratio': None,
            'avg_payout_ratio': 0.0,
            'payout_sum': 0.0,
            'payout_count': 0
        }
        self.calibration = CalibrationMetrics(instrument=instrument)

    def can_trade(self) -> tuple[bool, str]:
        """Check if this instrument can trade"""
        with self.lock:
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            if self.state['hour_start'] != current_hour:
                self.state['trades_this_hour'] = 0
                self.state['hour_start'] = current_hour

            current_minute = datetime.now().replace(second=0, microsecond=0)
            if self.state['minute_start'] != current_minute:
                self.state['trades_this_minute'] = 0
                self.state['minute_start'] = current_minute

            if self.state['is_trading']:
                return False, "Trade already active"

            if self.state['trades_this_minute'] >= 1:
                return False, "Already traded this minute"

            if self.state['trades_this_hour'] >= ParallelTradingConfig.MAX_TRADES_PER_INSTRUMENT_HOUR:
                return False, f"Hourly limit reached"

            if self.state['last_trade_time']:
                elapsed = (datetime.now() - self.state['last_trade_time']).total_seconds()
                if elapsed < ParallelTradingConfig.MIN_SECONDS_BETWEEN_INSTRUMENT_TRADES:
                    return False, f"Wait {int(ParallelTradingConfig.MIN_SECONDS_BETWEEN_INSTRUMENT_TRADES - elapsed)}s"

            # Check consecutive losses
            if self.state['consecutive_losses'] >= ParallelTradingConfig.MAX_CONSECUTIVE_LOSSES:
                return False, f"Max consecutive losses reached"

            return True, "OK"

    def start_trade(self, trade_id: str, payout_ratio: Optional[float] = None):
        """Mark instrument as trading"""
        with self.lock:
            self.state['is_trading'] = True
            self.state['active_trade_id'] = trade_id
            self.state['last_trade_time'] = datetime.now()
            self.state['trades_this_hour'] += 1
            self.state['trades_this_minute'] += 1
            self.state['total_trades'] += 1
            
            if payout_ratio is not None:
                self.state['last_payout_ratio'] = payout_ratio
                self.state['payout_sum'] += payout_ratio
                self.state['payout_count'] += 1
                self.state['avg_payout_ratio'] = self.state['payout_sum'] / self.state['payout_count']

    def complete_trade(self, won: bool, profit: float, execution_time_ms: int):
        """Complete a trade and update stats"""
        with self.lock:
            self.state['is_trading'] = False
            self.state['active_trade_id'] = None
            self.state['profit'] += profit
            self.state['last_execution_time_ms'] = execution_time_ms

            # Update calibration metrics
            self.calibration.total_trades += 1
            self.calibration.profit_history.append(profit)
            
            if won:
                self.state['wins'] += 1
                self.state['consecutive_wins'] += 1
                self.state['consecutive_losses'] = 0
                self.calibration.wins += 1
                self.calibration.avg_profit = (
                    (self.calibration.avg_profit * (self.calibration.wins - 1) + profit) / 
                    self.calibration.wins
                )
            else:
                self.state['losses'] += 1
                self.state['consecutive_losses'] += 1
                self.state['consecutive_wins'] = 0
                self.calibration.losses += 1
                self.calibration.avg_loss = (
                    (self.calibration.avg_loss * (self.calibration.losses - 1) + abs(profit)) / 
                    self.calibration.losses
                )
            
            # Update win rate
            if self.calibration.total_trades > 0:
                self.calibration.win_rate = self.calibration.wins / self.calibration.total_trades
            
            # Update average payout
            if self.state['last_payout_ratio'] is not None:
                self.calibration.avg_payout = self.state['avg_payout_ratio']
            
            # Recalibrate if needed
            if (self.calibration.total_trades % ParallelTradingConfig.CALIBRATION_INTERVAL_TRADES == 0 and
                self.calibration.total_trades >= ParallelTradingConfig.MIN_TRADES_FOR_CALIBRATION):
                self._recalibrate()

    def _recalibrate(self):
        """Recalibrate thresholds based on performance"""
        if not ParallelTradingConfig.ENABLE_DYNAMIC_CALIBRATION:
            return
        
        # Calculate Sharpe ratio
        if len(self.calibration.profit_history) >= 2:
            returns = list(self.calibration.profit_history)
            self.calibration.sharpe_ratio = BinaryOptionCalculator.calculate_sharpe_ratio(returns)
        
        # Calculate Kelly fraction
        if self.calibration.avg_payout > 0:
            self.calibration.kelly_fraction = BinaryOptionCalculator.calculate_kelly_fraction(
                self.calibration.win_rate,
                self.calibration.avg_payout
            )
        
        # Adjust confidence calibration based on performance
        if self.calibration.win_rate > 0.55:  # Performing well
            self.calibration.confidence_calibration = min(1.2, self.calibration.confidence_calibration + 0.05)
        elif self.calibration.win_rate < 0.45:  # Performing poorly
            self.calibration.confidence_calibration = max(0.8, self.calibration.confidence_calibration - 0.05)
        
        # Adjust noise threshold
        if self.calibration.sharpe_ratio > 1.0:  # Good risk-adjusted returns
            self.calibration.noise_threshold = max(0.2, self.calibration.noise_threshold - 0.05)
        elif self.calibration.sharpe_ratio < 0.5:  # Poor risk-adjusted returns
            self.calibration.noise_threshold = min(0.5, self.calibration.noise_threshold + 0.05)
        
        # Adjust neutral threshold
        if self.calibration.win_rate > 0.55:
            self.calibration.neutral_threshold = max(0.5, self.calibration.neutral_threshold - 0.05)
        elif self.calibration.win_rate < 0.45:
            self.calibration.neutral_threshold = min(0.7, self.calibration.neutral_threshold + 0.05)
        
        self.calibration.last_calibration = datetime.now()

    def get_calibrated_thresholds(self) -> Dict:
        """Get current calibrated thresholds"""
        with self.lock:
            return {
                'confidence_multiplier': self.calibration.confidence_calibration,
                'noise_threshold': self.calibration.noise_threshold,
                'neutral_threshold': self.calibration.neutral_threshold,
                'kelly_fraction': self.calibration.kelly_fraction
            }

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
                'trades_this_hour': self.state['trades_this_hour'],
                'avg_execution_ms': self.state['last_execution_time_ms'],
                'avg_payout_ratio': round(self.state['avg_payout_ratio'], 4),
                'sharpe_ratio': round(self.calibration.sharpe_ratio, 3),
                'kelly_fraction': round(self.calibration.kelly_fraction, 4),
                'calibration': {
                    'confidence_multiplier': round(self.calibration.confidence_calibration, 3),
                    'noise_threshold': round(self.calibration.noise_threshold, 3),
                    'neutral_threshold': round(self.calibration.neutral_threshold, 3)
                }
            }


# =============================================================================
# PORTFOLIO STATE MANAGER
# =============================================================================

class PortfolioStateManager:
    """Thread-safe portfolio-wide state management"""

    def __init__(self):
        self.lock = threading.Lock()
        self.instrument_managers: Dict[str, InstrumentStateManager] = {}
        self.state = {
            'running': False,
            'start_time': None,
            'current_balance': 0.0,
            'start_balance': 0.0,
            'daily_profit': 0.0,
            'daily_loss': 0.0,
            'trades_today': 0,
            'wins_today': 0,
            'losses_today': 0,
            'last_reset': datetime.now().date(),
            'trades_this_hour': 0,
            'hour_start': datetime.now().replace(minute=0, second=0, microsecond=0),
            'active_instruments': set(),
            'total_risk_allocated': 0.0,
            'api_connected': False,
            'last_error': None,
            'reconnect_count': 0,
            'last_connection_check': datetime.now(),
            'total_uptime_seconds': 0,
            'total_trades_all_time': 0,
            'avg_scan_time_ms': 0,
            'avg_execution_time_ms': 0,
            # Fictitious balance tracking
            'fictitious_balance_enabled': ParallelTradingConfig.ENABLE_FICTITIOUS_BALANCE,
            'fictitious_balance': ParallelTradingConfig.FICTITIOUS_START_BALANCE,
            'fictitious_start_balance': ParallelTradingConfig.FICTITIOUS_START_BALANCE,
            'real_balance': 0.0,
            'real_start_balance': 0.0
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

    def update_balance(self, real_balance: float, profit: float = 0.0):
        """Update both real and fictitious balances"""
        with self.lock:
            self.state['real_balance'] = real_balance
            
            if self.state['fictitious_balance_enabled']:
                # Update fictitious balance with P&L
                self.state['fictitious_balance'] += profit
                # Use fictitious balance for trading decisions
                self.state['current_balance'] = self.state['fictitious_balance']
            else:
                # Use real balance
                self.state['current_balance'] = real_balance

    def can_trade_portfolio(self) -> tuple[bool, str]:
        """Check portfolio-wide trading constraints"""
        self.reset_daily_stats()
        self.reset_hourly_stats()

        with self.lock:
            if self.state['current_balance'] < ParallelTradingConfig.MIN_BALANCE:
                return False, f"Balance too low"

            if self.state['daily_loss'] >= ParallelTradingConfig.MAX_DAILY_LOSS:
                return False, f"Daily loss limit"

            if self.state['daily_profit'] >= ParallelTradingConfig.MAX_DAILY_PROFIT:
                return False, f"Daily profit target"

            if self.state['trades_this_hour'] >= ParallelTradingConfig.MAX_TOTAL_TRADES_PER_HOUR:
                return False, f"Hourly limit"

            if self.state['trades_today'] >= ParallelTradingConfig.MAX_TOTAL_TRADES_PER_DAY:
                return False, f"Daily limit"

            if len(self.state['active_instruments']) >= ParallelTradingConfig.MAX_CONCURRENT_INSTRUMENTS:
                return False, f"Max concurrent"

            max_portfolio_risk = self.state['current_balance'] * (ParallelTradingConfig.TOTAL_PORTFOLIO_RISK_PERCENT / 100)
            if self.state['total_risk_allocated'] >= max_portfolio_risk:
                return False, f"Portfolio risk limit"

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

            instrument_stats = []
            for manager in self.instrument_managers.values():
                stats = manager.get_stats()
                if stats['total_trades'] > 0:
                    instrument_stats.append(stats)

            instrument_stats.sort(key=lambda x: x['profit'], reverse=True)

            stats = {
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
                'total_trades_all_time': self.state['total_trades_all_time'],
                'avg_scan_time_ms': self.state['avg_scan_time_ms'],
                'avg_execution_time_ms': self.state['avg_execution_time_ms']
            }

            # Add fictitious balance info if enabled
            if self.state['fictitious_balance_enabled']:
                stats['fictitious_balance_mode'] = True
                stats['fictitious_balance'] = round(self.state['fictitious_balance'], 2)
                stats['fictitious_start_balance'] = round(self.state['fictitious_start_balance'], 2)
                stats['fictitious_pnl'] = round(self.state['fictitious_balance'] - self.state['fictitious_start_balance'], 2)
                stats['fictitious_pnl_percent'] = round(
                    ((self.state['fictitious_balance'] - self.state['fictitious_start_balance']) / 
                     self.state['fictitious_start_balance']) * 100, 2
                )
                stats['real_balance'] = round(self.state['real_balance'], 2)
                stats['real_start_balance'] = round(self.state['real_start_balance'], 2)
            else:
                stats['fictitious_balance_mode'] = False

            return stats


# =============================================================================
# BINARY-OPTION OPTIMIZED TRADING BOT
# =============================================================================

class ParallelTradingBot:
    """Binary-option optimized 24/7 parallel trading bot"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.portfolio_manager = PortfolioStateManager()
        self.api: Optional[IQ_Option] = None
        self.api_client = None
        self.running = False
        self.shutdown_requested = False
        self.executor = ThreadPoolExecutor(max_workers=ParallelTradingConfig.MAX_WORKER_THREADS)
        self.market_data_cache = {}
        self.cache_lock = threading.Lock()

        # Database logging (PROJECT_FOCUS_GUIDELINES: "Log everything")
        self.trade_logger = None
        if DB_LOGGING_ENABLED:
            try:
                self.trade_logger = TradeLogger("logs/kael_trading.db")
                self.logger.info("✅ Database logging enabled")
            except Exception as e:
                self.logger.warning(f"⚠️  Database logging disabled: {e}")

        # Advanced strategy system
        self.strategy_integrator = None
        if ADVANCED_STRATEGIES_AVAILABLE:
            try:
                risk_profile = os.getenv('STRATEGY_RISK_PROFILE', 'moderate')
                self.strategy_integrator = create_integrator(risk_profile)
                self.logger.info(f"✅ Advanced strategies enabled (profile: {risk_profile})")
            except Exception as e:
                self.logger.warning(f"⚠️  Advanced strategies disabled: {e}")

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.logger.info("="*80)
        self.logger.info("🎯 BINARY-OPTION OPTIMIZED 24/7 PARALLEL TRADING BOT")
        self.logger.info(f"💰 Min Payout: {ParallelTradingConfig.MIN_PAYOUT_RATIO:.1%}")
        self.logger.info(f"⏰ Expiration Window: {ParallelTradingConfig.MIN_TIME_TO_EXPIRY_SECONDS}-{ParallelTradingConfig.MAX_TIME_TO_EXPIRY_SECONDS}s")
        self.logger.info(f"🔇 Noise Threshold: {ParallelTradingConfig.NOISE_THRESHOLD:.1%}")
        self.logger.info(f"📊 Calibration: {'Enabled' if ParallelTradingConfig.ENABLE_DYNAMIC_CALIBRATION else 'Disabled'}")
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
                self.logger.info(f"🔌 Connecting (Attempt {attempt + 1}/{max_attempts})...")

                if not ParallelTradingConfig.EMAIL or not ParallelTradingConfig.PASSWORD:
                    self.logger.error("❌ No credentials")
                    return False

                self.api = IQ_Option(
                    ParallelTradingConfig.EMAIL,
                    ParallelTradingConfig.PASSWORD
                )

                check, reason = self.api.connect()
                if not check:
                    self.logger.error(f"❌ Failed: {reason}")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                        continue
                    return False

                if ParallelTradingConfig.TRADING_MODE == 'live':
                    self.api.change_balance('REAL')
                    self.logger.warning("⚠️  LIVE MODE")
                else:
                    self.api.change_balance('PRACTICE')
                    self.logger.info("✅ Demo mode")

                real_balance = self.api.get_balance()
                
                # Initialize balances
                if ParallelTradingConfig.ENABLE_FICTITIOUS_BALANCE:
                    # Set fictitious balance for testing
                    self.portfolio_manager.state['real_balance'] = real_balance
                    self.portfolio_manager.state['real_start_balance'] = real_balance
                    self.portfolio_manager.state['fictitious_balance'] = ParallelTradingConfig.FICTITIOUS_START_BALANCE
                    self.portfolio_manager.state['fictitious_start_balance'] = ParallelTradingConfig.FICTITIOUS_START_BALANCE
                    self.portfolio_manager.state['current_balance'] = ParallelTradingConfig.FICTITIOUS_START_BALANCE
                    self.portfolio_manager.state['start_balance'] = ParallelTradingConfig.FICTITIOUS_START_BALANCE
                    
                    self.logger.info("="*80)
                    self.logger.info("💰 FICTITIOUS BALANCE MODE ENABLED")
                    self.logger.info(f"   Testing Balance: ${ParallelTradingConfig.FICTITIOUS_START_BALANCE:.2f}")
                    self.logger.info(f"   Real Balance: ${real_balance:.2f}")
                    self.logger.info("   P&L will be tracked from $100 baseline")
                    self.logger.info("="*80)
                else:
                    # Use real balance
                    self.portfolio_manager.state['current_balance'] = real_balance
                    self.portfolio_manager.state['start_balance'] = real_balance
                
                self.portfolio_manager.state['api_connected'] = True
                self.portfolio_manager.state['last_connection_check'] = datetime.now()

                # Wrap API with a rate-limited client to avoid hitting broker rate limits
                try:
                    self.api_client = ApiClient(
                        self.api,
                        min_interval=ParallelTradingConfig.API_MIN_INTERVAL,
                        max_retries=ParallelTradingConfig.API_MAX_RETRIES,
                        backoff_base=ParallelTradingConfig.API_RETRY_BACKOFF
                    )
                except Exception:
                    self.api_client = None

                self.logger.info(f"✅ Connected. Trading Balance: ${self.portfolio_manager.state['current_balance']:.2f}")
                return True

            except Exception as e:
                self.logger.error(f"❌ Error: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue
                return False

        return False

    def check_connection_health(self) -> bool:
        """Check connection health"""
        try:
            last_check = self.portfolio_manager.state['last_connection_check']
            if (datetime.now() - last_check).total_seconds() < ParallelTradingConfig.CONNECTION_CHECK_INTERVAL:
                return True

            # Prefer the rate-limited client when available
            connected = True
            try:
                if self.api_client:
                    connected = bool(self.api_client.check_connect())
                else:
                    connected = bool(self.api.check_connect())
            except Exception:
                connected = False

            if not self.api or not connected:
                self.logger.warning("⚠️  Reconnecting...")
                self.portfolio_manager.state['reconnect_count'] += 1
                return self.connect_to_broker()

            try:
                if self.api_client:
                    balance = self.api_client.get_balance()
                else:
                    balance = self.api.get_balance()
            except Exception as e:
                self.logger.error(f"❌ Failed to fetch balance during health check: {e}")
                return False

            self.portfolio_manager.state['current_balance'] = balance
            self.portfolio_manager.state['last_connection_check'] = datetime.now()

            return True

        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return False

    def get_available_instruments(self) -> List[str]:
        """Get available instruments with caching"""
        try:
            with self.cache_lock:
                if 'instruments' in self.market_data_cache:
                    cache_time, instruments = self.market_data_cache['instruments']
                    if (datetime.now() - cache_time).total_seconds() < ParallelTradingConfig.MARKET_DATA_CACHE_SECONDS:
                        return instruments

            if self.api_client:
                open_markets = self.api_client.get_all_open_time()
            else:
                open_markets = self.api.get_all_open_time()
            if not open_markets or 'binary' not in open_markets:
                return []

            binary_markets = open_markets['binary']
            available = []

            for instrument in ParallelTradingConfig.INSTRUMENT_POOL:
                instrument = instrument.strip()
                for suffix in ['', '-op', '-OTC']:
                    test_name = f"{instrument}{suffix}"
                    if test_name in binary_markets and binary_markets[test_name].get('open', False):
                        available.append(test_name)
                        break

            with self.cache_lock:
                self.market_data_cache['instruments'] = (datetime.now(), available)

            return available

        except Exception as e:
            self.logger.error(f"❌ Error getting instruments: {e}")
            return []

    def get_binary_option_context(self, instrument: str) -> BinaryOptionContext:
        """Get binary-option specific context for instrument"""
        context = BinaryOptionContext()
        
        try:
            # Get payout ratio
            if (self.api_client and hasattr(self.api_client, 'get_all_profit')) or (self.api and hasattr(self.api, 'get_all_profit')):
                try:
                    all_profit = self.api_client.get_all_profit() if self.api_client else self.api.get_all_profit()
                except Exception:
                    all_profit = self.api.get_all_profit() if self.api and hasattr(self.api, 'get_all_profit') else {}
                base_name = instrument.split('-')[0]
                profits = all_profit.get(base_name) or all_profit.get(instrument) or {}
                payout_ratio = profits.get('binary') if isinstance(profits, dict) else None
                
                if payout_ratio is None:
                    for key in list(all_profit.keys()):
                        if key.upper().startswith(base_name.upper()):
                            payout_ratio = all_profit[key].get('binary')
                            break
                
                if payout_ratio is not None:
                    context.payout_ratio = float(payout_ratio)
                    context.breakeven_win_rate = BinaryOptionCalculator.calculate_breakeven_win_rate(payout_ratio)
                    context.min_required_win_rate = BinaryOptionCalculator.calculate_required_win_rate(
                        payout_ratio, 
                        ParallelTradingConfig.SAFETY_MARGIN_WIN_RATE
                    )
                    
                    # Check payout threshold
                    context.meets_payout_threshold = payout_ratio >= ParallelTradingConfig.MIN_PAYOUT_RATIO
                    if not context.meets_payout_threshold:
                        context.rejection_reason = f"Payout {payout_ratio:.2%} < min {ParallelTradingConfig.MIN_PAYOUT_RATIO:.2%}"
        
        except Exception as e:
            self.logger.debug(f"Error getting payout for {instrument}: {e}")
        
        try:
            # Get time to expiry
            if (self.api_client and hasattr(self.api_client, 'get_remaning')) or (self.api and hasattr(self.api, 'get_remaning')):
                try:
                    rem = self.api_client.get_remaning(ParallelTradingConfig.BINARY_OPTION_DURATION) if self.api_client else self.api.get_remaning(ParallelTradingConfig.BINARY_OPTION_DURATION)
                except Exception:
                    rem = None
                if isinstance(rem, (list, tuple)) and len(rem) > 0:
                    rem_seconds = int(rem[0]) if isinstance(rem[0], (int, float)) else int(rem[1])
                else:
                    rem_seconds = int(rem)
                
                context.time_to_expiry_seconds = rem_seconds
                
                # Check expiration alignment
                context.expiration_aligned = (
                    ParallelTradingConfig.MIN_TIME_TO_EXPIRY_SECONDS <= rem_seconds <= 
                    ParallelTradingConfig.MAX_TIME_TO_EXPIRY_SECONDS
                )
                
                # Check timing risk
                context.timing_risk = (
                    rem_seconds < ParallelTradingConfig.MIN_TIME_TO_EXPIRY_SECONDS or
                    rem_seconds > ParallelTradingConfig.MAX_TIME_TO_EXPIRY_SECONDS
                )
                
                context.meets_timing_threshold = context.expiration_aligned and not context.timing_risk
                
                if not context.meets_timing_threshold:
                    context.rejection_reason = f"Time to expiry {rem_seconds}s outside window"
        
        except Exception as e:
            self.logger.debug(f"Error getting expiry for {instrument}: {e}")
        
        return context

    def get_ai_signal(self, instrument: str, context: BinaryOptionContext) -> Optional[Dict]:
        """Get AI signal with binary-option awareness and noise filtering"""
        import random
        from statistics import mean
        from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

        start_time = time.time()

        # Get calibrated thresholds
        inst_manager = self.portfolio_manager.get_instrument_manager(instrument)
        thresholds = inst_manager.get_calibrated_thresholds()

        # Fetch candles
        candles = None
        try:
            if self.api is not None:
                try:
                    raw = self.api_client.get_candles(instrument, 60, 60, time.time()) if self.api_client else self.api.get_candles(instrument, 60, 60, time.time())
                except Exception:
                    raw = None

                if raw and isinstance(raw, list) and len(raw) > 5:
                    candles = raw
        except Exception:
            candles = None

        # Fallback if no candles
        if not candles:
            return None

        # Strategy implementations
        def strat_price_action(c):
            last = c[-1]
            return ('CALL' if last['close'] > last['open'] else 'PUT' if last['close'] < last['open'] else 'NEUTRAL', 0.6)

        def strat_two_bar_reversal(c):
            if len(c) < 3:
                return ('NEUTRAL', 0.0)
            a, b, last = c[-3], c[-2], c[-1]
            if a['close'] > a['open'] and b['close'] < b['open'] and last['close'] < last['open']:
                return ('PUT', 0.7)
            if a['close'] < a['open'] and b['close'] > b['open'] and last['close'] > last['open']:
                return ('CALL', 0.7)
            return ('NEUTRAL', 0.0)

        def strat_trend_strength(c):
            if len(c) < 10:
                return ('NEUTRAL', 0.0)
            closes = [x['close'] for x in c[-10:]]
            slope = closes[-1] - closes[0]
            if slope > 0:
                return ('CALL', min(0.9, 0.5 + slope / closes[0]))
            if slope < 0:
                return ('PUT', min(0.9, 0.5 + abs(slope) / closes[0]))
            return ('NEUTRAL', 0.0)

        def strat_volume_spike(c):
            vols = [x.get('volume', 0) for x in c[-20:]]
            if not any(vols):
                return ('NEUTRAL', 0.0)
            avg = mean(vols)
            lastv = vols[-1]
            last = c[-1]
            if lastv > avg * 2:
                return ('CALL' if last['close'] > last['open'] else 'PUT', 0.75)
            return ('NEUTRAL', 0.0)

        def strat_count_green_red(c):
            window = c[-10:]
            greens = sum(1 for x in window if x['close'] > x['open'])
            reds = sum(1 for x in window if x['close'] < x['open'])
            if greens - reds >= 6:
                return ('CALL', 0.7)
            if reds - greens >= 6:
                return ('PUT', 0.7)
            return ('NEUTRAL', 0.0)

        # Very simple candle-count strategy specialized for binary options
        def strat_simple_candle_count(c):
            """Count green vs red candles in a short window and vote accordingly.

            Args:
                c (list): List of candle dictionaries, each with 'open' and 'close' keys.

            Rules:
            - Use the last N candles (default 10)
            - If greens >= reds + 3 -> strong CALL
            - If reds >= greens + 3 -> strong PUT
            - Otherwise NEUTRAL
            Score is proportional to the margin (capped)
            """
            window = c[-10:]
            total = len(window)
            if total == 0:
                return ('NEUTRAL', 0.0)
            greens = sum(1 for x in window if x['close'] > x['open'])
            reds = sum(1 for x in window if x['close'] < x['open'])
            margin = greens - reds
            # Strong directional bias threshold
            threshold = 3
            if margin >= threshold:
                # score scaled from 0.6 up to 0.95
                score = min(0.95, 0.6 + (margin / total))
                return ('CALL', round(score, 2))
            if margin <= -threshold:
                score = min(0.95, 0.6 + (abs(margin) / total))
                return ('PUT', round(score, 2))
            return ('NEUTRAL', 0.0)

        def strat_momentum(c):
            if len(c) < 14:
                return ('NEUTRAL', 0.0)
            diffs = [c[i+1]['close'] - c[i]['close'] for i in range(-14, -1)]
            up = sum(d for d in diffs if d > 0)
            down = -sum(d for d in diffs if d < 0)
            if up + down == 0:
                return ('NEUTRAL', 0.0)
            rsi = 100 * (up / (up + down))
            if rsi > 65:
                return ('CALL', 0.7)
            if rsi < 35:
                return ('PUT', 0.7)
            return ('NEUTRAL', 0.0)

        def strat_open_close_gap(c):
            last = c[-1]
            rng = last.get('max', 0) - last.get('min', 0) if last.get('max') and last.get('min') else abs(last['close'] - last['open'])
            if rng == 0:
                return ('NEUTRAL', 0.0)
            body = abs(last['close'] - last['open'])
            if body / rng > 0.7:
                return ('CALL' if last['close'] > last['open'] else 'PUT', 0.65)
            return ('NEUTRAL', 0.0)

        def strat_moving_average_cross(c):
            if len(c) < 8:
                return ('NEUTRAL', 0.0)
            closes = [x['close'] for x in c]
            ma_fast = mean(closes[-3:])
            ma_slow = mean(closes[-8:])
            if ma_fast > ma_slow:
                return ('CALL', 0.6)
            if ma_fast < ma_slow:
                return ('PUT', 0.6)
            return ('NEUTRAL', 0.0)

        def strat_recent_volatility(c):
            if len(c) < 6:
                return ('NEUTRAL', 0.0)
            last = c[-1]
            prev = c[-2]
            move = last['close'] - last['open']
            prev_move = prev['close'] - prev['open']
            if abs(move) > abs(prev_move) * 1.8:
                return ('PUT' if move > 0 else 'CALL', 0.55)
            return ('NEUTRAL', 0.0)

        # Use advanced strategies if available, otherwise fall back to simple strategies
        if self.strategy_integrator is not None:
            try:
                # Use advanced strategy engine
                direction, confidence, breakdown = self.strategy_integrator.analyze_instrument(candles)

                # Convert to expected format
                if direction == 'NEUTRAL':
                    selected_signal = 'NEUTRAL'
                    selected_confidence = 0
                else:
                    selected_signal = direction
                    selected_confidence = int(confidence * 100)

                generation_time = (time.time() - start_time) * 1000

                return {
                    'signal': selected_signal,
                    'confidence': selected_confidence,
                    'instrument': instrument,
                    'timestamp': datetime.now().isoformat(),
                    'generation_time_ms': generation_time,
                    'strategy_breakdown': breakdown
                }
            except Exception as e:
                self.logger.error(f"Advanced strategy error: {e}", exc_info=True)
                # Fall through to simple strategies

        # Simple strategy fallback (original implementation)
        strategies = [
            strat_simple_candle_count,
        ]

        votes = {'CALL': 0.0, 'PUT': 0.0, 'NEUTRAL': 0.0}
        breakdown = []

        # Run strategies in parallel
        try:
            with ThreadPoolExecutor(max_workers=min(6, len(strategies))) as executor:
                futs = {executor.submit(s, candles): s.__name__ for s in strategies}
                timeout = ParallelTradingConfig.SIGNAL_GENERATION_TIMEOUT
                for f in as_completed(futs, timeout=timeout):
                    try:
                        vote, score = f.result()
                        votes[vote] += score
                        breakdown.append({'strategy': futs[f], 'vote': vote, 'score': score})
                    except Exception:
                        breakdown.append({'strategy': futs[f], 'vote': 'NEUTRAL', 'score': 0.0})
        except TimeoutError:
            pass
        except Exception:
            signals = ['CALL', 'PUT', 'NEUTRAL']
            weights = [0.45, 0.45, 0.10]
            choice = random.choices(signals, weights=weights)[0]
            confidence = random.randint(60, 95)
            generation_time = (time.time() - start_time) * 1000
            return {
                'signal': choice,
                'confidence': confidence,
                'instrument': instrument,
                'timestamp': datetime.now().isoformat(),
                'generation_time_ms': generation_time,
                'strategy_breakdown': [{'strategy': 'fallback_error', 'vote': choice, 'score': confidence}]
            }

        # Decide final vote
        call_score = votes['CALL']
        put_score = votes['PUT']
        neutral_score = votes['NEUTRAL']

        score_total = call_score + put_score
        if score_total <= 0:
            estimated_win_prob = 0.5
        else:
            estimated_win_prob = 0.5 + (call_score - put_score) / (2.0 * (score_total))
            estimated_win_prob = max(0.0, min(1.0, estimated_win_prob))

        try:
            inst_manager = self.portfolio_manager.get_instrument_manager(instrument)
            hist_stats = inst_manager.get_stats()
            hist_win_rate = hist_stats.get('win_rate', 0) / 100.0 if hist_stats.get('total_trades', 0) > 0 else None
        except Exception:
            hist_win_rate = None

        if hist_win_rate is not None:
            estimated_win_prob = estimated_win_prob * 0.7 + hist_win_rate * 0.3

        if context.min_required_win_rate is not None:
            safety_margin = 0.02
            required = context.min_required_win_rate + safety_margin
            meets_edge = estimated_win_prob >= required
        else:
            required = None
            meets_edge = True

        confidence = int(max(50, min(99, 50 + (abs(call_score - put_score) / (max(1.0, score_total + neutral_score))) * 49)))

        final_vote = 'NEUTRAL'
        tradeable = True
        if neutral_score >= (call_score + put_score) * 0.6:
            final_vote = 'NEUTRAL'
            tradeable = False
        else:
            final_vote = 'CALL' if call_score > put_score else 'PUT'
            if not meets_edge:
                tradeable = False

        if context.timing_risk:
            tradeable = False

        generation_time = (time.time() - start_time) * 1000

        return {
            'signal': final_vote,
            'confidence': confidence,
            'instrument': instrument,
            'timestamp': datetime.now().isoformat(),
            'generation_time_ms': generation_time,
            'strategy_breakdown': breakdown,
            'votes': votes,
            'estimated_win_prob': round(estimated_win_prob, 4),
            'payout_ratio': context.payout_ratio,
            'min_required_win_rate': round(required, 4) if required is not None else None,
            'tradeable': tradeable,
            'timing_risk': context.timing_risk,
            'rem_seconds': context.time_to_expiry_seconds
        }

    def calculate_position_size(self, instrument: str, confidence: float) -> float:
        """Calculate position size"""
        balance = self.portfolio_manager.state['current_balance']
        max_per_instrument = balance * (ParallelTradingConfig.MAX_RISK_PER_INSTRUMENT / 100)
        amount = max_per_instrument * (confidence / 100)
        amount = max(ParallelTradingConfig.MIN_TRADE_AMOUNT, amount)
        # Use Kelly sizing when enabled and instrument has calibration
        try:
            inst_manager = self.portfolio_manager.get_instrument_manager(instrument)
            inst_kelly = getattr(inst_manager.calibration, 'kelly_fraction', 0.0) or 0.0
        except Exception:
            inst_kelly = 0.0

        if ParallelTradingConfig.ENABLE_KELLY_SIZING and inst_kelly > 0:
            # conservative fraction of Kelly
            kelly_alloc = balance * inst_kelly * ParallelTradingConfig.KELLY_FRACTION
            # cap Kelly allocation
            kelly_alloc = min(kelly_alloc, ParallelTradingConfig.MAX_KELLY_POSITION)
            amount = max(amount, round(kelly_alloc, 2))

        # Optional Martingale sizing: increase stake after consecutive losses
        try:
            if ParallelTradingConfig.MARTINGALE_ENABLED:
                losses = 0
                try:
                    losses = int(getattr(self.portfolio_manager.get_instrument_manager(instrument), 'state', {}).get('consecutive_losses', 0) or 0)
                except Exception:
                    losses = 0

                if losses > 0:
                    doublings = min(losses, ParallelTradingConfig.MARTINGALE_MAX_DOUBLINGS)
                    multiplier = (ParallelTradingConfig.MARTINGALE_BASE_MULTIPLIER ** doublings)
                    self.logger.debug("Martingale multiplier for %s: losses=%s doublings=%s multiplier=%s", instrument, losses, doublings, multiplier)
                    amount = amount * multiplier
        except Exception:
            # If martingale logic fails, fall back to base amount
            pass

        # Enforce global caps
        amount = min(ParallelTradingConfig.MAX_TRADE_AMOUNT, amount)
        amount = round(amount, 2)
        return amount

    def execute_instrument_trade(self, instrument: str) -> Optional[Dict]:
        """Execute trade with minimal delay"""
        execution_start = time.time()
        
        try:
            inst_manager = self.portfolio_manager.get_instrument_manager(instrument)

            can_trade, reason = inst_manager.can_trade()
            if not can_trade:
                return None

            # Get binary option context first
            context = self.get_binary_option_context(instrument)

            # INSTANT signal generation
            ai_signal = self.get_ai_signal(instrument, context)
            if not ai_signal or ai_signal['signal'] == 'NEUTRAL':
                return None

            # Respect minimum AI confidence
            if ai_signal['confidence'] < ParallelTradingConfig.MIN_AI_CONFIDENCE:
                return None

            # Respect tradeable flag, timing risk, and minimum payout
            if not ai_signal.get('tradeable', True):
                self.logger.info(f"✋ Not tradeable for {instrument}: tradeable={ai_signal.get('tradeable')} timing_risk={ai_signal.get('timing_risk')}")
                return None

            payout = ai_signal.get('payout_ratio')
            if payout is not None:
                try:
                    if float(payout) < ParallelTradingConfig.MIN_PAYOUT_RATIO:
                        self.logger.info(f"✋ Skipping {instrument}: payout {payout:.2f} < min {ParallelTradingConfig.MIN_PAYOUT_RATIO:.2f}")
                        return None
                except Exception:
                    pass

            # Log strategy breakdown for auditing
            try:
                self.logger.debug(f"STRATEGY_BREAKDOWN [{instrument}]: win_prob={ai_signal.get('estimated_win_prob')} votes={ai_signal.get('votes')} breakdown={ai_signal.get('strategy_breakdown')}")
            except Exception:
                pass

            amount = self.calculate_position_size(instrument, ai_signal['confidence'])

            if not self.portfolio_manager.allocate_risk(instrument, amount):
                return None

            trade_id = f"{instrument}_{int(time.time()*1000)}"  # Millisecond precision
            inst_manager.start_trade(trade_id, payout_ratio=context.payout_ratio)

            # Determine which strategy contributed most to the final decision
            selected_strategy = None
            try:
                breakdown = ai_signal.get('strategy_breakdown') or []
                final_vote = ai_signal.get('signal')
                # Prefer the highest-scoring strategy that voted for the final direction
                candidates = [b for b in breakdown if b.get('vote') == final_vote]
                if candidates:
                    best = max(candidates, key=lambda x: x.get('score', 0))
                    selected_strategy = best.get('strategy')
                else:
                    # Fallback: pick highest score overall
                    if breakdown:
                        best = max(breakdown, key=lambda x: x.get('score', 0))
                        selected_strategy = best.get('strategy')
            except Exception:
                selected_strategy = None

            # Prepare trade entry for logging (DB)
            if self.trade_logger:
                try:
                    trade_entry = {
                        'trade_id': trade_id,
                        'instrument': instrument,
                        'direction': ai_signal.get('signal'),
                        'amount': amount,
                        'duration': ParallelTradingConfig.BINARY_OPTION_DURATION,
                        'payout_ratio': context.payout_ratio,
                        'entry_time': datetime.now().isoformat(),
                        'expiration_time': (datetime.now() + timedelta(seconds=ParallelTradingConfig.BINARY_OPTION_DURATION)).isoformat(),
                        'execution_time_ms': None,
                        'result': 'PENDING',
                        'profit': 0.0,
                        'entry_price': None,
                        'exit_price': None,
                        'price_change': None,
                        'mode': ParallelTradingConfig.TRADING_MODE,
                        'balance_before': self.portfolio_manager.state.get('current_balance'),
                        'balance_after': None,
                        'notes': None,
                        'selected_strategy': selected_strategy,
                        # store the breakdown as a native structure; DB manager will serialize as needed
                        'strategy_breakdown': ai_signal.get('strategy_breakdown', [])
                    }
                    self.trade_logger.log_trade_entry(trade_entry)
                except Exception:
                    pass

            # INSTANT EXECUTION - No delay
            action = ai_signal['signal'].lower()
            
            trade_entry_time = datetime.now()
            self.logger.info(f"⚡ INSTANT TRADE [{instrument}]: {ai_signal['signal']} ${amount} @ {ai_signal['confidence']}% | Entry: {trade_entry_time.strftime('%H:%M:%S.%f')[:-3]}")

            # Re-check expiry just before buy to avoid "buy late" failures
            try:
                remv = None
                if (self.api_client and hasattr(self.api_client, 'get_remaning')) or (self.api and hasattr(self.api, 'get_remaning')):
                    try:
                        remv = self.api_client.get_remaning(ParallelTradingConfig.BINARY_OPTION_DURATION) if self.api_client else self.api.get_remaning(ParallelTradingConfig.BINARY_OPTION_DURATION)
                    except Exception:
                        remv = None
                rem_check = None
                if remv is not None:
                    if isinstance(remv, (list, tuple)) and len(remv) > 0:
                        rem_check = int(remv[0])
                    else:
                        rem_check = int(remv)

                if rem_check is not None and rem_check < ParallelTradingConfig.EXPIRATION_BUFFER_SECONDS:
                    self.logger.warning(f"⚠️ Skipping {instrument}: remaining {rem_check}s < buffer {ParallelTradingConfig.EXPIRATION_BUFFER_SECONDS}s (avoid late buy)")
                    inst_manager.complete_trade(False, 0, 0)
                    self.portfolio_manager.release_risk(instrument, amount)
                    return None
            except Exception:
                # If unable to check remaining time, proceed but protect with a retry below
                rem_check = None

            # Attempt to buy; if it fails due to timing, perform one quick retry if timing still allows
            status = False
            order_id = None
            try:
                if self.api_client:
                    status, order_id = self.api_client.buy(amount, instrument, action, ParallelTradingConfig.BINARY_OPTION_DURATION)
                else:
                    status, order_id = self.api.buy(amount, instrument, action, ParallelTradingConfig.BINARY_OPTION_DURATION)
                if not status or order_id is None:
                    # quick re-check of remaining time and a single retry
                    try:
                        remv2 = None
                        if (self.api_client and hasattr(self.api_client, 'get_remaning')) or (self.api and hasattr(self.api, 'get_remaning')):
                            remv2 = self.api_client.get_remaning(ParallelTradingConfig.BINARY_OPTION_DURATION) if self.api_client else self.api.get_remaning(ParallelTradingConfig.BINARY_OPTION_DURATION)

                        if isinstance(remv2, (list, tuple)) and len(remv2) > 0:
                            rem2 = int(remv2[0])
                        else:
                            rem2 = int(remv2) if remv2 is not None else None
                    except Exception:
                        rem2 = None

                    if rem2 is None or rem2 >= ParallelTradingConfig.EXPIRATION_BUFFER_SECONDS:
                        time.sleep(0.12)
                        try:
                            if self.api_client:
                                status2, order_id2 = self.api_client.buy(amount, instrument, action, ParallelTradingConfig.BINARY_OPTION_DURATION)
                            else:
                                status2, order_id2 = self.api.buy(amount, instrument, action, ParallelTradingConfig.BINARY_OPTION_DURATION)

                            if status2 and order_id2:
                                status, order_id = status2, order_id2
                        except Exception as e:
                            self.logger.debug(f"Retry buy exception for {instrument}: {e}")

            except Exception as e:
                self.logger.error(f"❌ [{instrument}] buy error: {e}")
                status, order_id = False, None

            if not status or order_id is None:
                self.logger.error(f"❌ [{instrument}] Failed")
                inst_manager.complete_trade(False, 0, 0)
                self.portfolio_manager.release_risk(instrument, amount)
                return None

            execution_time_ms = int((time.time() - execution_start) * 1000)
            self.logger.info(f"✅ [{instrument}] Executed in {execution_time_ms}ms | Order: {order_id}")

            # Wait for result (optimized to 65 seconds)
            time.sleep(ParallelTradingConfig.WAIT_FOR_RESULT_SECONDS)

            # Check result
            profit = None
            for attempt in range(20):  # Reduced from 30 to 20
                try:
                    if self.api_client:
                        profit = self.api_client.check_win_v3(order_id)
                    else:
                        profit = self.api.check_win_v3(order_id)

                    if profit is not None:
                        break
                except Exception:
                    pass
                time.sleep(0.5)  # Reduced from 1 to 0.5 seconds

            if profit is None:
                self.logger.error(f"❌ [{instrument}] No result")
                inst_manager.complete_trade(False, 0, execution_time_ms)
                self.portfolio_manager.release_risk(instrument, amount)
                return None

            won = profit > 0
            result_str = "WIN" if won else "LOSS"

            inst_manager.complete_trade(won, profit, execution_time_ms)
            self.portfolio_manager.update_trade_result(profit, won)
            self.portfolio_manager.release_risk(instrument, amount)

            try:
                new_balance = self.api_client.get_balance() if self.api_client else self.api.get_balance()
            except Exception:
                new_balance = self.portfolio_manager.state.get('current_balance', ParallelTradingConfig.FICTITIOUS_START_BALANCE)
            self.portfolio_manager.state['current_balance'] = new_balance

            self.logger.info("="*80)
            self.logger.info(f"📈 RESULT [{instrument}]: {result_str} | P/L: ${profit:+.2f} | Exec: {execution_time_ms}ms")
            self.logger.info(f"   Balance: ${new_balance:.2f} | Daily: ${self.portfolio_manager.state['daily_profit'] - self.portfolio_manager.state['daily_loss']:+.2f}")
            self.logger.info("="*80)

            return {
                'instrument': instrument,
                'order_id': order_id,
                'action': action,
                'amount': amount,
                'profit': profit,
                'won': won,
                'execution_time_ms': execution_time_ms
            }

        except Exception as e:
            self.logger.error(f"❌ [{instrument}] Error: {e}")
            return None

    def parallel_trading_cycle(self):
        """Execute optimized parallel trading cycle"""
        cycle_start = time.time()

        try:
            # Check if trading is paused
            if self.portfolio_manager.state.get('paused', False):
                self.logger.debug("⏸️  Trading paused - skipping cycle")
                return

            if not self.check_connection_health():
                return

            can_trade, reason = self.portfolio_manager.can_trade_portfolio()
            if not can_trade:
                return

            available_instruments = self.get_available_instruments()
            if not available_instruments:
                return

            if len(available_instruments) > ParallelTradingConfig.MAX_INSTRUMENTS_TO_MONITOR:
                available_instruments = available_instruments[:ParallelTradingConfig.MAX_INSTRUMENTS_TO_MONITOR]

            self.logger.info(f"🔍 Scanning {len(available_instruments)} instruments...")

            # INSTANT parallel execution
            futures = []
            for instrument in available_instruments:
                can_trade, _ = self.portfolio_manager.can_trade_portfolio()
                if not can_trade:
                    break

                future = self.executor.submit(self.execute_instrument_trade, instrument)
                futures.append(future)

            completed = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        completed += 1
                except Exception as e:
                    self.logger.error(f"❌ Execution error: {e}")

            if completed > 0:
                cycle_time_ms = int((time.time() - cycle_start) * 1000)
                self.logger.info(f"✅ Completed {completed} trades | Cycle: {cycle_time_ms}ms")
                
                # Update performance metrics
                self.portfolio_manager.state['avg_scan_time_ms'] = cycle_time_ms

        except Exception as e:
            self.logger.error(f"❌ Cycle error: {e}")

    def trading_loop(self):
        """Optimized 24/7 trading loop"""
        self.logger.info("🔄 Starting optimized 24/7 loop...")
        self.portfolio_manager.state['running'] = True
        self.portfolio_manager.state['start_time'] = datetime.now()

        while self.running and not self.shutdown_requested:
            try:
                self.parallel_trading_cycle()

                # OPTIMIZED: Minimal wait (3 seconds)
                time.sleep(ParallelTradingConfig.INSTRUMENT_SCAN_INTERVAL)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"❌ Loop error: {e}")
                
                if ParallelTradingConfig.AUTO_RECONNECT_ON_FAILURE:
                    self.logger.info(f"🔄 Auto-recovery in {ParallelTradingConfig.RECONNECT_DELAY_SECONDS}s...")
                    time.sleep(ParallelTradingConfig.RECONNECT_DELAY_SECONDS)
                    self.connect_to_broker()
                else:
                    break

        self.logger.info("🛑 Trading loop stopped")
        self.portfolio_manager.state['running'] = False

    def start(self):
        """Start the optimized bot"""
        self.logger.info("🚀 Starting Optimized 24/7 Bot...")

        if not self.connect_to_broker():
            self.logger.error("❌ Failed to connect")
            return False

        self.print_configuration()
        self.running = True
        self.trading_loop()

        return True

    def stop(self):
        """Stop the bot"""
        self.logger.info("🛑 Stopping...")
        self.running = False
        self.shutdown_requested = True
        self.executor.shutdown(wait=True)

    def print_configuration(self):
        """Print configuration"""
        self.logger.info("="*80)
        self.logger.info("⚙️  OPTIMIZED CONFIGURATION")
        self.logger.info("="*80)
        self.logger.info(f"Mode: {ParallelTradingConfig.TRADING_MODE.upper()}")
        self.logger.info(f"⚡ INSTANT EXECUTION - Zero delay")
        self.logger.info(f"⚡ Scan Interval: {ParallelTradingConfig.INSTRUMENT_SCAN_INTERVAL}s (OPTIMIZED)")
        self.logger.info(f"⚡ Result Wait: {ParallelTradingConfig.WAIT_FOR_RESULT_SECONDS}s (OPTIMIZED)")
        self.logger.info(f"📊 Max Concurrent: {ParallelTradingConfig.MAX_CONCURRENT_INSTRUMENTS}")
        self.logger.info(f"🧵 Worker Threads: {ParallelTradingConfig.MAX_WORKER_THREADS}")
        self.logger.info("="*80)

    def get_statistics(self) -> Dict:
        """Get statistics"""
        stats = self.portfolio_manager.get_portfolio_stats()
        stats['status'] = 'running' if self.running else 'stopped'
        stats['mode'] = ParallelTradingConfig.TRADING_MODE
        stats['operation_mode'] = 'OPTIMIZED 24/7'

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

    @app.route('/recent_trades', methods=['GET'])
    def recent_trades():
        """Return recent trades including selected_strategy and breakdown"""
        limit = int(request.args.get('limit', 100))
        if bot.trade_logger and hasattr(bot.trade_logger, 'db'):
            try:
                trades = bot.trade_logger.db.get_recent_trades(limit)
                # Ensure JSON-serializable strategy_breakdown
                for t in trades:
                    if isinstance(t.get('strategy_breakdown'), str):
                        try:
                            t['strategy_breakdown'] = json.loads(t['strategy_breakdown'])
                        except Exception:
                            pass
                return jsonify({'trades': trades})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return jsonify({'error': 'database logging not available'}), 503

    @app.route('/strategy_stats', methods=['GET'])
    def strategy_stats():
        """Return aggregated stats by strategy"""
        limit = int(request.args.get('limit', 100))
        if bot.trade_logger and hasattr(bot.trade_logger, 'db'):
            try:
                stats = bot.trade_logger.db.get_strategy_stats(limit)
                return jsonify({'strategy_stats': stats})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return jsonify({'error': 'database logging not available'}), 503

    @app.route('/stop', methods=['POST'])
    def stop():
        bot.stop()
        return jsonify({'message': 'Shutdown initiated'})

    @app.route('/performance', methods=['GET'])
    def performance():
        """Return detailed performance metrics"""
        try:
            stats = bot.get_statistics()

            # Calculate additional metrics
            total_trades = stats.get('total_trades', 0)
            wins = stats.get('wins', 0)
            losses = stats.get('losses', 0)
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

            daily_pnl = stats.get('daily_pnl', 0)
            balance = stats.get('balance', 0)
            roi = (daily_pnl / 100 * 100) if balance > 0 else 0  # ROI based on $100 start

            performance_data = {
                'summary': {
                    'total_trades': total_trades,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': round(win_rate, 2),
                    'daily_pnl': round(daily_pnl, 2),
                    'roi_percent': round(roi, 2),
                    'balance': round(balance, 2)
                },
                'streaks': {
                    'current_win_streak': bot.portfolio_manager.state.get('win_streak', 0),
                    'current_loss_streak': bot.portfolio_manager.state.get('loss_streak', 0),
                    'best_win_streak': bot.portfolio_manager.state.get('best_win_streak', 0),
                    'worst_loss_streak': bot.portfolio_manager.state.get('worst_loss_streak', 0)
                },
                'limits': {
                    'max_daily_loss': ParallelTradingConfig.MAX_DAILY_LOSS,
                    'remaining_loss_budget': ParallelTradingConfig.MAX_DAILY_LOSS + daily_pnl,
                    'max_concurrent_instruments': ParallelTradingConfig.MAX_CONCURRENT_INSTRUMENTS
                },
                'timestamp': datetime.now().isoformat()
            }

            return jsonify(performance_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/active_trades', methods=['GET'])
    def active_trades():
        """Return currently active trades"""
        try:
            active = []
            for instrument in bot.portfolio_manager.state.get('active_instruments', []):
                active.append({
                    'instrument': instrument,
                    'entry_time': bot.portfolio_manager.state.get(f'{instrument}_entry_time', 'Unknown'),
                    'direction': bot.portfolio_manager.state.get(f'{instrument}_direction', 'Unknown'),
                    'amount': bot.portfolio_manager.state.get(f'{instrument}_amount', 0)
                })

            return jsonify({
                'active_count': len(active),
                'active_trades': active,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/config', methods=['GET'])
    def get_config():
        """Return current bot configuration"""
        config_data = {
            'trading': {
                'mode': ParallelTradingConfig.TRADING_MODE,
                'max_concurrent_instruments': ParallelTradingConfig.MAX_CONCURRENT_INSTRUMENTS,
                'max_daily_loss': ParallelTradingConfig.MAX_DAILY_LOSS,
                'instrument_scan_interval': ParallelTradingConfig.INSTRUMENT_SCAN_INTERVAL,
                'fictitious_balance_enabled': ParallelTradingConfig.ENABLE_FICTITIOUS_BALANCE,
                'fictitious_start_balance': ParallelTradingConfig.FICTITIOUS_START_BALANCE
            },
            'strategy': {
                'advanced_strategies_enabled': ADVANCED_STRATEGIES_AVAILABLE and bot.strategy_integrator is not None,
                'min_confidence': bot.strategy_integrator.config.min_confidence if bot.strategy_integrator else 'N/A',
                'min_confluence': bot.strategy_integrator.config.min_confluence if bot.strategy_integrator else 'N/A',
                'max_trade_amount': bot.strategy_integrator.config.max_trade_amount if bot.strategy_integrator else 'N/A',
                'enabled_strategies_count': len(bot.strategy_integrator.config.enabled_strategies) if bot.strategy_integrator else 0
            },
            'binary_options': {
                'min_payout_ratio': ParallelTradingConfig.MIN_PAYOUT_RATIO,
                'min_time_to_expiry_seconds': ParallelTradingConfig.MIN_TIME_TO_EXPIRY_SECONDS,
                'max_time_to_expiry_seconds': ParallelTradingConfig.MAX_TIME_TO_EXPIRY_SECONDS,
                'noise_threshold': ParallelTradingConfig.NOISE_THRESHOLD
            },
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(config_data)

    @app.route('/strategy_info', methods=['GET'])
    def strategy_info():
        """Return information about enabled strategies"""
        if not bot.strategy_integrator:
            return jsonify({'error': 'Advanced strategies not enabled'}), 404

        try:
            strategy_data = {
                'enabled': True,
                'risk_profile': os.getenv('STRATEGY_RISK_PROFILE', 'moderate'),
                'strategies': bot.strategy_integrator.config.enabled_strategies,
                'config': {
                    'min_confidence': bot.strategy_integrator.config.min_confidence,
                    'min_confluence': bot.strategy_integrator.config.min_confluence,
                    'max_trade_amount': bot.strategy_integrator.config.max_trade_amount,
                    'min_trade_amount': bot.strategy_integrator.config.min_trade_amount,
                    'max_daily_loss': bot.strategy_integrator.config.max_daily_loss,
                    'max_concurrent_trades': bot.strategy_integrator.config.max_concurrent_trades
                },
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(strategy_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/pause', methods=['POST'])
    def pause_trading():
        """Pause trading (stop taking new trades but let active ones finish)"""
        try:
            bot.portfolio_manager.state['paused'] = True
            return jsonify({
                'status': 'paused',
                'message': 'Trading paused. Active trades will complete.',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/resume', methods=['POST'])
    def resume_trading():
        """Resume trading after pause"""
        try:
            bot.portfolio_manager.state['paused'] = False
            return jsonify({
                'status': 'active',
                'message': 'Trading resumed.',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        """Serve a simple HTML dashboard"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KAEL Trading Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child { border-bottom: none; }
        .metric-label {
            font-weight: 500;
            color: #666;
        }
        .metric-value {
            font-weight: bold;
            color: #333;
        }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .neutral { color: #6b7280; }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .status-active {
            background: #d1fae5;
            color: #065f46;
        }
        .status-paused {
            background: #fef3c7;
            color: #92400e;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            margin: 5px;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
        }
        .btn-warning {
            background: #f59e0b;
            color: white;
        }
        .btn-warning:hover {
            background: #d97706;
        }
        .btn-success {
            background: #10b981;
            color: white;
        }
        .btn-success:hover {
            background: #059669;
        }
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        .btn-danger:hover {
            background: #dc2626;
        }
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        .trades-table {
            width: 100%;
            margin-top: 15px;
            border-collapse: collapse;
        }
        .trades-table th {
            background: #f3f4f6;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }
        .trades-table td {
            padding: 10px;
            border-bottom: 1px solid #e5e7eb;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 KAEL Trading Bot Dashboard</h1>

        <div class="grid">
            <!-- Status Card -->
            <div class="card">
                <h2>📊 Status</h2>
                <div class="metric">
                    <span class="metric-label">Bot Status:</span>
                    <span id="bot-status" class="status-badge status-active">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Trading Mode:</span>
                    <span id="trading-mode" class="metric-value">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Updated:</span>
                    <span id="last-updated" class="metric-value neutral">-</span>
                </div>
            </div>

            <!-- Performance Card -->
            <div class="card">
                <h2>💰 Performance</h2>
                <div class="metric">
                    <span class="metric-label">Balance:</span>
                    <span id="balance" class="metric-value">$-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Daily P&L:</span>
                    <span id="daily-pnl" class="metric-value">$-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">ROI:</span>
                    <span id="roi" class="metric-value">-%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Win Rate:</span>
                    <span id="win-rate" class="metric-value">-%</span>
                </div>
            </div>

            <!-- Trades Card -->
            <div class="card">
                <h2>📈 Trades</h2>
                <div class="metric">
                    <span class="metric-label">Total Trades:</span>
                    <span id="total-trades" class="metric-value">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Wins:</span>
                    <span id="wins" class="metric-value positive">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Losses:</span>
                    <span id="losses" class="metric-value negative">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Trades:</span>
                    <span id="active-trades" class="metric-value">-</span>
                </div>
            </div>

            <!-- Strategy Card -->
            <div class="card">
                <h2>🎯 Strategy</h2>
                <div class="metric">
                    <span class="metric-label">Advanced Strategies:</span>
                    <span id="strategies-enabled" class="metric-value">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Min Confidence:</span>
                    <span id="min-confidence" class="metric-value">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Min Confluence:</span>
                    <span id="min-confluence" class="metric-value">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Max Trade Amount:</span>
                    <span id="max-trade-amount" class="metric-value">$-</span>
                </div>
            </div>
        </div>

        <!-- Recent Trades -->
        <div class="card">
            <h2>📋 Recent Trades (Last 10)</h2>
            <div id="recent-trades-container">
                <div class="loading">
                    <div class="spinner"></div>
                    Loading trades...
                </div>
            </div>
        </div>

        <!-- Controls -->
        <div class="card controls">
            <h2>🎮 Controls</h2>
            <button class="btn btn-success" onclick="resumeTrading()">▶️ Resume Trading</button>
            <button class="btn btn-warning" onclick="pauseTrading()">⏸️ Pause Trading</button>
            <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh Data</button>
            <button class="btn btn-danger" onclick="stopBot()">⏹️ Stop Bot</button>
        </div>
    </div>

    <script>
        let autoRefreshInterval;

        async function fetchData(endpoint) {
            try {
                const response = await fetch(endpoint);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return await response.json();
            } catch (error) {
                console.error(`Error fetching ${endpoint}:`, error);
                return null;
            }
        }

        async function updateDashboard() {
            const [performance, config, activeTrades, recentTrades] = await Promise.all([
                fetchData('/performance'),
                fetchData('/config'),
                fetchData('/active_trades'),
                fetchData('/recent_trades?limit=10')
            ]);

            if (performance) {
                document.getElementById('balance').textContent = `$${performance.summary.balance}`;
                const pnl = performance.summary.daily_pnl;
                const pnlElement = document.getElementById('daily-pnl');
                pnlElement.textContent = `$${pnl >= 0 ? '+' : ''}${pnl}`;
                pnlElement.className = pnl >= 0 ? 'metric-value positive' : 'metric-value negative';

                const roi = performance.summary.roi_percent;
                const roiElement = document.getElementById('roi');
                roiElement.textContent = `${roi >= 0 ? '+' : ''}${roi}%`;
                roiElement.className = roi >= 0 ? 'metric-value positive' : 'metric-value negative';

                document.getElementById('win-rate').textContent = `${performance.summary.win_rate}%`;
                document.getElementById('total-trades').textContent = performance.summary.total_trades;
                document.getElementById('wins').textContent = performance.summary.wins;
                document.getElementById('losses').textContent = performance.summary.losses;
            }

            if (config) {
                document.getElementById('trading-mode').textContent = config.trading.mode.toUpperCase();
                document.getElementById('strategies-enabled').textContent =
                    config.strategy.advanced_strategies_enabled ? '✅ Enabled' : '❌ Disabled';
                document.getElementById('min-confidence').textContent =
                    config.strategy.min_confidence !== 'N/A' ? `${(config.strategy.min_confidence * 100).toFixed(0)}%` : 'N/A';
                document.getElementById('min-confluence').textContent =
                    config.strategy.min_confluence !== 'N/A' ? `${config.strategy.min_confluence} strategies` : 'N/A';
                document.getElementById('max-trade-amount').textContent =
                    config.strategy.max_trade_amount !== 'N/A' ? `$${config.strategy.max_trade_amount}` : 'N/A';
            }

            if (activeTrades) {
                document.getElementById('active-trades').textContent = activeTrades.active_count;
            }

            if (recentTrades && recentTrades.trades) {
                displayRecentTrades(recentTrades.trades);
            }

            document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
            document.getElementById('bot-status').textContent = 'Active';
        }

        function displayRecentTrades(trades) {
            const container = document.getElementById('recent-trades-container');
            if (!trades || trades.length === 0) {
                container.innerHTML = '<p class="loading">No trades yet</p>';
                return;
            }

            const table = `
                <table class="trades-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Instrument</th>
                            <th>Direction</th>
                            <th>Amount</th>
                            <th>Result</th>
                            <th>P&L</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${trades.map(trade => `
                            <tr>
                                <td>${new Date(trade.entry_time).toLocaleTimeString()}</td>
                                <td>${trade.instrument}</td>
                                <td>${trade.direction}</td>
                                <td>$${trade.amount}</td>
                                <td class="${trade.result === 'win' ? 'positive' : 'negative'}">${trade.result.toUpperCase()}</td>
                                <td class="${trade.pnl >= 0 ? 'positive' : 'negative'}">$${trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            container.innerHTML = table;
        }

        async function pauseTrading() {
            const response = await fetch('/pause', { method: 'POST' });
            const data = await response.json();
            alert(data.message || 'Trading paused');
            updateDashboard();
        }

        async function resumeTrading() {
            const response = await fetch('/resume', { method: 'POST' });
            const data = await response.json();
            alert(data.message || 'Trading resumed');
            updateDashboard();
        }

        async function stopBot() {
            if (!confirm('Are you sure you want to stop the bot? This will shut down the system.')) return;
            const response = await fetch('/stop', { method: 'POST' });
            const data = await response.json();
            alert(data.message || 'Bot stopped');
        }

        function refreshData() {
            updateDashboard();
        }

        function startAutoRefresh() {
            autoRefreshInterval = setInterval(updateDashboard, 5000); // Refresh every 5 seconds
        }

        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
            }
        }

        // Initial load
        updateDashboard();
        startAutoRefresh();

        // Stop auto-refresh when page is hidden (saves resources)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopAutoRefresh();
            } else {
                startAutoRefresh();
            }
        });
    </script>
</body>
</html>
        """
        return html

    return app


def start_health_server(app: Flask, logger: logging.Logger):
    """Start the health API using a production server when possible.

    Prefer waitress if installed, otherwise fallback to Flask's threaded server.
    """
    try:
        # Prefer waitress (lightweight and production-ready for WSGI)
        import waitress  # type: ignore
        logger.info("ℹ️  Starting health API with waitress")
        waitress.serve(app, host='0.0.0.0', port=ParallelTradingConfig.HEALTH_API_PORT)
        return
    except Exception:
        logger.debug("waitress not available, falling back to Flask development server")

    # Fallback: use threaded Flask server but log a clear warning
    logger.warning("⚠️  Health API running with Flask's built-in server. For production, run with waitress/gunicorn.")
    app.run(host='0.0.0.0', port=ParallelTradingConfig.HEALTH_API_PORT, debug=False, use_reloader=False, threaded=True)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    logger = setup_logging()

    logger.info("="*80)
    logger.info("⚡ OPTIMIZED 24/7 PARALLEL TRADING BOT - INSTANT EXECUTION")
    logger.info("="*80)
    logger.info(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {ParallelTradingConfig.TRADING_MODE.upper()}")
    logger.info("⚡ ZERO-DELAY EXECUTION FOR ACCURATE TECHNICAL ANALYSIS")
    logger.info("="*80)

    if not ParallelTradingConfig.EMAIL or not ParallelTradingConfig.PASSWORD:
        logger.error("❌ No credentials")
        return 1

    if ParallelTradingConfig.TRADING_MODE == 'live':
        logger.warning("="*80)
        logger.warning("⚠️  LIVE MODE - REAL MONEY")
        logger.warning("="*80)
        time.sleep(3)

    bot = ParallelTradingBot(logger)

    if ParallelTradingConfig.ENABLE_HEALTH_API:
        health_app = create_health_api(bot)
        health_thread = threading.Thread(
            target=lambda: start_health_server(health_app, logger),
            daemon=True
        )
        health_thread.start()
        logger.info(f"🏥 Health API: http://localhost:{ParallelTradingConfig.HEALTH_API_PORT}")

    try:
        bot.start()
    except Exception as e:
        logger.error(f"❌ Fatal: {e}")
        return 1
    finally:
        logger.info("="*80)
        logger.info("🏁 SHUTDOWN")
        logger.info("="*80)

        stats = bot.get_statistics()
        for key, value in stats.items():
            if key != 'instrument_stats':
                logger.info(f"{key}: {value}")

    return 0


if __name__ == '__main__':
    sys.exit(main())