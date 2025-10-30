#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ULTIMATE BINARY OPTION STRATEGY EVALUATOR
Production-Ready System for Comprehensive Strategy Performance Measurement

UNIFIED ARCHITECTURE combining best features from:
- Multi-Instrument Parallel Bot (Advanced risk management)
- Strategy-Per-Thread Bot (Strategy isolation)
- Multi-Account Bot (Comprehensive analytics)

Features:
✅ 10+ Binary Option Strategies running concurrently
✅ Advanced Risk Management (Kelly Criterion, Sharpe Ratio, Dynamic Calibration)
✅ Per-Strategy Performance Tracking & Comparison
✅ Payout-Aware Position Sizing
✅ Fictitious $100 Balance for Realistic Testing
✅ TimescaleDB Integration for Time-Series Data
✅ Comprehensive Analytics & Visualization
✅ CSV/Excel Export for Data Analysis
✅ RESTful API with Real-Time Metrics
✅ Prometheus + Grafana Integration
✅ Weekly Performance Summaries

GOAL: Measure and compare 10+ strategies to identify the best performing ones
"""

import sys
import os
import time
import logging
import signal
import traceback
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Set
import threading
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from collections import deque
import queue
import statistics
import numpy as np

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

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

# Advanced strategy system
USE_ADVANCED_STRATEGIES = os.getenv('USE_ADVANCED_STRATEGIES', 'true').lower() == 'true'
try:
    if USE_ADVANCED_STRATEGIES:
        from strategies.advanced_strategies import AdvancedStrategyEngine, StrategySignal
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

# Strategy-specific metrics (per strategy)
prometheus_strategy_trades = Counter('kael_strategy_total_trades', 'Total trades per strategy', ['strategy'])
prometheus_strategy_wins = Counter('kael_strategy_wins', 'Winning trades per strategy', ['strategy'])
prometheus_strategy_losses = Counter('kael_strategy_losses', 'Losing trades per strategy', ['strategy'])
prometheus_strategy_win_rate = Gauge('kael_strategy_win_rate', 'Win rate per strategy', ['strategy'])
prometheus_strategy_pnl = Gauge('kael_strategy_total_pnl', 'Total P&L per strategy', ['strategy'])
prometheus_strategy_confidence = Gauge('kael_strategy_avg_confidence', 'Average confidence per strategy', ['strategy'])
prometheus_strategy_sharpe = Gauge('kael_strategy_sharpe_ratio', 'Sharpe ratio per strategy', ['strategy'])
prometheus_strategy_kelly = Gauge('kael_strategy_kelly_fraction', 'Kelly fraction per strategy', ['strategy'])

# Portfolio metrics
prometheus_portfolio_balance = Gauge('kael_portfolio_balance', 'Total portfolio balance')
prometheus_portfolio_pnl = Gauge('kael_portfolio_daily_pnl', 'Total daily P&L')
prometheus_portfolio_win_rate = Gauge('kael_portfolio_win_rate', 'Overall portfolio win rate')
prometheus_active_strategies = Gauge('kael_active_strategies', 'Number of active strategies')
prometheus_total_trades = Counter('kael_total_trades', 'Total trades across all strategies')

# Risk metrics
prometheus_max_drawdown = Gauge('kael_max_drawdown', 'Maximum drawdown percentage')
prometheus_risk_budget_remaining = Gauge('kael_risk_budget_remaining', 'Remaining daily risk budget')

# Performance metrics
prometheus_execution_time = Histogram('kael_trade_execution_time_ms', 'Trade execution time in milliseconds',
                                      buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000])


# =============================================================================
# BINARY OPTION CALCULATOR (from Multi-Instrument Bot)
# =============================================================================

class BinaryOptionCalculator:
    """Advanced calculations for binary options"""

    @staticmethod
    def calculate_breakeven_win_rate(payout_ratio: float) -> float:
        """Calculate breakeven win rate for given payout"""
        if payout_ratio <= 0:
            return 1.0
        return 1.0 / (1.0 + payout_ratio)

    @staticmethod
    def calculate_required_win_rate(payout_ratio: float, safety_margin: float = 0.02) -> float:
        """Calculate required win rate with safety margin"""
        breakeven = BinaryOptionCalculator.calculate_breakeven_win_rate(payout_ratio)
        return breakeven + safety_margin

    @staticmethod
    def calculate_expected_value(win_rate: float, payout_ratio: float, amount: float = 1.0) -> float:
        """Calculate expected value of a trade"""
        win_profit = amount * payout_ratio
        loss = amount
        ev = (win_rate * win_profit) - ((1 - win_rate) * loss)
        return ev

    @staticmethod
    def calculate_kelly_fraction(win_rate: float, payout_ratio: float) -> float:
        """Calculate Kelly Criterion optimal bet size"""
        if payout_ratio <= 0 or win_rate <= 0:
            return 0.0

        q = 1 - win_rate
        kelly = (win_rate * payout_ratio - q) / payout_ratio

        # Cap Kelly at 25% for safety
        return max(0.0, min(kelly, 0.25))

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return 0.0

        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return
        return sharpe


# =============================================================================
# STRATEGY STATE MANAGER (Enhanced from Multi-Instrument Bot)
# =============================================================================

@dataclass
class StrategyMetrics:
    """Performance metrics for a single strategy"""
    strategy_name: str
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    avg_confidence: float = 0.0
    avg_payout: float = 0.0
    sharpe_ratio: float = 0.0
    kelly_fraction: float = 0.0
    max_consecutive_losses: int = 0
    current_streak: int = 0  # Positive = wins, Negative = losses

    # Trade history
    profit_history: deque = field(default_factory=lambda: deque(maxlen=100))
    confidence_history: deque = field(default_factory=lambda: deque(maxlen=100))
    payout_history: deque = field(default_factory=lambda: deque(maxlen=100))

    # Calibration
    confidence_multiplier: float = 1.0
    last_calibration: datetime = field(default_factory=datetime.now)

    def update(self, won: bool, profit: float, confidence: float, payout_ratio: float):
        """Update metrics after a trade"""
        self.total_trades += 1

        if won:
            self.wins += 1
            self.current_streak = max(0, self.current_streak) + 1
        else:
            self.losses += 1
            self.current_streak = min(0, self.current_streak) - 1
            self.max_consecutive_losses = max(self.max_consecutive_losses, abs(self.current_streak))

        self.win_rate = self.wins / self.total_trades if self.total_trades > 0 else 0.0
        self.total_pnl += profit

        self.profit_history.append(profit)
        self.confidence_history.append(confidence)
        self.payout_history.append(payout_ratio)

        # Update averages
        if self.confidence_history:
            self.avg_confidence = statistics.mean(self.confidence_history)
        if self.payout_history:
            self.avg_payout = statistics.mean(self.payout_history)

        # Calculate Sharpe ratio
        if len(self.profit_history) >= 2:
            self.sharpe_ratio = BinaryOptionCalculator.calculate_sharpe_ratio(list(self.profit_history))

        # Calculate Kelly fraction
        if self.avg_payout > 0:
            self.kelly_fraction = BinaryOptionCalculator.calculate_kelly_fraction(self.win_rate, self.avg_payout)

    def should_recalibrate(self) -> bool:
        """Check if strategy needs recalibration"""
        time_since = datetime.now() - self.last_calibration
        return (self.total_trades >= 20 and time_since.total_seconds() > 3600) or self.total_trades >= 50

    def recalibrate(self):
        """Adjust confidence multiplier based on performance"""
        if self.total_trades < 10:
            return

        # If win rate is low, increase confidence threshold (more selective)
        if self.win_rate < 0.55:
            self.confidence_multiplier = min(1.2, self.confidence_multiplier * 1.05)
        # If win rate is high, can be slightly less selective
        elif self.win_rate > 0.70:
            self.confidence_multiplier = max(0.9, self.confidence_multiplier * 0.98)

        self.last_calibration = datetime.now()
        logging.getLogger(self.strategy_name).info(
            f"📊 Recalibrated: confidence_multiplier={self.confidence_multiplier:.2f}, "
            f"win_rate={self.win_rate:.1%}, trades={self.total_trades}"
        )

    def get_stats(self) -> Dict:
        """Get strategy statistics"""
        return {
            'strategy_name': self.strategy_name,
            'total_trades': self.total_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': round(self.win_rate * 100, 2),
            'total_pnl': round(self.total_pnl, 2),
            'avg_confidence': round(self.avg_confidence * 100, 2),
            'avg_payout': round(self.avg_payout, 4),
            'sharpe_ratio': round(self.sharpe_ratio, 3),
            'kelly_fraction': round(self.kelly_fraction, 4),
            'max_consecutive_losses': self.max_consecutive_losses,
            'current_streak': self.current_streak,
            'confidence_multiplier': round(self.confidence_multiplier, 3)
        }


# =============================================================================
# PORTFOLIO STATE MANAGER (from Multi-Instrument Bot)
# =============================================================================

class PortfolioStateManager:
    """Manages portfolio-wide state and risk"""

    def __init__(self, initial_balance: float = 100.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.peak_balance = initial_balance
        self.daily_pnl = 0.0
        self.total_trades = 0
        self.total_wins = 0
        self.total_losses = 0

        # Risk management
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', 10.0))
        self.daily_loss_reached = False
        self.risk_budget_used = 0.0

        # Strategy metrics
        self.strategy_metrics: Dict[str, StrategyMetrics] = {}

        # Thread safety
        self.lock = threading.Lock()

    def get_strategy_metrics(self, strategy_name: str) -> StrategyMetrics:
        """Get or create strategy metrics"""
        with self.lock:
            if strategy_name not in self.strategy_metrics:
                self.strategy_metrics[strategy_name] = StrategyMetrics(strategy_name)
            return self.strategy_metrics[strategy_name]

    def can_trade(self) -> Tuple[bool, str]:
        """Check if portfolio can trade"""
        with self.lock:
            if self.daily_loss_reached:
                return False, "Daily loss limit reached"

            if abs(self.daily_pnl) >= self.max_daily_loss and self.daily_pnl < 0:
                self.daily_loss_reached = True
                return False, f"Daily loss limit reached: ${self.daily_pnl:.2f}"

            if self.current_balance < 50:
                return False, "Insufficient balance"

            return True, "OK"

    def update_trade_result(self, strategy_name: str, won: bool, profit: float,
                           confidence: float, payout_ratio: float):
        """Update portfolio after trade"""
        with self.lock:
            # Update portfolio
            self.current_balance += profit
            self.daily_pnl += profit
            self.total_trades += 1

            if won:
                self.total_wins += 1
            else:
                self.total_losses += 1

            # Update peak for drawdown calculation
            if self.current_balance > self.peak_balance:
                self.peak_balance = self.current_balance

            # Update strategy metrics
            metrics = self.get_strategy_metrics(strategy_name)
            metrics.update(won, profit, confidence, payout_ratio)

            # Recalibrate if needed
            if metrics.should_recalibrate():
                metrics.recalibrate()

            # Update Prometheus metrics
            prometheus_strategy_trades.labels(strategy=strategy_name).inc()
            if won:
                prometheus_strategy_wins.labels(strategy=strategy_name).inc()
            else:
                prometheus_strategy_losses.labels(strategy=strategy_name).inc()

            if metrics.total_trades > 0:
                prometheus_strategy_win_rate.labels(strategy=strategy_name).set(metrics.win_rate * 100)
            prometheus_strategy_pnl.labels(strategy=strategy_name).set(metrics.total_pnl)
            prometheus_strategy_confidence.labels(strategy=strategy_name).set(metrics.avg_confidence * 100)
            prometheus_strategy_sharpe.labels(strategy=strategy_name).set(metrics.sharpe_ratio)
            prometheus_strategy_kelly.labels(strategy=strategy_name).set(metrics.kelly_fraction)

            prometheus_portfolio_balance.set(self.current_balance)
            prometheus_portfolio_pnl.set(self.daily_pnl)
            prometheus_total_trades.inc()

            # Calculate portfolio win rate
            if self.total_trades > 0:
                portfolio_wr = (self.total_wins / self.total_trades) * 100
                prometheus_portfolio_win_rate.set(portfolio_wr)

            # Calculate max drawdown
            if self.peak_balance > 0:
                drawdown = ((self.peak_balance - self.current_balance) / self.peak_balance) * 100
                prometheus_max_drawdown.set(drawdown)

    def get_portfolio_stats(self) -> Dict:
        """Get portfolio statistics"""
        with self.lock:
            win_rate = (self.total_wins / self.total_trades * 100) if self.total_trades > 0 else 0.0
            roi = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
            drawdown = ((self.peak_balance - self.current_balance) / self.peak_balance) * 100 if self.peak_balance > 0 else 0.0

            return {
                'initial_balance': self.initial_balance,
                'current_balance': round(self.current_balance, 2),
                'daily_pnl': round(self.daily_pnl, 2),
                'roi': round(roi, 2),
                'max_drawdown': round(drawdown, 2),
                'total_trades': self.total_trades,
                'total_wins': self.total_wins,
                'total_losses': self.total_losses,
                'portfolio_win_rate': round(win_rate, 2),
                'active_strategies': len(self.strategy_metrics),
                'strategies': {name: metrics.get_stats() for name, metrics in self.strategy_metrics.items()}
            }

    def reset_daily_stats(self):
        """Reset daily statistics"""
        with self.lock:
            self.daily_pnl = 0.0
            self.daily_loss_reached = False
            self.risk_budget_used = 0.0


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
# CONFIGURATION
# =============================================================================

class UltimateEvaluatorConfig:
    """Configuration for ultimate strategy evaluator"""

    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'demo')

    # Fictitious Balance (for realistic testing)
    ENABLE_FICTITIOUS_BALANCE = bool(os.getenv('ENABLE_FICTITIOUS_BALANCE', True))
    FICTITIOUS_START_BALANCE = float(os.getenv('FICTITIOUS_START_BALANCE', 100.0))

    # Strategy Settings
    STRATEGY_SCAN_INTERVAL = int(os.getenv('STRATEGY_SCAN_INTERVAL', 5))
    MIN_CONFIDENCE_BASE = float(os.getenv('MIN_CONFIDENCE_BASE', 0.70))

    # Binary Options Settings
    BINARY_OPTION_DURATION = 1
    BASE_TRADE_AMOUNT = float(os.getenv('BASE_TRADE_AMOUNT', 1.0))
    MIN_PAYOUT_RATIO = float(os.getenv('MIN_PAYOUT_RATIO', 0.65))

    # Trading Assets
    INSTRUMENT_POOL = os.getenv('TRADING_ASSETS',
        'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,AUDJPY'
    ).split(',')

    # Risk Management
    MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', 5))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 10.0))
    MIN_BALANCE = float(os.getenv('MIN_BALANCE', 50))
    MIN_SECONDS_BETWEEN_TRADES = int(os.getenv('MIN_SECONDS_BETWEEN_TRADES', 70))

    # Timing
    WAIT_FOR_RESULT_SECONDS = int(os.getenv('WAIT_FOR_RESULT_SECONDS', 65))

    # API rate limiting
    API_MIN_INTERVAL = float(os.getenv('API_MIN_INTERVAL', 0.3))
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', 3))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = Path('logs')

    # Health API
    ENABLE_HEALTH_API = bool(os.getenv('ENABLE_HEALTH_API', True))
    HEALTH_API_PORT = int(os.getenv('HEALTH_API_PORT', 5001))

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kael')

    # 7 Strategies to Evaluate (implemented in AdvancedStrategyEngine)
    STRATEGIES_TO_EVALUATE = [
        'enhanced_candle_count',
        'rsi_divergence',
        'macd_momentum',
        'bollinger_rsi_combo',
        'stochastic',
        'support_resistance',
        'trend_alignment',
        # Note: The following strategies are not yet implemented in AdvancedStrategyEngine
        # 'ema_crossover',
        # 'volume_analysis',
        # 'price_action_patterns'
    ]


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure comprehensive logging"""
    UltimateEvaluatorConfig.LOG_DIR.mkdir(exist_ok=True)

    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(
        UltimateEvaluatorConfig.LOG_DIR / f'ultimate_evaluator_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    console_handler.setLevel(getattr(logging, UltimateEvaluatorConfig.LOG_LEVEL))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger(__name__)


# =============================================================================
# STRATEGY EVALUATOR THREAD
# =============================================================================

class StrategyEvaluatorThread:
    """Dedicated thread for evaluating a single strategy"""

    def __init__(self, strategy_name: str, api_client: ApiClient,
                 portfolio_manager: PortfolioStateManager,
                 db_logger, logger: logging.Logger):
        self.strategy_name = strategy_name
        self.api_client = api_client
        self.portfolio = portfolio_manager
        self.db_logger = db_logger
        self.logger = logging.getLogger(f"Strategy-{strategy_name}")

        # Strategy engine
        self.strategy_engine = AdvancedStrategyEngine() if ADVANCED_STRATEGIES_AVAILABLE else None

        # Thread control
        self.running = False
        self.thread = None
        self.last_trade_time = 0

        # Statistics
        self.trades_today = 0
        self.consecutive_losses = 0

    def get_available_instruments(self) -> List[str]:
        """Get available trading instruments"""
        try:
            open_markets = self.api_client.get_all_open_time()
            if not open_markets or 'binary' not in open_markets:
                return []

            binary_markets = open_markets['binary']
            available = []

            for inst in UltimateEvaluatorConfig.INSTRUMENT_POOL:
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

    def analyze_instrument(self, instrument: str) -> Optional[Tuple[str, float, List, float]]:
        """Analyze instrument with this strategy"""
        try:
            # Get candles
            candles = self.api_client.get_candles(instrument, 60, 100, time.time())
            if not candles or len(candles) < 50:
                return None

            # Analyze with strategy engine
            if not self.strategy_engine:
                return None

            # Convert to numpy arrays for specific strategy methods
            closes = np.array([c['close'] for c in candles], dtype=float)
            opens = np.array([c['open'] for c in candles], dtype=float)
            highs = np.array([c.get('max', c['close']) for c in candles], dtype=float)
            lows = np.array([c.get('min', c['close']) for c in candles], dtype=float)
            volumes = np.array([c.get('volume', 0) for c in candles], dtype=float)

            # Call specific strategy method based on strategy name
            signal = None
            if self.strategy_name == 'enhanced_candle_count':
                signal = self.strategy_engine.enhanced_candle_count(candles, closes, opens)
            elif self.strategy_name == 'rsi_divergence':
                signal = self.strategy_engine.rsi_divergence_strategy(closes, highs, lows)
            elif self.strategy_name == 'macd_momentum':
                signal = self.strategy_engine.macd_momentum_strategy(closes)
            elif self.strategy_name == 'bollinger_rsi_combo':
                signal = self.strategy_engine.bollinger_rsi_combo(closes)
            elif self.strategy_name == 'stochastic':
                signal = self.strategy_engine.stochastic_strategy(highs, lows, closes)
            elif self.strategy_name == 'support_resistance':
                signal = self.strategy_engine.support_resistance_strategy(highs, lows, closes)
            elif self.strategy_name == 'trend_alignment':
                signal = self.strategy_engine.trend_alignment_strategy(closes)
            else:
                self.logger.warning(f"Strategy {self.strategy_name} not implemented")
                return None

            if not signal or signal.direction == 'NEUTRAL':
                return None

            # Get strategy metrics for calibration
            metrics = self.portfolio.get_strategy_metrics(self.strategy_name)

            # Apply confidence multiplier from calibration
            adjusted_confidence = signal.confidence * metrics.confidence_multiplier

            # Check confidence threshold
            if adjusted_confidence < UltimateEvaluatorConfig.MIN_CONFIDENCE_BASE:
                return None

            # Get payout ratio
            payouts = self.api_client.get_all_profit()
            if not payouts or instrument not in payouts:
                return None

            payout_ratio = payouts[instrument].get('turbo', 0.80)

            # Check payout threshold
            if payout_ratio < UltimateEvaluatorConfig.MIN_PAYOUT_RATIO:
                return None

            return signal.direction, adjusted_confidence, signal.reasons, payout_ratio

        except Exception as e:
            self.logger.error(f"Analysis error for {instrument}: {e}")
            return None

    def can_trade(self) -> bool:
        """Check if strategy can trade"""
        # Check portfolio-wide limits
        can_trade, reason = self.portfolio.can_trade()
        if not can_trade:
            return False

        # Check consecutive losses
        if self.consecutive_losses >= UltimateEvaluatorConfig.MAX_CONSECUTIVE_LOSSES:
            return False

        # Check time between trades
        time_since_last = time.time() - self.last_trade_time
        if time_since_last < UltimateEvaluatorConfig.MIN_SECONDS_BETWEEN_TRADES:
            return False

        return True

    def execute_trade(self, instrument: str, direction: str, confidence: float,
                     reasons: List[str], payout_ratio: float) -> Optional[Dict]:
        """Execute a single trade"""
        start_time = time.time()

        try:
            # Get strategy metrics for Kelly-based position sizing
            metrics = self.portfolio.get_strategy_metrics(self.strategy_name)

            # Calculate trade amount using Kelly criterion if available
            if metrics.kelly_fraction > 0 and metrics.total_trades >= 10:
                kelly_amount = self.portfolio.current_balance * metrics.kelly_fraction
                # Cap at base amount and use fractional Kelly (25% of full Kelly)
                amount = min(UltimateEvaluatorConfig.BASE_TRADE_AMOUNT, kelly_amount * 0.25)
            else:
                amount = UltimateEvaluatorConfig.BASE_TRADE_AMOUNT

            self.logger.info(
                f"📊 {instrument} {direction} ${amount:.2f} @ {confidence:.0%} "
                f"(payout={payout_ratio:.2%})"
            )
            self.logger.info(f"   Strategy: {self.strategy_name}")
            self.logger.info(f"   Reasons: {', '.join(reasons[:2])}")

            # Place order
            action = 'call' if direction == 'CALL' else 'put'
            success, order_id = self.api_client.buy(amount, instrument, action, 1)

            if not success:
                self.logger.error("❌ Trade failed")
                return None

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Log to database
            if self.db_logger:
                try:
                    trade_data = {
                        'trade_id': str(order_id),
                        'instrument': instrument,
                        'direction': direction,
                        'amount': amount,
                        'entry_time': datetime.now(),
                        'expiration_seconds': 60,
                        'selected_strategy': self.strategy_name,
                        'confidence': int(confidence * 100),
                        'payout_ratio': payout_ratio,
                        'execution_time_ms': execution_time_ms,
                        'mode': UltimateEvaluatorConfig.TRADING_MODE
                    }

                    if hasattr(self.db_logger, 'log_trade'):
                        if MultiAccountTradeLogger is not None:
                            self.db_logger.log_trade('evaluation_account', trade_data)
                        else:
                            self.db_logger.log_trade(trade_data)
                except Exception as e:
                    self.logger.warning(f"Database logging failed: {e}")

            # Wait for result
            time.sleep(UltimateEvaluatorConfig.WAIT_FOR_RESULT_SECONDS)

            # Check result
            profit = self.api_client.check_win_v3(order_id)
            if profit is None:
                return None

            won = profit > 0
            result_str = 'WIN' if won else 'LOSS'

            self.logger.info(f"{'✅' if won else '❌'} {result_str}: ${profit:.2f}")

            # Update portfolio
            self.portfolio.update_trade_result(
                self.strategy_name, won, profit, confidence, payout_ratio
            )

            # Update local stats
            self.trades_today += 1
            self.last_trade_time = time.time()

            if won:
                self.consecutive_losses = 0
            else:
                self.consecutive_losses += 1

            prometheus_execution_time.observe(execution_time_ms)

            return {
                'strategy': self.strategy_name,
                'instrument': instrument,
                'result': result_str,
                'profit': profit,
                'confidence': confidence
            }

        except Exception as e:
            self.logger.error(f"Execute trade error: {e}")
            return None

    def run(self):
        """Main strategy evaluation loop"""
        self.running = True
        self.logger.info(f"🚀 Strategy thread started: {self.strategy_name}")

        while self.running:
            try:
                if not self.can_trade():
                    time.sleep(UltimateEvaluatorConfig.STRATEGY_SCAN_INTERVAL)
                    continue

                instruments = self.get_available_instruments()
                if not instruments:
                    time.sleep(UltimateEvaluatorConfig.STRATEGY_SCAN_INTERVAL)
                    continue

                # Analyze instruments
                for instrument in instruments[:10]:
                    if not self.running:
                        break

                    analysis = self.analyze_instrument(instrument)
                    if analysis:
                        direction, confidence, reasons, payout_ratio = analysis
                        result = self.execute_trade(instrument, direction, confidence, reasons, payout_ratio)
                        if result:
                            # Wait before next trade
                            time.sleep(UltimateEvaluatorConfig.MIN_SECONDS_BETWEEN_TRADES)
                            break

                time.sleep(UltimateEvaluatorConfig.STRATEGY_SCAN_INTERVAL)

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


# =============================================================================
# ULTIMATE STRATEGY EVALUATOR (Main Orchestrator)
# =============================================================================

class UltimateStrategyEvaluator:
    """Main orchestrator for evaluating 10+ strategies"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.portfolio = PortfolioStateManager(
            initial_balance=UltimateEvaluatorConfig.FICTITIOUS_START_BALANCE
        )
        self.db_logger = None
        self.strategy_threads: Dict[str, StrategyEvaluatorThread] = {}
        self.api = None
        self.api_client = None
        self.running = False

        # Initialize database
        if DB_LOGGING_ENABLED:
            try:
                if MultiAccountTradeLogger is not None:
                    self.db_logger = MultiAccountTradeLogger(UltimateEvaluatorConfig.DATABASE_URL)
                else:
                    self.db_logger = TradeLogger(UltimateEvaluatorConfig.DATABASE_URL)
                self.logger.info("✅ Database logging enabled")
            except Exception as e:
                self.logger.warning(f"⚠️ Database initialization failed: {e}")

    def connect_to_broker(self) -> bool:
        """Connect to IQ Option"""
        try:
            email = os.getenv('IQOPTION_EMAIL')
            password = os.getenv('IQOPTION_PASSWORD')

            if not email or not password:
                self.logger.error("❌ IQ Option credentials not found in .env")
                return False

            self.logger.info(f"🔌 Connecting to IQ Option: {email}")

            self.api = IQ_Option(email, password)
            check, reason = self.api.connect()

            if not check:
                self.logger.error(f"❌ Connection failed: {reason}")
                return False

            # Set trading mode
            if UltimateEvaluatorConfig.TRADING_MODE == 'live':
                self.api.change_balance('REAL')
                self.logger.warning("⚠️ LIVE MODE")
            else:
                self.api.change_balance('PRACTICE')
                self.logger.info("✅ Demo mode")

            balance = self.api.get_balance()
            self.logger.info(f"💰 Account balance: ${balance:.2f}")

            # Initialize API client
            self.api_client = ApiClient(
                self.api,
                min_interval=UltimateEvaluatorConfig.API_MIN_INTERVAL,
                max_retries=UltimateEvaluatorConfig.API_MAX_RETRIES
            )

            return True

        except Exception as e:
            self.logger.error(f"❌ Connection error: {e}")
            return False

    def initialize_strategy_threads(self) -> bool:
        """Initialize all strategy evaluation threads"""
        self.logger.info("="*80)
        self.logger.info("🚀 ULTIMATE STRATEGY EVALUATOR")
        self.logger.info("="*80)
        self.logger.info(f"Initializing {len(UltimateEvaluatorConfig.STRATEGIES_TO_EVALUATE)} strategies...")

        for strategy_name in UltimateEvaluatorConfig.STRATEGIES_TO_EVALUATE:
            thread = StrategyEvaluatorThread(
                strategy_name, self.api_client, self.portfolio,
                self.db_logger, self.logger
            )
            self.strategy_threads[strategy_name] = thread
            self.logger.info(f"   ✅ {strategy_name}")

        prometheus_active_strategies.set(len(self.strategy_threads))

        self.logger.info(f"✅ {len(self.strategy_threads)} strategies ready")
        self.logger.info("="*80)

        return True

    def start(self):
        """Start all strategy threads"""
        if not self.strategy_threads:
            self.logger.error("No strategies initialized")
            return False

        self.running = True
        self.logger.info("🎯 Starting all strategy evaluation threads...")

        # Start each strategy in its own thread
        for strategy_name, thread in self.strategy_threads.items():
            thread.start()
            self.logger.info(f"   ✅ {strategy_name} thread started")

        # Monitor threads
        try:
            while self.running:
                time.sleep(60)
                self._print_status()
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested...")
            self.stop()

        return True

    def stop(self):
        """Stop all strategy threads"""
        self.running = False

        self.logger.info("🛑 Stopping all strategy threads...")
        for thread in self.strategy_threads.values():
            thread.stop()

        self.logger.info("✅ All strategies stopped")

    def _print_status(self):
        """Print current status"""
        stats = self.portfolio.get_portfolio_stats()

        self.logger.info("="*80)
        self.logger.info("📊 PORTFOLIO STATUS")
        self.logger.info(f"Balance: ${stats['current_balance']:.2f} (Start: ${stats['initial_balance']:.2f})")
        self.logger.info(f"Daily P&L: ${stats['daily_pnl']:.2f}")
        self.logger.info(f"ROI: {stats['roi']:.2f}%")
        self.logger.info(f"Max Drawdown: {stats['max_drawdown']:.2f}%")
        self.logger.info(f"Total Trades: {stats['total_trades']}")
        self.logger.info(f"Portfolio Win Rate: {stats['portfolio_win_rate']:.2f}%")
        self.logger.info("")
        self.logger.info("📈 STRATEGY PERFORMANCE")

        # Sort strategies by P&L
        sorted_strategies = sorted(
            stats['strategies'].items(),
            key=lambda x: x[1]['total_pnl'],
            reverse=True
        )

        for strategy_name, strategy_stats in sorted_strategies:
            self.logger.info(
                f"  {strategy_name:25s} | "
                f"Trades: {strategy_stats['total_trades']:3d} | "
                f"WR: {strategy_stats['win_rate']:5.1f}% | "
                f"P&L: ${strategy_stats['total_pnl']:7.2f} | "
                f"Sharpe: {strategy_stats['sharpe_ratio']:5.2f} | "
                f"Kelly: {strategy_stats['kelly_fraction']:.3f}"
            )

        self.logger.info("="*80)

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        return self.portfolio.get_portfolio_stats()

    def export_reports(self):
        """Export performance reports"""
        if not self.db_logger:
            return

        try:
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Export CSV
            if hasattr(self.db_logger, 'export_trades_to_csv'):
                csv_file = reports_dir / f'strategy_evaluation_{timestamp}.csv'
                self.db_logger.export_trades_to_csv(str(csv_file), days=7)

            # Export JSON
            if hasattr(self.db_logger, 'export_performance_to_json'):
                json_file = reports_dir / f'strategy_performance_{timestamp}.json'
                self.db_logger.export_performance_to_json(str(json_file), days=7)

            # Export portfolio stats as JSON
            stats_file = reports_dir / f'portfolio_stats_{timestamp}.json'
            with open(stats_file, 'w') as f:
                json.dump(self.get_statistics(), f, indent=2)

            self.logger.info(f"✅ Reports exported to {reports_dir}")

        except Exception as e:
            self.logger.error(f"Failed to export reports: {e}")


# =============================================================================
# HEALTH API
# =============================================================================

def create_health_api(evaluator: UltimateStrategyEvaluator):
    """Create health monitoring API"""
    app = Flask(__name__)

    # Cache for statistics to avoid blocking calls
    stats_cache = {
        'data': {
            'current_balance': 100.0,
            'initial_balance': 100.0,
            'daily_pnl': 0.0,
            'roi': 0.0,
            'portfolio_win_rate': 0.0,
            'max_drawdown': 0.0,
            'total_trades': 0,
            'total_wins': 0,
            'total_losses': 0,
            'active_strategies': 0,
            'strategies': {}
        },
        'timestamp': 0,
        'updating': False
    }

    def update_statistics_cache():
        """Background thread to update statistics cache"""
        while True:
            try:
                time.sleep(3)  # Update every 3 seconds
                if not stats_cache['updating']:
                    stats_cache['updating'] = True
                    try:
                        new_data = evaluator.get_statistics()
                        stats_cache['data'] = new_data
                        stats_cache['timestamp'] = time.time()
                    except Exception as e:
                        app.logger.error(f"Error updating statistics cache: {e}")
                    finally:
                        stats_cache['updating'] = False
            except Exception as e:
                app.logger.error(f"Cache update thread error: {e}")
                time.sleep(5)

    # Start background cache updater
    import threading
    cache_thread = threading.Thread(target=update_statistics_cache, daemon=True)
    cache_thread.start()

    def get_cached_statistics():
        """Get statistics from cache (never blocks)"""
        return stats_cache['data']

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
        return jsonify(get_cached_statistics())

    @app.route('/strategies', methods=['GET'])
    def strategies():
        """Get all strategies performance"""
        stats = get_cached_statistics()
        return jsonify({
            'strategies': stats.get('strategies', {}),
            'total': len(stats.get('strategies', {}))
        })

    @app.route('/strategy/<strategy_name>', methods=['GET'])
    def strategy_detail(strategy_name):
        """Get specific strategy details"""
        stats = get_cached_statistics()
        strategies = stats.get('strategies', {})

        if strategy_name not in strategies:
            return jsonify({'error': 'Strategy not found'}), 404

        return jsonify(strategies[strategy_name])

    @app.route('/export/csv', methods=['GET'])
    def export_csv():
        """Export trades to CSV"""
        days = int(request.args.get('days', 7))

        if not evaluator.db_logger:
            return jsonify({'error': 'Database not available'}), 503

        try:
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'strategy_evaluation_{timestamp}.csv'
            filepath = reports_dir / filename

            if hasattr(evaluator.db_logger, 'export_trades_to_csv'):
                evaluator.db_logger.export_trades_to_csv(str(filepath), days=days)
                return send_file(str(filepath), as_attachment=True, download_name=filename)
            else:
                return jsonify({'error': 'Export not supported'}), 503

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/export/json', methods=['GET'])
    def export_json():
        """Export performance to JSON"""
        try:
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'strategy_performance_{timestamp}.json'
            filepath = reports_dir / filename

            stats = evaluator.get_statistics()
            with open(filepath, 'w') as f:
                json.dump(stats, f, indent=2)

            return send_file(str(filepath), as_attachment=True, download_name=filename)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/stop', methods=['POST'])
    def stop():
        evaluator.stop()
        return jsonify({'message': 'Shutdown initiated'})

    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Prometheus metrics endpoint"""
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    @app.route('/performance', methods=['GET'])
    def performance():
        """Get performance metrics (alias for /statistics for Angular dashboard compatibility)"""
        stats = get_cached_statistics()
        return jsonify({
            'summary': {
                'balance': stats['current_balance'],
                'daily_pnl': stats['daily_pnl'],
                'roi_percent': stats['roi'],
                'win_rate': stats['portfolio_win_rate'],
                'total_trades': stats['total_trades'],
                'wins': stats['total_wins'],
                'losses': stats['total_losses']
            },
            'streaks': {
                'current_win_streak': 0,  # Calculate from strategies if needed
                'current_loss_streak': 0,
                'best_win_streak': 0,
                'worst_loss_streak': 0
            },
            'limits': {
                'max_concurrent_instruments': 10,
                'max_daily_loss': UltimateEvaluatorConfig.MAX_DAILY_LOSS,
                'remaining_loss_budget': max(0, UltimateEvaluatorConfig.MAX_DAILY_LOSS - abs(stats['daily_pnl']))
            },
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/config', methods=['GET'])
    def config():
        """Get bot configuration"""
        return jsonify({
            'trading': {
                'mode': UltimateEvaluatorConfig.TRADING_MODE,
                'min_payout_ratio': UltimateEvaluatorConfig.MIN_PAYOUT_RATIO,
                'expiration_seconds': UltimateEvaluatorConfig.BINARY_OPTION_DURATION * 60
            },
            'strategy': {
                'advanced_strategies_enabled': ADVANCED_STRATEGIES_AVAILABLE,
                'min_confidence': UltimateEvaluatorConfig.MIN_CONFIDENCE_BASE,
                'min_confluence': 'N/A',
                'max_trade_amount': UltimateEvaluatorConfig.BASE_TRADE_AMOUNT
            }
        })

    @app.route('/active_trades', methods=['GET'])
    def active_trades():
        """Get active trades"""
        # For now return empty as we don't track active trades in memory
        # This would require enhancing the evaluator to track pending trades
        return jsonify({
            'active_count': 0,
            'active_trades': []
        })

    @app.route('/recent_trades', methods=['GET'])
    def recent_trades():
        """Get recent trades from database"""
        limit = int(request.args.get('limit', 10))

        if not evaluator.db_logger:
            return jsonify({'trades': []}), 200

        try:
            # Query database for recent trades with timeout to prevent hanging
            import psycopg2

            # Create connection with timeout to prevent hanging
            conn = psycopg2.connect(
                UltimateEvaluatorConfig.DATABASE_URL,
                connect_timeout=5
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT trade_id, instrument, direction, amount, entry_time,
                       exit_time, result, profit, payout_ratio, selected_strategy
                FROM trades
                ORDER BY entry_time DESC
                LIMIT %s
            """, (limit,))

            trades = []
            for row in cursor.fetchall():
                trades.append({
                    'id': row[0],
                    'instrument': row[1],
                    'direction': row[2],
                    'amount': float(row[3]) if row[3] else 0,
                    'entry_time': row[4].isoformat() if row[4] else None,
                    'exit_time': row[5].isoformat() if row[5] else None,
                    'result': row[6],
                    'profit': float(row[7]) if row[7] else None,
                    'payout_ratio': float(row[8]) if row[8] else None,
                    'selected_strategy': row[9]
                })

            cursor.close()
            conn.close()

            return jsonify({'trades': trades})

        except Exception as e:
            app.logger.error(f"Error fetching recent trades: {e}")
            return jsonify({'trades': [], 'error': str(e)}), 200

    @app.route('/strategy_stats', methods=['GET'])
    def strategy_stats():
        """Get strategy statistics (maps to /strategies)"""
        hours = request.args.get('hours', type=int)
        stats = get_cached_statistics()
        strategies = stats.get('strategies', {})

        # Convert to format expected by Angular dashboard
        strategy_list = []
        for name, metrics in strategies.items():
            strategy_list.append({
                'strategy_name': name,
                'total_trades': metrics['total_trades'],
                'wins': metrics['wins'],
                'losses': metrics['losses'],
                'win_rate': metrics['win_rate'],
                'total_profit': metrics['total_pnl'],
                'avg_profit_per_trade': metrics['total_pnl'] / metrics['total_trades'] if metrics['total_trades'] > 0 else 0,
                'best_trade': 0,  # Would need to track this
                'worst_trade': 0,  # Would need to track this
                'avg_payout_percent': metrics['avg_payout'] * 100
            })

        return jsonify({
            'strategy_stats': strategy_list,
            'time_period': f'last_{hours}_hours' if hours else 'all_time',
            'total_strategies': len(strategy_list)
        })

    @app.route('/pause', methods=['POST'])
    def pause():
        """Pause trading (placeholder)"""
        return jsonify({'message': 'Pause not implemented - use /stop to shutdown'})

    @app.route('/resume', methods=['POST'])
    def resume():
        """Resume trading (placeholder)"""
        return jsonify({'message': 'Resume not implemented - restart the evaluator to resume'})

    return app


def start_health_server(app: Flask, logger: logging.Logger):
    """Start health API server"""
    try:
        import waitress
        logger.info("ℹ️ Starting health API with waitress")
        waitress.serve(
            app,
            host='0.0.0.0',
            port=UltimateEvaluatorConfig.HEALTH_API_PORT,
            threads=32,  # Increased from 8 to handle concurrent dashboard + Prometheus requests
            channel_timeout=120,  # Increased from 60 to prevent premature timeouts
            log_socket_errors=False,
            asyncore_use_poll=True,  # Better performance for many connections
            backlog=64  # Queue up to 64 connections before rejecting
        )
    except Exception:
        logger.warning("⚠️ Health API running with Flask's built-in server")
        app.run(host='0.0.0.0', port=UltimateEvaluatorConfig.HEALTH_API_PORT,
               debug=False, use_reloader=False, threaded=True)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    logger = setup_logging()

    logger.info("="*80)
    logger.info("🚀 ULTIMATE BINARY OPTION STRATEGY EVALUATOR")
    logger.info("="*80)
    logger.info(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {UltimateEvaluatorConfig.TRADING_MODE.upper()}")
    logger.info(f"Fictitious Balance: ${UltimateEvaluatorConfig.FICTITIOUS_START_BALANCE:.2f}")
    logger.info(f"Strategies to Evaluate: {len(UltimateEvaluatorConfig.STRATEGIES_TO_EVALUATE)}")
    logger.info("="*80)

    if not ADVANCED_STRATEGIES_AVAILABLE:
        logger.error("❌ Advanced strategies not available")
        return 1

    evaluator = UltimateStrategyEvaluator(logger)

    if not evaluator.connect_to_broker():
        logger.error("❌ Failed to connect to broker")
        return 1

    if not evaluator.initialize_strategy_threads():
        logger.error("❌ Failed to initialize strategies")
        return 1

    if UltimateEvaluatorConfig.ENABLE_HEALTH_API:
        health_app = create_health_api(evaluator)
        health_thread = threading.Thread(
            target=lambda: start_health_server(health_app, logger),
            daemon=True
        )
        health_thread.start()
        logger.info(f"🏥 Health API: http://localhost:{UltimateEvaluatorConfig.HEALTH_API_PORT}")
        logger.info(f"   - Statistics: http://localhost:{UltimateEvaluatorConfig.HEALTH_API_PORT}/statistics")
        logger.info(f"   - Strategies: http://localhost:{UltimateEvaluatorConfig.HEALTH_API_PORT}/strategies")
        logger.info(f"   - Metrics: http://localhost:{UltimateEvaluatorConfig.HEALTH_API_PORT}/metrics")

    try:
        evaluator.start()
    except Exception as e:
        logger.error(f"❌ Fatal: {e}")
        return 1
    finally:
        logger.info("="*80)
        logger.info("🏁 SHUTDOWN")
        logger.info("="*80)

        stats = evaluator.get_statistics()
        logger.info(f"Total Trades: {stats.get('total_trades', 0)}")
        logger.info(f"Portfolio Win Rate: {stats.get('portfolio_win_rate', 0):.2f}%")
        logger.info(f"Final Balance: ${stats.get('current_balance', 0):.2f}")
        logger.info(f"ROI: {stats.get('roi', 0):.2f}%")

        # Export final reports
        logger.info("📊 Exporting final reports...")
        evaluator.export_reports()

    return 0


if __name__ == '__main__':
    sys.exit(main())
