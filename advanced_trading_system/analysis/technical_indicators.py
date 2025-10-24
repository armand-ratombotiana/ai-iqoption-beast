"""
Technical Indicators Library
Calculates various technical indicators for market analysis
"""
import numpy as np
from typing import List, Dict, Tuple, Optional


class TechnicalIndicators:
    """Calculate technical indicators from price data"""

    @staticmethod
    def rsi(candles: List[Dict], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(candles) < period + 1:
            return 50.0  # Default neutral

        closes = [c['close'] for c in candles[-(period + 1):]]
        deltas = np.diff(closes)

        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:]) if len(gains) >= period else 0
        avg_loss = np.mean(losses[-period:]) if len(losses) >= period else 0

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    @staticmethod
    def macd(candles: List[Dict], fast: int = 12, slow: int = 26,
             signal: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(candles) < slow:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}

        closes = np.array([c['close'] for c in candles])

        # Calculate EMAs
        ema_fast = TechnicalIndicators._ema(closes, fast)
        ema_slow = TechnicalIndicators._ema(closes, slow)

        macd_line = ema_fast - ema_slow

        # Signal line (EMA of MACD)
        macd_values = macd_line[-signal:] if len(macd_line) >= signal else macd_line
        signal_line = np.mean(macd_values)  # Simplified

        histogram = macd_line[-1] - signal_line

        return {
            'macd': round(float(macd_line[-1]), 6),
            'signal': round(float(signal_line), 6),
            'histogram': round(float(histogram), 6)
        }

    @staticmethod
    def bollinger_bands(candles: List[Dict], period: int = 20,
                       std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(candles) < period:
            current = candles[-1]['close'] if candles else 0
            return {
                'upper': current,
                'middle': current,
                'lower': current,
                'position': 0.5
            }

        closes = np.array([c['close'] for c in candles[-period:]])
        middle = np.mean(closes)
        std = np.std(closes)

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        current_price = candles[-1]['close']
        # Position: 0 = at lower band, 0.5 = at middle, 1 = at upper band
        if upper != lower:
            position = (current_price - lower) / (upper - lower)
        else:
            position = 0.5

        return {
            'upper': round(float(upper), 6),
            'middle': round(float(middle), 6),
            'lower': round(float(lower), 6),
            'position': round(float(position), 2)
        }

    @staticmethod
    def ema(candles: List[Dict], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(candles) < period:
            return candles[-1]['close'] if candles else 0

        closes = np.array([c['close'] for c in candles])
        ema_val = TechnicalIndicators._ema(closes, period)
        return round(float(ema_val[-1]), 6)

    @staticmethod
    def sma(candles: List[Dict], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(candles) < period:
            return candles[-1]['close'] if candles else 0

        closes = [c['close'] for c in candles[-period:]]
        return round(float(np.mean(closes)), 6)

    @staticmethod
    def atr(candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range (volatility indicator)"""
        if len(candles) < period + 1:
            return 0.0

        true_ranges = []
        for i in range(-(period + 1), -1):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_close = candles[i - 1]['close'] if i > 0 else candles[i]['close']

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        return round(float(np.mean(true_ranges)), 6)

    @staticmethod
    def stochastic(candles: List[Dict], k_period: int = 14,
                   d_period: int = 3) -> Dict[str, float]:
        """Calculate Stochastic Oscillator"""
        if len(candles) < k_period:
            return {'k': 50.0, 'd': 50.0}

        recent_candles = candles[-k_period:]

        current_close = recent_candles[-1]['close']
        lowest_low = min([c['low'] for c in recent_candles])
        highest_high = max([c['high'] for c in recent_candles])

        if highest_high != lowest_low:
            k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        else:
            k = 50.0

        # Simplified %D (SMA of %K)
        d = k  # In full implementation, this would be SMA of last d_period %K values

        return {
            'k': round(float(k), 2),
            'd': round(float(d), 2)
        }

    @staticmethod
    def adx(candles: List[Dict], period: int = 14) -> float:
        """Calculate Average Directional Index (trend strength)"""
        if len(candles) < period + 1:
            return 0.0

        # Simplified ADX calculation
        # Full implementation would use +DI, -DI, and smoothing

        # Calculate True Range and Directional Movement
        plus_dm = []
        minus_dm = []
        tr_values = []

        for i in range(-(period + 1), -1):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_high = candles[i - 1]['high']
            prev_low = candles[i - 1]['low']
            prev_close = candles[i - 1]['close']

            # True Range
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_values.append(tr)

            # Directional Movement
            up_move = high - prev_high
            down_move = prev_low - low

            plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0)
            minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0)

        # Simplified ADX (normally uses smoothing and DX calculation)
        avg_tr = np.mean(tr_values)
        avg_plus_dm = np.mean(plus_dm)
        avg_minus_dm = np.mean(minus_dm)

        if avg_tr > 0:
            plus_di = (avg_plus_dm / avg_tr) * 100
            minus_di = (avg_minus_dm / avg_tr) * 100
            dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        else:
            dx = 0

        return round(float(dx), 2)

    @staticmethod
    def cci(candles: List[Dict], period: int = 20) -> float:
        """Calculate Commodity Channel Index"""
        if len(candles) < period:
            return 0.0

        recent = candles[-period:]
        typical_prices = [(c['high'] + c['low'] + c['close']) / 3 for c in recent]

        sma_tp = np.mean(typical_prices)
        mean_deviation = np.mean([abs(tp - sma_tp) for tp in typical_prices])

        if mean_deviation > 0:
            cci = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)
        else:
            cci = 0

        return round(float(cci), 2)

    @staticmethod
    def williams_r(candles: List[Dict], period: int = 14) -> float:
        """Calculate Williams %R"""
        if len(candles) < period:
            return -50.0

        recent = candles[-period:]
        highest_high = max([c['high'] for c in recent])
        lowest_low = min([c['low'] for c in recent])
        current_close = recent[-1]['close']

        if highest_high != lowest_low:
            wr = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        else:
            wr = -50.0

        return round(float(wr), 2)

    @staticmethod
    def identify_trend(candles: List[Dict], period: int = 20) -> str:
        """Identify market trend based on moving averages"""
        if len(candles) < period:
            return 'neutral'

        sma_short = TechnicalIndicators.sma(candles, period // 2)
        sma_long = TechnicalIndicators.sma(candles, period)

        current_price = candles[-1]['close']

        if current_price > sma_short > sma_long:
            return 'uptrend'
        elif current_price < sma_short < sma_long:
            return 'downtrend'
        else:
            return 'sideways'

    @staticmethod
    def calculate_volatility(candles: List[Dict], period: int = 20) -> Tuple[str, float]:
        """Calculate volatility classification and value"""
        if len(candles) < period:
            return 'unknown', 0.0

        atr_value = TechnicalIndicators.atr(candles, period)
        current_price = candles[-1]['close']

        # Volatility as percentage of price
        volatility_pct = (atr_value / current_price * 100) if current_price > 0 else 0

        if volatility_pct < 0.5:
            classification = 'low'
        elif volatility_pct < 1.5:
            classification = 'medium'
        else:
            classification = 'high'

        return classification, round(volatility_pct, 2)

    @staticmethod
    def find_support_resistance(candles: List[Dict], period: int = 50) -> Tuple[float, float]:
        """Find support and resistance levels"""
        if len(candles) < period:
            current = candles[-1]['close'] if candles else 0
            return current * 0.99, current * 1.01

        recent = candles[-period:]

        # Simple approach: use highest high and lowest low
        highs = [c['high'] for c in recent]
        lows = [c['low'] for c in recent]

        resistance = max(highs)
        support = min(lows)

        return round(support, 6), round(resistance, 6)

    @staticmethod
    def detect_candlestick_pattern(candles: List[Dict]) -> str:
        """Detect basic candlestick patterns"""
        if len(candles) < 2:
            return 'none'

        current = candles[-1]
        previous = candles[-2]

        current_body = abs(current['close'] - current['open'])
        current_range = current['high'] - current['low']
        prev_body = abs(previous['close'] - previous['open'])

        # Doji
        if current_body < (current_range * 0.1):
            return 'doji'

        # Bullish Engulfing
        if (previous['close'] < previous['open'] and  # Previous bearish
            current['close'] > current['open'] and     # Current bullish
            current['open'] < previous['close'] and
            current['close'] > previous['open']):
            return 'bullish_engulfing'

        # Bearish Engulfing
        if (previous['close'] > previous['open'] and  # Previous bullish
            current['close'] < current['open'] and     # Current bearish
            current['open'] > previous['close'] and
            current['close'] < previous['open']):
            return 'bearish_engulfing'

        # Hammer (bullish)
        lower_shadow = min(current['open'], current['close']) - current['low']
        upper_shadow = current['high'] - max(current['open'], current['close'])
        if (lower_shadow > current_body * 2 and
            upper_shadow < current_body * 0.5 and
            current['close'] > current['open']):
            return 'hammer'

        # Shooting Star (bearish)
        if (upper_shadow > current_body * 2 and
            lower_shadow < current_body * 0.5 and
            current['close'] < current['open']):
            return 'shooting_star'

        return 'none'

    @staticmethod
    def volume_analysis(candles: List[Dict], period: int = 20) -> Tuple[float, str]:
        """Analyze volume trends"""
        if len(candles) < period:
            current_vol = candles[-1].get('volume', 0) if candles else 0
            return current_vol, 'neutral'

        volumes = [c.get('volume', 0) for c in candles[-period:]]
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]

        # Volume trend
        if current_volume > avg_volume * 1.5:
            trend = 'high'
        elif current_volume < avg_volume * 0.5:
            trend = 'low'
        else:
            trend = 'normal'

        return round(float(avg_volume), 2), trend

    @staticmethod
    def _ema(values: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA using pandas-style calculation"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(values)
        ema[0] = values[0]

        for i in range(1, len(values)):
            ema[i] = alpha * values[i] + (1 - alpha) * ema[i - 1]

        return ema
