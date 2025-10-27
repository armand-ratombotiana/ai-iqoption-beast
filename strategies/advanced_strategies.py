"""
Advanced Strategy Engine with TA-Lib Integration

This module implements sophisticated trading strategies combining:
1. Advanced candle pattern analysis
2. TA-Lib technical indicators (RSI, MACD, Bollinger Bands, Stochastic, etc.)
3. Multi-timeframe analysis
4. Confluence-based signal generation

Optimized for $100 real money trading with focus on high-probability setups.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from statistics import mean, stdev

# Try to import TA-Lib, fall back to custom implementations
try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    logging.warning("TA-Lib not available. Using fallback implementations.")


@dataclass
class StrategySignal:
    """Signal output from a strategy"""
    direction: str  # 'CALL', 'PUT', or 'NEUTRAL'
    confidence: float  # 0.0 to 1.0
    strategy_name: str
    reasons: List[str]  # Human-readable reasons for the signal
    indicators: Dict[str, float]  # Indicator values used


class AdvancedStrategyEngine:
    """
    Advanced strategy engine combining multiple technical analysis methods
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.min_candles = 50  # Minimum candles needed for most indicators

    def analyze(self, candles: List[Dict]) -> StrategySignal:
        """
        Main analysis method that combines all strategies

        Args:
            candles: List of candle dicts with keys: open, high, low, close, timestamp

        Returns:
            StrategySignal with aggregated analysis
        """
        if len(candles) < self.min_candles:
            return StrategySignal(
                direction='NEUTRAL',
                confidence=0.0,
                strategy_name='insufficient_data',
                reasons=['Not enough candles for analysis'],
                indicators={}
            )

        # Convert to numpy arrays for TA-Lib
        closes = np.array([c['close'] for c in candles], dtype=float)
        opens = np.array([c['open'] for c in candles], dtype=float)
        highs = np.array([c.get('max', c['close']) for c in candles], dtype=float)
        lows = np.array([c.get('min', c['close']) for c in candles], dtype=float)
        volumes = np.array([c.get('volume', 0) for c in candles], dtype=float)

        # Run all strategies
        strategies_results = []

        # 1. Enhanced Candle Counting Strategy
        result = self.enhanced_candle_count(candles, closes, opens)
        if result:
            strategies_results.append(result)

        # 2. RSI with Divergence
        result = self.rsi_divergence_strategy(closes, highs, lows)
        if result:
            strategies_results.append(result)

        # 3. MACD Crossover with Momentum
        result = self.macd_momentum_strategy(closes)
        if result:
            strategies_results.append(result)

        # 4. Bollinger Bands + RSI Combo
        result = self.bollinger_rsi_combo(closes)
        if result:
            strategies_results.append(result)

        # 5. Stochastic Oscillator Strategy
        result = self.stochastic_strategy(highs, lows, closes)
        if result:
            strategies_results.append(result)

        # 6. Multi-Timeframe Trend Alignment
        result = self.trend_alignment_strategy(closes)
        if result:
            strategies_results.append(result)

        # 7. Support/Resistance Breakout
        result = self.support_resistance_strategy(closes, highs, lows)
        if result:
            strategies_results.append(result)

        # Aggregate signals
        return self._aggregate_signals(strategies_results)

    def enhanced_candle_count(self, candles: List[Dict], closes: np.ndarray,
                             opens: np.ndarray) -> Optional[StrategySignal]:
        """
        Enhanced candle counting with pattern recognition
        """
        window_sizes = [5, 10, 15, 20]  # Multi-window analysis
        signals = []
        reasons = []
        indicators = {}

        for window in window_sizes:
            if len(candles) < window:
                continue

            recent_candles = candles[-window:]

            # Count bullish and bearish candles
            bullish = sum(1 for c in recent_candles if c['close'] > c['open'])
            bearish = sum(1 for c in recent_candles if c['close'] < c['open'])
            doji = window - bullish - bearish

            # Calculate candle body sizes (strength)
            bullish_strength = sum(
                abs(c['close'] - c['open'])
                for c in recent_candles
                if c['close'] > c['open']
            )
            bearish_strength = sum(
                abs(c['close'] - c['open'])
                for c in recent_candles
                if c['close'] < c['open']
            )

            # Strong directional bias
            if bullish >= bearish + 3 and bullish_strength > bearish_strength * 1.5:
                signals.append(('CALL', 0.7 + (bullish - bearish) * 0.03))
                reasons.append(f"Strong bullish pattern: {bullish}/{window} green candles")
            elif bearish >= bullish + 3 and bearish_strength > bullish_strength * 1.5:
                signals.append(('PUT', 0.7 + (bearish - bullish) * 0.03))
                reasons.append(f"Strong bearish pattern: {bearish}/{window} red candles")

            indicators[f'bullish_{window}'] = bullish
            indicators[f'bearish_{window}'] = bearish

        if not signals:
            return None

        # Aggregate multiple window signals
        call_conf = mean([s[1] for s in signals if s[0] == 'CALL']) if any(s[0] == 'CALL' for s in signals) else 0
        put_conf = mean([s[1] for s in signals if s[0] == 'PUT']) if any(s[0] == 'PUT' for s in signals) else 0

        if call_conf > put_conf and call_conf > 0.65:
            return StrategySignal('CALL', min(0.95, call_conf), 'enhanced_candle_count', reasons, indicators)
        elif put_conf > call_conf and put_conf > 0.65:
            return StrategySignal('PUT', min(0.95, put_conf), 'enhanced_candle_count', reasons, indicators)

        return None

    def rsi_divergence_strategy(self, closes: np.ndarray, highs: np.ndarray,
                                lows: np.ndarray) -> Optional[StrategySignal]:
        """
        RSI with divergence detection for reversal signals
        """
        if len(closes) < 14:
            return None

        # Calculate RSI
        if HAS_TALIB:
            rsi = talib.RSI(closes, timeperiod=14)
        else:
            rsi = self._calculate_rsi(closes, 14)

        current_rsi = rsi[-1]
        indicators = {'rsi': current_rsi}
        reasons = []

        # Oversold/Overbought conditions
        if current_rsi < 30:
            reasons.append(f"RSI oversold: {current_rsi:.2f}")
            return StrategySignal('CALL', 0.80, 'rsi_divergence', reasons, indicators)
        elif current_rsi > 70:
            reasons.append(f"RSI overbought: {current_rsi:.2f}")
            return StrategySignal('PUT', 0.80, 'rsi_divergence', reasons, indicators)

        # Divergence detection (simplified)
        if len(closes) >= 20:
            # Bullish divergence: price lower low, RSI higher low
            if closes[-1] < closes[-10] and rsi[-1] > rsi[-10] and current_rsi < 40:
                reasons.append("Bullish divergence detected")
                return StrategySignal('CALL', 0.85, 'rsi_divergence', reasons, indicators)

            # Bearish divergence: price higher high, RSI lower high
            if closes[-1] > closes[-10] and rsi[-1] < rsi[-10] and current_rsi > 60:
                reasons.append("Bearish divergence detected")
                return StrategySignal('PUT', 0.85, 'rsi_divergence', reasons, indicators)

        return None

    def macd_momentum_strategy(self, closes: np.ndarray) -> Optional[StrategySignal]:
        """
        MACD crossover with momentum confirmation
        """
        if len(closes) < 26:
            return None

        if HAS_TALIB:
            macd, signal, hist = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
        else:
            macd, signal, hist = self._calculate_macd(closes)

        indicators = {
            'macd': macd[-1],
            'signal': signal[-1],
            'histogram': hist[-1]
        }
        reasons = []

        # Bullish crossover
        if len(hist) >= 2:
            if hist[-2] < 0 and hist[-1] > 0:
                reasons.append("MACD bullish crossover")
                return StrategySignal('CALL', 0.75, 'macd_momentum', reasons, indicators)

            # Bearish crossover
            if hist[-2] > 0 and hist[-1] < 0:
                reasons.append("MACD bearish crossover")
                return StrategySignal('PUT', 0.75, 'macd_momentum', reasons, indicators)

            # Strong momentum continuation
            if hist[-1] > 0 and hist[-1] > hist[-2] > hist[-3]:
                reasons.append("Strong bullish momentum")
                return StrategySignal('CALL', 0.70, 'macd_momentum', reasons, indicators)

            if hist[-1] < 0 and hist[-1] < hist[-2] < hist[-3]:
                reasons.append("Strong bearish momentum")
                return StrategySignal('PUT', 0.70, 'macd_momentum', reasons, indicators)

        return None

    def bollinger_rsi_combo(self, closes: np.ndarray) -> Optional[StrategySignal]:
        """
        Bollinger Bands combined with RSI for high-probability reversals
        """
        if len(closes) < 20:
            return None

        # Bollinger Bands
        if HAS_TALIB:
            upper, middle, lower = talib.BBANDS(closes, timeperiod=20, nbdevup=2, nbdevdn=2)
            rsi = talib.RSI(closes, timeperiod=14)
        else:
            upper, middle, lower = self._calculate_bollinger_bands(closes, 20, 2)
            rsi = self._calculate_rsi(closes, 14)

        current_price = closes[-1]
        current_rsi = rsi[-1]

        indicators = {
            'bb_upper': upper[-1],
            'bb_middle': middle[-1],
            'bb_lower': lower[-1],
            'price': current_price,
            'rsi': current_rsi
        }
        reasons = []

        # Price at lower band + oversold RSI = strong buy
        if current_price <= lower[-1] and current_rsi < 35:
            reasons.append(f"Price at lower BB ({current_price:.5f}) + RSI oversold ({current_rsi:.2f})")
            return StrategySignal('CALL', 0.90, 'bollinger_rsi_combo', reasons, indicators)

        # Price at upper band + overbought RSI = strong sell
        if current_price >= upper[-1] and current_rsi > 65:
            reasons.append(f"Price at upper BB ({current_price:.5f}) + RSI overbought ({current_rsi:.2f})")
            return StrategySignal('PUT', 0.90, 'bollinger_rsi_combo', reasons, indicators)

        return None

    def stochastic_strategy(self, highs: np.ndarray, lows: np.ndarray,
                           closes: np.ndarray) -> Optional[StrategySignal]:
        """
        Stochastic Oscillator for momentum reversals
        """
        if len(closes) < 14:
            return None

        if HAS_TALIB:
            slowk, slowd = talib.STOCH(highs, lows, closes,
                                       fastk_period=14, slowk_period=3, slowd_period=3)
        else:
            slowk, slowd = self._calculate_stochastic(highs, lows, closes, 14, 3, 3)

        indicators = {'stoch_k': slowk[-1], 'stoch_d': slowd[-1]}
        reasons = []

        # Oversold crossover
        if len(slowk) >= 2:
            if slowk[-2] < slowd[-2] and slowk[-1] > slowd[-1] and slowk[-1] < 20:
                reasons.append(f"Stochastic bullish crossover in oversold zone ({slowk[-1]:.2f})")
                return StrategySignal('CALL', 0.80, 'stochastic', reasons, indicators)

            # Overbought crossover
            if slowk[-2] > slowd[-2] and slowk[-1] < slowd[-1] and slowk[-1] > 80:
                reasons.append(f"Stochastic bearish crossover in overbought zone ({slowk[-1]:.2f})")
                return StrategySignal('PUT', 0.80, 'stochastic', reasons, indicators)

        return None

    def trend_alignment_strategy(self, closes: np.ndarray) -> Optional[StrategySignal]:
        """
        Multi-timeframe trend alignment using EMAs
        """
        if len(closes) < 50:
            return None

        # Multiple EMAs for trend detection
        if HAS_TALIB:
            ema_fast = talib.EMA(closes, timeperiod=8)
            ema_medium = talib.EMA(closes, timeperiod=21)
            ema_slow = talib.EMA(closes, timeperiod=50)
        else:
            ema_fast = self._calculate_ema(closes, 8)
            ema_medium = self._calculate_ema(closes, 21)
            ema_slow = self._calculate_ema(closes, 50)

        indicators = {
            'ema_8': ema_fast[-1],
            'ema_21': ema_medium[-1],
            'ema_50': ema_slow[-1]
        }
        reasons = []

        # Strong uptrend alignment
        if ema_fast[-1] > ema_medium[-1] > ema_slow[-1] and closes[-1] > ema_fast[-1]:
            reasons.append("All EMAs aligned for uptrend")
            return StrategySignal('CALL', 0.75, 'trend_alignment', reasons, indicators)

        # Strong downtrend alignment
        if ema_fast[-1] < ema_medium[-1] < ema_slow[-1] and closes[-1] < ema_fast[-1]:
            reasons.append("All EMAs aligned for downtrend")
            return StrategySignal('PUT', 0.75, 'trend_alignment', reasons, indicators)

        return None

    def support_resistance_strategy(self, closes: np.ndarray, highs: np.ndarray,
                                    lows: np.ndarray) -> Optional[StrategySignal]:
        """
        Support and resistance level breakout detection
        """
        if len(closes) < 30:
            return None

        # Find recent support and resistance levels
        lookback = 20
        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]

        resistance = np.percentile(recent_highs, 90)
        support = np.percentile(recent_lows, 10)

        current_price = closes[-1]

        indicators = {
            'resistance': resistance,
            'support': support,
            'current_price': current_price
        }
        reasons = []

        # Breakout above resistance
        if current_price > resistance and closes[-2] <= resistance:
            reasons.append(f"Breakout above resistance {resistance:.5f}")
            return StrategySignal('CALL', 0.75, 'support_resistance', reasons, indicators)

        # Breakdown below support
        if current_price < support and closes[-2] >= support:
            reasons.append(f"Breakdown below support {support:.5f}")
            return StrategySignal('PUT', 0.75, 'support_resistance', reasons, indicators)

        # Bounce from support
        if abs(current_price - support) / support < 0.001 and closes[-1] > closes[-2]:
            reasons.append(f"Bounce from support {support:.5f}")
            return StrategySignal('CALL', 0.70, 'support_resistance', reasons, indicators)

        # Rejection from resistance
        if abs(current_price - resistance) / resistance < 0.001 and closes[-1] < closes[-2]:
            reasons.append(f"Rejection from resistance {resistance:.5f}")
            return StrategySignal('PUT', 0.70, 'support_resistance', reasons, indicators)

        return None

    def _aggregate_signals(self, signals: List[StrategySignal]) -> StrategySignal:
        """
        Aggregate multiple strategy signals into a final decision
        """
        if not signals:
            return StrategySignal(
                direction='NEUTRAL',
                confidence=0.0,
                strategy_name='no_signals',
                reasons=['No strategy generated a signal'],
                indicators={}
            )

        # Count strategies voting in each direction
        call_signals = [s for s in signals if s.direction == 'CALL']
        put_signals = [s for s in signals if s.direction == 'PUT']

        call_count = len(call_signals)
        put_count = len(put_signals)

        # Calculate weighted scores
        call_score = sum(s.confidence for s in call_signals)
        put_score = sum(s.confidence for s in put_signals)

        # Collect all reasons and indicators
        all_reasons = []
        all_indicators = {}
        for sig in signals:
            # Only include reasons from strategies voting in winning direction
            all_indicators.update({f"{sig.strategy_name}_{k}": v for k, v in sig.indicators.items()})

        # IMPROVED: Require at least 2 strategies agreeing AND strong score
        # For real money trading, we need higher confidence
        min_strategies_required = 2
        min_score_required = 1.5  # At least 2 strategies with 0.75+ confidence each

        if call_count >= min_strategies_required and call_score > put_score and call_score >= min_score_required:
            # Calculate confidence as average of agreeing strategies
            avg_confidence = call_score / call_count
            # Boost confidence slightly if more strategies agree
            confluence_boost = min(0.05 * (call_count - 1), 0.15)
            final_confidence = min(0.95, avg_confidence + confluence_boost)

            # Only include reasons from CALL strategies
            all_reasons = [f"[{sig.strategy_name}] {r}" for sig in call_signals for r in sig.reasons]

            return StrategySignal('CALL', final_confidence, 'aggregated', all_reasons, all_indicators)

        elif put_count >= min_strategies_required and put_score > call_score and put_score >= min_score_required:
            # Calculate confidence as average of agreeing strategies
            avg_confidence = put_score / put_count
            # Boost confidence slightly if more strategies agree
            confluence_boost = min(0.05 * (put_count - 1), 0.15)
            final_confidence = min(0.95, avg_confidence + confluence_boost)

            # Only include reasons from PUT strategies
            all_reasons = [f"[{sig.strategy_name}] {r}" for sig in put_signals for r in sig.reasons]

            return StrategySignal('PUT', final_confidence, 'aggregated', all_reasons, all_indicators)

        else:
            # Log why signal was rejected for debugging
            rejection_reason = f"Insufficient confluence: {call_count} CALL ({call_score:.2f}), {put_count} PUT ({put_score:.2f})"
            return StrategySignal('NEUTRAL', 0.0, 'insufficient_confluence',
                                [rejection_reason], all_indicators)

    # ========== Fallback Implementations (when TA-Lib not available) ==========

    def _calculate_rsi(self, closes: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate RSI without TA-Lib"""
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gains = np.zeros_like(closes)
        avg_losses = np.zeros_like(closes)

        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])

        for i in range(period + 1, len(closes)):
            avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
            avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period

        rs = avg_gains / (avg_losses + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, closes: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate MACD without TA-Lib"""
        ema12 = self._calculate_ema(closes, 12)
        ema26 = self._calculate_ema(closes, 26)
        macd = ema12 - ema26
        signal = self._calculate_ema(macd, 9)
        histogram = macd - signal
        return macd, signal, histogram

    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA without TA-Lib"""
        ema = np.zeros_like(data)
        ema[0] = data[0]
        multiplier = 2 / (period + 1)

        for i in range(1, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]

        return ema

    def _calculate_bollinger_bands(self, closes: np.ndarray, period: int = 20,
                                   num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands without TA-Lib"""
        middle = np.zeros_like(closes)
        upper = np.zeros_like(closes)
        lower = np.zeros_like(closes)

        for i in range(period-1, len(closes)):
            window = closes[i-period+1:i+1]
            middle[i] = np.mean(window)
            std = np.std(window)
            upper[i] = middle[i] + num_std * std
            lower[i] = middle[i] - num_std * std

        return upper, middle, lower

    def _calculate_stochastic(self, highs: np.ndarray, lows: np.ndarray,
                             closes: np.ndarray, k_period: int, k_smooth: int,
                             d_smooth: int) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Stochastic Oscillator without TA-Lib"""
        # Fast %K
        fast_k = np.zeros_like(closes)
        for i in range(k_period-1, len(closes)):
            window_high = np.max(highs[i-k_period+1:i+1])
            window_low = np.min(lows[i-k_period+1:i+1])
            if window_high != window_low:
                fast_k[i] = 100 * (closes[i] - window_low) / (window_high - window_low)

        # Smooth %K
        slow_k = self._simple_moving_average(fast_k, k_smooth)

        # %D
        slow_d = self._simple_moving_average(slow_k, d_smooth)

        return slow_k, slow_d

    def _simple_moving_average(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate simple moving average"""
        sma = np.zeros_like(data)
        for i in range(period-1, len(data)):
            sma[i] = np.mean(data[i-period+1:i+1])
        return sma
