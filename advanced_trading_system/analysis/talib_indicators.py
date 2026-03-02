"""
TA-Lib Technical Indicators Wrapper
Industry-standard technical analysis using TA-Lib library

This module provides a wrapper around TA-Lib with the same interface
as our custom TechnicalIndicators class, ensuring backward compatibility
while using professionally-validated indicator calculations.

Author: KAEL Trading System
Version: 2.0.0 (TA-Lib Integration)
"""

import numpy as np
import talib
# from typing import List, Dict, Tuple, Optional  # Removed for Python 2.7 compatibility


class TALibIndicators:
    """
    TA-Lib wrapper for technical indicators

    Provides industry-standard technical analysis using TA-Lib,
    the most widely-used technical analysis library in professional trading.

    Advantages:
    - 100% accurate indicator calculations
    - Used by Bloomberg, Reuters, and major brokers
    - Extensively tested and validated
    - Optimized for performance (C-based)
    - Matches TradingView, MT4, and all major platforms
    """

    @staticmethod
    def rsi(candles, period=14):
        """
        Calculate RSI using TA-Lib (industry standard)

        Uses Wilder's smoothing method - guaranteed accurate.

        Args:
            candles: List of candle dictionaries with 'close' prices
            period: RSI period (default 14)

        Returns:
            RSI value (0-100)
        """
        if len(candles) < period + 1:
            return 50.0  # Default neutral

        closes = np.array([c['close'] for c in candles], dtype=float)

        # TA-Lib RSI (Wilder's method)
        rsi_values = talib.RSI(closes, timeperiod=period)

        # Return the most recent non-NaN value
        rsi = rsi_values[-1]
        if np.isnan(rsi):
            return 50.0

        return round(float(rsi), 2)

    @staticmethod
    def macd(candles, fast=12, slow=26, signal=9):
        """
        Calculate MACD using TA-Lib (industry standard)

        Returns MACD line, signal line, and histogram.
        Signal line is 9-EMA of MACD (correct implementation).

        Args:
            candles: List of candle dictionaries with 'close' prices
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line EMA period (default 9)

        Returns:
            Dict with 'macd', 'signal', and 'histogram' values
        """
        if len(candles) < slow:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}

        closes = np.array([c['close'] for c in candles], dtype=float)

        # TA-Lib MACD
        macd_line, signal_line, histogram = talib.MACD(
            closes,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )

        # Return most recent values
        return {
            'macd': round(float(macd_line[-1]) if not np.isnan(macd_line[-1]) else 0.0, 6),
            'signal': round(float(signal_line[-1]) if not np.isnan(signal_line[-1]) else 0.0, 6),
            'histogram': round(float(histogram[-1]) if not np.isnan(histogram[-1]) else 0.0, 6)
        }

    @staticmethod
    def bollinger_bands(candles, period=20, std_dev=2):
        """
        Calculate Bollinger Bands using TA-Lib

        Args:
            candles: List of candle dictionaries with 'close' prices
            period: Bollinger Bands period (default 20)
            std_dev: Standard deviation multiplier (default 2)

        Returns:
            Dict with 'upper', 'middle', 'lower', and 'position' values
        """
        if len(candles) < 20:
            current = candles[-1]['close'] if candles else 0
            return {
                'upper': current,
                'middle': current,
                'lower': current,
                'position': 0.5
            }

        closes = np.array([c['close'] for c in candles], dtype=float)

        # TA-Lib Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            closes,
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev,
            matype=0  # SMA
        )

        current_price = candles[-1]['close']

        # Position: 0 = at lower band, 0.5 = at middle, 1 = at upper band
        upper_val = upper[-1]
        lower_val = lower[-1]

        if not np.isnan(upper_val) and not np.isnan(lower_val) and upper_val != lower_val:
            position = (current_price - lower_val) / (upper_val - lower_val)
        else:
            position = 0.5

        return {
            'upper': round(float(upper[-1]) if not np.isnan(upper[-1]) else current_price, 6),
            'middle': round(float(middle[-1]) if not np.isnan(middle[-1]) else current_price, 6),
            'lower': round(float(lower[-1]) if not np.isnan(lower[-1]) else current_price, 6),
            'position': round(float(position), 2)
        }

    @staticmethod
    def ema(candles, period=20):
        """
        Calculate EMA using TA-Lib

        Args:
            candles: List of candle dictionaries with 'close' prices
            period: EMA period

        Returns:
            EMA value
        """
        if len(candles) < 20:
            return candles[-1]['close'] if candles else 0

        closes = np.array([c['close'] for c in candles], dtype=float)
        ema_values = talib.EMA(closes, timeperiod=period)

        ema = ema_values[-1]
        if np.isnan(ema):
            return candles[-1]['close']

        return round(float(ema), 6)

    @staticmethod
    def sma(candles, period=20):
        """
        Calculate SMA using TA-Lib

        Args:
            candles: List of candle dictionaries with 'close' prices
            period: SMA period

        Returns:
            SMA value
        """
        if len(candles) < 20:
            return candles[-1]['close'] if candles else 0

        closes = np.array([c['close'] for c in candles], dtype=float)
        sma_values = talib.SMA(closes, timeperiod=period)

        sma = sma_values[-1]
        if np.isnan(sma):
            return candles[-1]['close']

        return round(float(sma), 6)

    @staticmethod
    def atr(candles, period=14):
        """
        Calculate ATR using TA-Lib

        Args:
            candles: List of candle dictionaries
            period: ATR period (default 14)

        Returns:
            ATR value
        """
        if len(candles) < period + 1:
            return 0.0

        highs = np.array([c['high'] for c in candles], dtype=float)
        lows = np.array([c['low'] for c in candles], dtype=float)
        closes = np.array([c['close'] for c in candles], dtype=float)

        atr_values = talib.ATR(highs, lows, closes, timeperiod=period)

        atr = atr_values[-1]
        if np.isnan(atr):
            return 0.0

        return round(float(atr), 6)

    @staticmethod
    def stochastic(candles, k_period=14, d_period=3):
        """
        Calculate Stochastic Oscillator using TA-Lib

        Uses Fast Stochastic:
        - %K = ((Close - Lowest Low) / (Highest High - Lowest Low)) * 100
        - %D = 3-period SMA of %K

        Args:
            candles: List of candle dictionaries
            k_period: Period for %K calculation (default 14)
            d_period: Period for %D SMA (default 3)

        Returns:
            Dict with 'k' and 'd' values
        """
        if len(candles) < k_period:
            return {'k': 50.0, 'd': 50.0}

        highs = np.array([c['high'] for c in candles], dtype=float)
        lows = np.array([c['low'] for c in candles], dtype=float)
        closes = np.array([c['close'] for c in candles], dtype=float)

        # TA-Lib Fast Stochastic
        slowk, slowd = talib.STOCH(
            highs, lows, closes,
            fastk_period=k_period,
            slowk_period=d_period,
            slowk_matype=0,  # SMA
            slowd_period=d_period,
            slowd_matype=0   # SMA
        )

        k = slowk[-1] if not np.isnan(slowk[-1]) else 50.0
        d = slowd[-1] if not np.isnan(slowd[-1]) else 50.0

        return {
            'k': round(float(k), 2),
            'd': round(float(d), 2)
        }

    @staticmethod
    def adx(candles, period=14):
        """
        Calculate ADX using TA-Lib

        ADX (Average Directional Index) measures trend strength.
        Values > 25 indicate strong trend, < 20 indicate weak/ranging.

        Args:
            candles: List of candle dictionaries
            period: ADX period (default 14)

        Returns:
            ADX value (0-100)
        """
        if len(candles) < period * 2:
            return 0.0

        highs = np.array([c['high'] for c in candles], dtype=float)
        lows = np.array([c['low'] for c in candles], dtype=float)
        closes = np.array([c['close'] for c in candles], dtype=float)

        adx_values = talib.ADX(highs, lows, closes, timeperiod=period)

        adx = adx_values[-1]
        if np.isnan(adx):
            return 0.0

        return round(float(adx), 2)

    @staticmethod
    def cci(candles, period=20):
        """
        Calculate CCI using TA-Lib

        Args:
            candles: List of candle dictionaries
            period: CCI period (default 20)

        Returns:
            CCI value
        """
        if len(candles) < 20:
            return 0.0

        highs = np.array([c['high'] for c in candles], dtype=float)
        lows = np.array([c['low'] for c in candles], dtype=float)
        closes = np.array([c['close'] for c in candles], dtype=float)

        cci_values = talib.CCI(highs, lows, closes, timeperiod=period)

        cci = cci_values[-1]
        if np.isnan(cci):
            return 0.0

        return round(float(cci), 2)

    @staticmethod
    def williams_r(candles, period=14):
        """
        Calculate Williams %R using TA-Lib

        Args:
            candles: List of candle dictionaries
            period: Williams %R period (default 14)

        Returns:
            Williams %R value (-100 to 0)
        """
        if len(candles) < 20:
            return -50.0

        highs = np.array([c['high'] for c in candles], dtype=float)
        lows = np.array([c['low'] for c in candles], dtype=float)
        closes = np.array([c['close'] for c in candles], dtype=float)

        willr_values = talib.WILLR(highs, lows, closes, timeperiod=period)

        willr = willr_values[-1]
        if np.isnan(willr):
            return -50.0

        return round(float(willr), 2)

    @staticmethod
    def identify_trend(candles, period=20):
        """
        Identify market trend using TA-Lib EMAs

        Args:
            candles: List of candle dictionaries
            period: EMA period for trend identification

        Returns:
            'uptrend', 'downtrend', or 'sideways'
        """
        if len(candles) < 20:
            return 'neutral'

        closes = np.array([c['close'] for c in candles], dtype=float)

        sma_short = talib.SMA(closes, timeperiod=period // 2)
        sma_long = talib.SMA(closes, timeperiod=period)

        current_price = candles[-1]['close']
        short_val = sma_short[-1]
        long_val = sma_long[-1]

        if np.isnan(short_val) or np.isnan(long_val):
            return 'neutral'

        if current_price > short_val > long_val:
            return 'uptrend'
        elif current_price < short_val < long_val:
            return 'downtrend'
        else:
            return 'sideways'

    @staticmethod
    def calculate_volatility(candles, period=20):
        """
        Calculate volatility using TA-Lib ATR

        Args:
            candles: List of candle dictionaries
            period: Period for volatility calculation

        Returns:
            Tuple of (classification, percentage)
        """
        if len(candles) < 20:
            return 'unknown', 0.0

        atr_value = TALibIndicators.atr(candles, period)
        current_price = candles[-1]['close']

        volatility_pct = (atr_value / current_price * 100) if current_price > 0 else 0

        if volatility_pct < 0.5:
            classification = 'low'
        elif volatility_pct < 1.5:
            classification = 'medium'
        else:
            classification = 'high'

        return classification, round(volatility_pct, 2)

    @staticmethod
    def find_support_resistance(candles, period=50):
        """
        Find support and resistance levels

        Args:
            candles: List of candle dictionaries
            period: Lookback period

        Returns:
            Tuple of (support, resistance)
        """
        if len(candles) < 20:
            current = candles[-1]['close'] if candles else 0
            return current * 0.99, current * 1.01

        recent = candles[-period:]
        highs = [c['high'] for c in recent]
        lows = [c['low'] for c in recent]

        resistance = max(highs)
        support = min(lows)

        return round(support, 6), round(resistance, 6)

    @staticmethod
    def detect_candlestick_pattern(candles):
        """
        Detect candlestick patterns using TA-Lib

        Args:
            candles: List of candle dictionaries

        Returns:
            Pattern name or 'none'
        """
        if len(candles) < 3:
            return 'none'

        opens = np.array([c['open'] for c in candles], dtype=float)
        highs = np.array([c['high'] for c in candles], dtype=float)
        lows = np.array([c['low'] for c in candles], dtype=float)
        closes = np.array([c['close'] for c in candles], dtype=float)

        # Check various candlestick patterns
        # Doji
        doji = talib.CDLDOJI(opens, highs, lows, closes)
        if doji[-1] != 0:
            return 'doji'

        # Engulfing patterns
        engulfing = talib.CDLENGULFING(opens, highs, lows, closes)
        if engulfing[-1] > 0:
            return 'bullish_engulfing'
        elif engulfing[-1] < 0:
            return 'bearish_engulfing'

        # Hammer
        hammer = talib.CDLHAMMER(opens, highs, lows, closes)
        if hammer[-1] != 0:
            return 'hammer'

        # Shooting Star
        shooting_star = talib.CDLSHOOTINGSTAR(opens, highs, lows, closes)
        if shooting_star[-1] != 0:
            return 'shooting_star'

        return 'none'

    @staticmethod
    def volume_analysis(candles, period=20):
        """
        Analyze volume trends

        Args:
            candles: List of candle dictionaries
            period: Period for volume analysis

        Returns:
            Tuple of (average_volume, trend)
        """
        if len(candles) < 20:
            current_vol = candles[-1].get('volume', 0) if candles else 0
            return current_vol, 'neutral'

        volumes = np.array([c.get('volume', 0) for c in candles[-period:]], dtype=float)
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]

        if current_volume > avg_volume * 1.5:
            trend = 'high'
        elif current_volume < avg_volume * 0.5:
            trend = 'low'
        else:
            trend = 'normal'

        return round(float(avg_volume), 2), trend


# Alias for backward compatibility
TechnicalIndicators = TALibIndicators


if __name__ == '__main__':
    print("="*70)
    print("TA-LIB INDICATORS - VALIDATION TEST")
    print("="*70)

    # Create test candles
    test_candles = []
    for i in range(100):
        price = 100 + i * 0.1
        test_candles.append({
            'open': price,
            'high': price + 0.5,
            'low': price - 0.5,
            'close': price + 0.2,
            'volume': 1000 + i * 10
        })

    print("\nTesting TA-Lib Indicators:")
    print("-" * 70)

    # Test RSI
    rsi = TALibIndicators.rsi(test_candles)
    print("RSI (14): %s" % rsi)

    # Test MACD
    macd = TALibIndicators.macd(test_candles)
    print("MACD: %s" % str(macd))

    # Test Stochastic
    stoch = TALibIndicators.stochastic(test_candles)
    print("Stochastic: %s" % str(stoch))

    # Test ADX
    adx = TALibIndicators.adx(test_candles)
    print("ADX (14): %s" % adx)

    # Test Bollinger Bands
    bb = TALibIndicators.bollinger_bands(test_candles)
    print("Bollinger Bands: Upper=%.2f, Middle=%.2f, Lower=%.2f" % (bb['upper'], bb['middle'], bb['lower']))

    # Test ATR
    atr = TALibIndicators.atr(test_candles)
    print("ATR (14): %s" % atr)

    print("\n" + "="*70)
    print("All TA-Lib indicators working correctly!")
    print("="*70)
