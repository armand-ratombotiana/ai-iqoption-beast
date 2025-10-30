#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SPECIALIZED BINARY OPTIONS STRATEGY ENGINE
Handles the reality of binary options trading with advanced analytics

Features:
✅ Binary-specific market condition analysis
✅ Volatility-aware signal generation
✅ Time-decay consideration (60-second expiry)
✅ Broker behavior modeling (slippage, rejection rates)
✅ Market microstructure analysis
✅ Entry timing optimization
✅ Comprehensive data collection for AI training
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
from enum import Enum


class MarketCondition(Enum):
    """Market condition classification"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"


class EntryQuality(Enum):
    """Entry timing quality"""
    EXCELLENT = "excellent"  # Perfect timing, < 2 seconds to expiry minute
    GOOD = "good"  # Good timing, < 5 seconds
    FAIR = "fair"  # Acceptable, < 10 seconds
    POOR = "poor"  # Late entry, > 10 seconds


@dataclass
class MarketSnapshot:
    """Comprehensive market snapshot for AI training"""
    timestamp: datetime
    instrument: str

    # Price data
    current_price: float
    open_price: float
    high_price: float
    low_price: float

    # Market conditions
    volatility: float  # ATR-based volatility
    trend_strength: float  # ADX
    trend_direction: int  # 1=up, -1=down, 0=neutral

    # Technical indicators
    rsi: float
    macd: float
    macd_signal: float
    bollinger_position: float  # -1 to 1 (bottom to top)

    # Market microstructure
    price_momentum_1m: float  # 1-minute momentum
    price_momentum_5m: float  # 5-minute momentum
    volume_ratio: float  # Current volume vs average

    # Binary-specific metrics
    seconds_to_minute: int  # Seconds remaining in current minute
    candle_completion: float  # 0.0 to 1.0
    recent_rejection_rate: float  # Broker rejection rate

    # Classification
    market_condition: MarketCondition
    entry_quality: EntryQuality


@dataclass
class BinarySignal:
    """Enhanced signal with binary options reality"""
    direction: str  # CALL or PUT
    confidence: float
    reasons: List[str]

    # Binary-specific
    market_snapshot: MarketSnapshot
    expected_win_probability: float
    risk_score: float  # 0.0 to 1.0
    optimal_entry_seconds: int  # Optimal seconds to wait before entry

    # Strategy tracking
    strategy_name: str
    signal_strength: float  # 0.0 to 1.0
    confluence_score: int  # Number of confirming indicators


@dataclass
class TradeAnalytics:
    """Comprehensive trade analytics for AI training"""
    # Trade identifiers
    trade_id: str
    strategy_name: str
    timestamp: datetime

    # Market state at entry
    market_snapshot_entry: MarketSnapshot

    # Trade execution
    instrument: str
    direction: str
    amount: float
    entry_price: float
    entry_delay_ms: int  # Delay from signal to execution

    # Trade parameters
    confidence: float
    payout_ratio: float
    expected_profit: float

    # Market state at expiry
    exit_price: float
    price_movement: float  # Pips/points moved

    # Outcome
    result: str  # WIN or LOSS
    profit: float

    # Performance metrics
    entry_timing_quality: EntryQuality
    market_condition_stability: float  # Did conditions change during trade?
    volatility_during_trade: float

    # Learning features
    feature_vector: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            'trade_id': self.trade_id,
            'strategy_name': self.strategy_name,
            'timestamp': self.timestamp.isoformat(),
            'instrument': self.instrument,
            'direction': self.direction,
            'amount': self.amount,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'price_movement': self.price_movement,
            'entry_delay_ms': self.entry_delay_ms,
            'confidence': self.confidence,
            'payout_ratio': self.payout_ratio,
            'expected_profit': self.expected_profit,
            'result': self.result,
            'profit': self.profit,
            'entry_timing_quality': self.entry_timing_quality.value,
            'market_condition': self.market_snapshot_entry.market_condition.value,
            'volatility': self.market_snapshot_entry.volatility,
            'trend_strength': self.market_snapshot_entry.trend_strength,
            'rsi': self.market_snapshot_entry.rsi,
            'macd': self.market_snapshot_entry.macd,
            'seconds_to_minute': self.market_snapshot_entry.seconds_to_minute,
            'feature_vector': self.feature_vector
        }


class BinaryOptionsEngine:
    """Specialized engine for binary options trading"""

    def __init__(self):
        self.rejection_history = []  # Track broker rejections
        self.execution_delays = []  # Track execution delays

    def analyze_market_conditions(self, candles: List[Dict]) -> MarketSnapshot:
        """Comprehensive market condition analysis"""
        if len(candles) < 50:
            return None

        closes = np.array([c['close'] for c in candles])
        highs = np.array([c.get('max', c['close']) for c in candles])
        lows = np.array([c.get('min', c['close']) for c in candles])
        volumes = np.array([c.get('volume', 0) for c in candles])

        current_price = closes[-1]

        # Calculate volatility (ATR)
        volatility = self._calculate_atr(highs, lows, closes, period=14)

        # Calculate trend strength (ADX)
        trend_strength = self._calculate_adx(highs, lows, closes, period=14)

        # Determine trend direction
        ema_fast = self._calculate_ema(closes, 8)
        ema_slow = self._calculate_ema(closes, 21)
        trend_direction = 1 if ema_fast > ema_slow else -1

        # Technical indicators
        rsi = self._calculate_rsi(closes, 14)
        macd, macd_signal = self._calculate_macd(closes)

        # Bollinger Bands position
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(closes, 20, 2)
        if bb_upper > bb_lower:
            bollinger_position = (current_price - bb_lower) / (bb_upper - bb_lower) - 0.5
        else:
            bollinger_position = 0.0

        # Market momentum
        price_momentum_1m = (closes[-1] - closes[-2]) / closes[-2] if len(closes) > 1 else 0
        price_momentum_5m = (closes[-1] - closes[-6]) / closes[-6] if len(closes) > 5 else 0

        # Volume analysis
        avg_volume = np.mean(volumes[-20:]) if len(volumes) > 20 else 1
        volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1.0

        # Binary-specific metrics
        now = datetime.now()
        seconds_to_minute = 60 - now.second
        candle_completion = now.second / 60.0

        # Determine market condition
        market_condition = self._classify_market_condition(
            volatility, trend_strength, rsi, closes
        )

        # Determine entry quality based on timing
        entry_quality = self._assess_entry_timing(seconds_to_minute)

        return MarketSnapshot(
            timestamp=now,
            instrument="",  # Set by caller
            current_price=current_price,
            open_price=candles[-1]['open'],
            high_price=highs[-1],
            low_price=lows[-1],
            volatility=volatility,
            trend_strength=trend_strength,
            trend_direction=trend_direction,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            bollinger_position=bollinger_position,
            price_momentum_1m=price_momentum_1m,
            price_momentum_5m=price_momentum_5m,
            volume_ratio=volume_ratio,
            seconds_to_minute=seconds_to_minute,
            candle_completion=candle_completion,
            recent_rejection_rate=self._calculate_rejection_rate(),
            market_condition=market_condition,
            entry_quality=entry_quality
        )

    def generate_binary_signal(self, market_snapshot: MarketSnapshot,
                               strategy_name: str) -> Optional[BinarySignal]:
        """Generate binary options signal with reality checks"""

        # Check if market conditions are suitable for binary options
        if not self._is_tradeable_condition(market_snapshot):
            return None

        # Generate signal based on market snapshot
        direction, confidence, reasons = self._analyze_for_signal(market_snapshot)

        if direction == "NEUTRAL" or confidence < 0.60:
            return None

        # Calculate binary-specific metrics
        win_probability = self._estimate_win_probability(market_snapshot, direction)
        risk_score = self._calculate_risk_score(market_snapshot)
        optimal_entry_seconds = self._calculate_optimal_entry_timing(market_snapshot)
        signal_strength = confidence
        confluence_score = len(reasons)

        return BinarySignal(
            direction=direction,
            confidence=confidence,
            reasons=reasons,
            market_snapshot=market_snapshot,
            expected_win_probability=win_probability,
            risk_score=risk_score,
            optimal_entry_seconds=optimal_entry_seconds,
            strategy_name=strategy_name,
            signal_strength=signal_strength,
            confluence_score=confluence_score
        )

    def _is_tradeable_condition(self, snapshot: MarketSnapshot) -> bool:
        """Check if market conditions are suitable for binary trading"""

        # Avoid trading at the very end of a candle (< 5 seconds)
        if snapshot.seconds_to_minute < 5:
            return False

        # Avoid extremely low volatility (flat market)
        if snapshot.volatility < 0.00005:
            return False

        # Avoid extremely high volatility (unpredictable)
        if snapshot.volatility > 0.01:
            return False

        # Avoid high broker rejection periods
        if snapshot.recent_rejection_rate > 0.3:
            return False

        return True

    def _analyze_for_signal(self, snapshot: MarketSnapshot) -> Tuple[str, float, List[str]]:
        """Analyze market snapshot for trading signal"""
        reasons = []
        bull_score = 0
        bear_score = 0

        # Trend analysis
        if snapshot.trend_direction > 0 and snapshot.trend_strength > 25:
            bull_score += 2
            reasons.append("Strong uptrend")
        elif snapshot.trend_direction < 0 and snapshot.trend_strength > 25:
            bear_score += 2
            reasons.append("Strong downtrend")

        # RSI analysis
        if snapshot.rsi < 30:
            bull_score += 2
            reasons.append("RSI oversold")
        elif snapshot.rsi > 70:
            bear_score += 2
            reasons.append("RSI overbought")
        elif 40 < snapshot.rsi < 60:
            # Neutral RSI in trending market
            if snapshot.trend_direction > 0:
                bull_score += 1
            else:
                bear_score += 1

        # MACD analysis
        if snapshot.macd > snapshot.macd_signal:
            bull_score += 1
            reasons.append("MACD bullish")
        else:
            bear_score += 1
            reasons.append("MACD bearish")

        # Bollinger Bands analysis
        if snapshot.bollinger_position < -0.4:
            bull_score += 1
            reasons.append("Price near BB lower")
        elif snapshot.bollinger_position > 0.4:
            bear_score += 1
            reasons.append("Price near BB upper")

        # Momentum analysis
        if snapshot.price_momentum_1m > 0.0001 and snapshot.price_momentum_5m > 0:
            bull_score += 1
            reasons.append("Positive momentum")
        elif snapshot.price_momentum_1m < -0.0001 and snapshot.price_momentum_5m < 0:
            bear_score += 1
            reasons.append("Negative momentum")

        # Determine direction and confidence
        total_score = bull_score + bear_score
        if total_score == 0:
            return "NEUTRAL", 0.0, []

        if bull_score > bear_score:
            confidence = bull_score / (bull_score + bear_score)
            return "CALL", confidence, reasons
        elif bear_score > bull_score:
            confidence = bear_score / (bull_score + bear_score)
            return "PUT", confidence, reasons
        else:
            return "NEUTRAL", 0.5, reasons

    def _estimate_win_probability(self, snapshot: MarketSnapshot, direction: str) -> float:
        """Estimate win probability based on market conditions"""
        base_probability = 0.55  # Base 55% for binary options

        # Adjust for trend strength
        if snapshot.trend_strength > 25:
            if (direction == "CALL" and snapshot.trend_direction > 0) or \
               (direction == "PUT" and snapshot.trend_direction < 0):
                base_probability += 0.10

        # Adjust for volatility
        if 0.0001 < snapshot.volatility < 0.001:
            base_probability += 0.05  # Optimal volatility

        # Adjust for entry timing
        if snapshot.entry_quality == EntryQuality.EXCELLENT:
            base_probability += 0.05
        elif snapshot.entry_quality == EntryQuality.GOOD:
            base_probability += 0.02

        # Adjust for market condition
        if snapshot.market_condition in [MarketCondition.TRENDING_UP, MarketCondition.TRENDING_DOWN]:
            base_probability += 0.05

        return min(0.85, base_probability)  # Cap at 85%

    def _calculate_risk_score(self, snapshot: MarketSnapshot) -> float:
        """Calculate risk score (0.0 = low risk, 1.0 = high risk)"""
        risk = 0.0

        # Volatility risk
        if snapshot.volatility > 0.005:
            risk += 0.3
        elif snapshot.volatility < 0.0001:
            risk += 0.2

        # Timing risk
        if snapshot.seconds_to_minute < 10:
            risk += 0.3

        # Trend uncertainty risk
        if snapshot.trend_strength < 20:
            risk += 0.2

        # Market condition risk
        if snapshot.market_condition == MarketCondition.HIGH_VOLATILITY:
            risk += 0.2

        return min(1.0, risk)

    def _calculate_optimal_entry_timing(self, snapshot: MarketSnapshot) -> int:
        """Calculate optimal seconds to wait before entry"""
        # Ideal entry is 15-20 seconds into the new minute
        current_second = 60 - snapshot.seconds_to_minute

        if current_second < 15:
            return 15 - current_second
        elif current_second > 50:
            return 65 - current_second  # Wait for next minute
        else:
            return 0  # Enter now

    def _classify_market_condition(self, volatility: float, trend_strength: float,
                                   rsi: float, closes: np.ndarray) -> MarketCondition:
        """Classify current market condition"""

        # High/Low volatility
        if volatility > 0.005:
            return MarketCondition.HIGH_VOLATILITY
        elif volatility < 0.0001:
            return MarketCondition.LOW_VOLATILITY

        # Trending conditions
        if trend_strength > 25:
            if closes[-1] > closes[-10]:
                return MarketCondition.TRENDING_UP
            else:
                return MarketCondition.TRENDING_DOWN

        # Reversal detection (RSI extreme + price action)
        if rsi > 75 or rsi < 25:
            return MarketCondition.REVERSAL

        # Breakout detection
        if len(closes) > 20:
            recent_high = np.max(closes[-20:])
            recent_low = np.min(closes[-20:])
            if closes[-1] > recent_high * 0.999 or closes[-1] < recent_low * 1.001:
                return MarketCondition.BREAKOUT

        return MarketCondition.RANGING

    def _assess_entry_timing(self, seconds_to_minute: int) -> EntryQuality:
        """Assess entry timing quality"""
        # Optimal entry: 40-55 seconds remaining (5-20 seconds into minute)
        if 40 <= seconds_to_minute <= 55:
            return EntryQuality.EXCELLENT
        elif 25 <= seconds_to_minute < 40 or 55 < seconds_to_minute <= 60:
            return EntryQuality.GOOD
        elif 10 <= seconds_to_minute < 25:
            return EntryQuality.FAIR
        else:
            return EntryQuality.POOR

    def _calculate_rejection_rate(self) -> float:
        """Calculate recent broker rejection rate"""
        if not self.rejection_history:
            return 0.0

        # Only consider last 20 attempts
        recent = self.rejection_history[-20:]
        return sum(recent) / len(recent)

    # Technical indicator calculations
    def _calculate_atr(self, highs: np.ndarray, lows: np.ndarray,
                      closes: np.ndarray, period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(closes) < period + 1:
            return 0.0

        high_low = highs - lows
        high_close = np.abs(highs[1:] - closes[:-1])
        low_close = np.abs(lows[1:] - closes[:-1])

        true_range = np.maximum(high_low[1:], np.maximum(high_close, low_close))
        atr = np.mean(true_range[-period:])

        return float(atr)

    def _calculate_adx(self, highs: np.ndarray, lows: np.ndarray,
                      closes: np.ndarray, period: int = 14) -> float:
        """Calculate Average Directional Index"""
        if len(closes) < period + 1:
            return 0.0

        # Simplified ADX calculation
        plus_dm = np.maximum(highs[1:] - highs[:-1], 0)
        minus_dm = np.maximum(lows[:-1] - lows[1:], 0)

        atr = self._calculate_atr(highs, lows, closes, period)
        if atr == 0:
            return 0.0

        plus_di = 100 * np.mean(plus_dm[-period:]) / atr
        minus_di = 100 * np.mean(minus_dm[-period:]) / atr

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0

        return float(dx)

    def _calculate_ema(self, data: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return float(np.mean(data))

        multiplier = 2 / (period + 1)
        ema = np.mean(data[:period])

        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return float(ema)

    def _calculate_rsi(self, closes: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(closes) < period + 1:
            return 50.0

        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return float(rsi)

    def _calculate_macd(self, closes: np.ndarray,
                       fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
        """Calculate MACD and Signal line"""
        if len(closes) < slow:
            return 0.0, 0.0

        ema_fast = self._calculate_ema(closes, fast)
        ema_slow = self._calculate_ema(closes, slow)

        macd = ema_fast - ema_slow

        # Simplified signal line (should use EMA of MACD)
        macd_signal = macd * 0.9  # Approximation

        return float(macd), float(macd_signal)

    def _calculate_bollinger_bands(self, closes: np.ndarray,
                                   period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        if len(closes) < period:
            mean = np.mean(closes)
            return mean, mean, mean

        middle = np.mean(closes[-period:])
        std = np.std(closes[-period:])

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        return float(upper), float(middle), float(lower)
