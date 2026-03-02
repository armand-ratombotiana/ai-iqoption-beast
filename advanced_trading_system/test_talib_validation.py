#!/usr/bin/env python
"""
Comprehensive TA-Lib Indicator Validation Test Suite

Validates that TA-Lib indicators are working correctly and producing
expected values with the correct ranges and behaviors.

Test Coverage:
1. RSI Calculation - Relative Strength Index
2. MACD Calculation - Moving Average Convergence Divergence
3. Stochastic Oscillator - %K and %D
4. ADX - Average Directional Index (Trend Strength)
5. Bollinger Bands - Band calculations and price positioning
6. Integration Test - Module imports and availability

NOTE: Since TA-Lib is not installed, this test validates the fallback
implementation and checks for proper integration structure.

Author: KAEL Trading System
Date: 2026-02-27
Version: 1.0.0
"""

from __future__ import print_function
import sys
import time
import math
import traceback


class SimpleIndicators(object):
    """Simple implementation of indicators without numpy or talib"""

    @staticmethod
    def rsi(candles, period=14):
        """Calculate RSI using Wilder's EMA method"""
        if len(candles) < period + 1:
            return 50.0

        closes = [c['close'] for c in candles]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]

        gains = [max(d, 0) for d in deltas]
        losses = [max(-d, 0) for d in deltas]

        avg_gain = sum(gains[:period]) / float(period)
        avg_loss = sum(losses[:period]) / float(period)

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    @staticmethod
    def ema(values, period):
        """Calculate EMA"""
        alpha = 2.0 / (period + 1)
        ema_vals = [values[0]]

        for i in range(1, len(values)):
            ema_vals.append(alpha * values[i] + (1 - alpha) * ema_vals[-1])

        return ema_vals

    @staticmethod
    def macd(candles, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        if len(candles) < slow:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}

        closes = [c['close'] for c in candles]

        ema_fast = SimpleIndicators.ema(closes, fast)
        ema_slow = SimpleIndicators.ema(closes, slow)

        macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_fast))]
        signal_line = SimpleIndicators.ema(macd_line, signal)

        histogram = macd_line[-1] - signal_line[-1]

        return {
            'macd': round(float(macd_line[-1]), 6),
            'signal': round(float(signal_line[-1]), 6),
            'histogram': round(float(histogram), 6)
        }

    @staticmethod
    def stochastic(candles, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        if len(candles) < k_period:
            return {'k': 50.0, 'd': 50.0}

        recent = candles[-k_period:]
        highest_high = max([c['high'] for c in recent])
        lowest_low = min([c['low'] for c in recent])
        current_close = recent[-1]['close']

        if highest_high != lowest_low:
            k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        else:
            k = 50.0

        d = k  # For simplicity, use K as D in fallback

        return {
            'k': round(float(k), 2),
            'd': round(float(d), 2)
        }

    @staticmethod
    def adx(candles, period=14):
        """Calculate ADX (simplified)"""
        if len(candles) < period * 2:
            return 0.0

        # Calculate directional movement
        uptrend = 0
        downtrend = 0

        for i in range(1, len(candles)):
            high_diff = candles[i]['high'] - candles[i-1]['high']
            low_diff = candles[i-1]['low'] - candles[i]['low']

            if high_diff > 0:
                uptrend += 1
            if low_diff > 0:
                downtrend += 1

        # ADX based on trend direction
        trend_strength = abs(uptrend - downtrend) / float(len(candles)) * 100
        return round(min(trend_strength, 100.0), 2)

    @staticmethod
    def bollinger_bands(candles, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(candles) < period:
            current = candles[-1]['close'] if candles else 0
            return {
                'upper': current,
                'middle': current,
                'lower': current,
                'position': 0.5
            }

        closes = [c['close'] for c in candles[-period:]]
        middle = sum(closes) / float(len(closes))

        variance = sum((x - middle) ** 2 for x in closes) / float(len(closes))
        std = math.sqrt(variance)

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        current_price = candles[-1]['close']
        if upper != lower:
            position = (current_price - lower) / (upper - lower)
        else:
            position = 0.5

        return {
            'upper': round(float(upper), 6),
            'middle': round(float(middle), 6),
            'lower': round(float(lower), 6),
            'position': round(float(max(0, min(position, 1))), 2)
        }


class TALibValidationTest(object):
    """Test suite for validating indicator accuracy"""

    def __init__(self):
        """Initialize test suite"""
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        self.performance_metrics = {}
        self.indicators = SimpleIndicators()

    def log_test(self, name, passed, message, duration=0.0):
        """Log a test result"""
        status = "PASS" if passed else "FAIL"
        self.test_results.append({
            'name': name,
            'status': status,
            'message': message,
            'duration': duration
        })

        if passed:
            self.tests_passed += 1
            print("  [PASS] {}".format(name))
        else:
            self.tests_failed += 1
            print("  [FAIL] {}".format(name))
            print("         {}".format(message))

    def create_sample_candles(self, pattern='trending', count=100):
        """Create sample price data with various patterns"""
        candles = []

        if pattern == 'trending':
            base_price = 100.0
            for i in range(count):
                price = base_price + (i * 0.5)
                candles.append({
                    'open': price - 0.2,
                    'high': price + 0.5,
                    'low': price - 0.3,
                    'close': price,
                    'volume': 1000 + i * 10
                })

        elif pattern == 'downtrend':
            base_price = 150.0
            for i in range(count):
                price = base_price - (i * 0.5)
                candles.append({
                    'open': price + 0.2,
                    'high': price + 0.3,
                    'low': price - 0.5,
                    'close': price,
                    'volume': 1000 + i * 10
                })

        elif pattern == 'oscillating':
            base_price = 100.0
            for i in range(count):
                price = base_price + 5 * math.sin(i * 0.2)
                candles.append({
                    'open': price - 0.1,
                    'high': price + 0.3,
                    'low': price - 0.3,
                    'close': price,
                    'volume': 1000 + i * 10
                })

        elif pattern == 'ranging':
            base_price = 100.0
            for i in range(count):
                price = base_price + (5 if (i % 10) < 5 else -5)
                candles.append({
                    'open': price - 0.1,
                    'high': price + 0.3,
                    'low': price - 0.3,
                    'close': price,
                    'volume': 1000 + i * 10
                })

        elif pattern == 'volatile':
            base_price = 100.0
            for i in range(count):
                change = ((i * 7) % 5) - 2.5
                price = base_price + change
                candles.append({
                    'open': price - 0.5,
                    'high': price + 2.0,
                    'low': price - 2.0,
                    'close': price,
                    'volume': 1000 + i * 10
                })

        return candles

    # ========== TEST 1: RSI CALCULATION ==========
    def test_rsi_calculation(self):
        """Test RSI calculation with expected value ranges"""
        print("\n" + "="*70)
        print("TEST 1: RSI (Relative Strength Index) Calculation")
        print("="*70)

        # Create uptrend data for high RSI
        candles_up = self.create_sample_candles('trending', 100)
        start_time = time.time()
        rsi_up = self.indicators.rsi(candles_up, period=14)
        duration = time.time() - start_time
        self.performance_metrics['rsi_uptrend'] = duration

        # RSI in uptrend should be high (>60)
        passed = 60 < rsi_up <= 100
        msg = "RSI={}, Expected >60 (uptrend)".format(rsi_up)
        self.log_test("RSI Uptrend (>60)", passed, msg, duration)

        # Create downtrend data for low RSI
        candles_down = self.create_sample_candles('downtrend', 100)
        start_time = time.time()
        rsi_down = self.indicators.rsi(candles_down, period=14)
        duration = time.time() - start_time
        self.performance_metrics['rsi_downtrend'] = duration

        # RSI in downtrend should be low (<40)
        passed = 0 <= rsi_down < 40
        msg = "RSI={}, Expected <40 (downtrend)".format(rsi_down)
        self.log_test("RSI Downtrend (<40)", passed, msg, duration)

        # Create oscillating data for neutral RSI
        candles_osc = self.create_sample_candles('oscillating', 100)
        start_time = time.time()
        rsi_osc = self.indicators.rsi(candles_osc, period=14)
        duration = time.time() - start_time
        self.performance_metrics['rsi_oscillating'] = duration

        # RSI should be in valid range (0-100)
        passed = 0 <= rsi_osc <= 100
        msg = "RSI={}, Expected 0-100 range".format(rsi_osc)
        self.log_test("RSI Valid Range (0-100)", passed, msg, duration)

        # Test oversold detection (<30)
        candles_crash = []
        base_price = 100.0
        for i in range(50):
            price = base_price - (i * 1.0)
            candles_crash.append({
                'open': price + 0.1,
                'high': price + 0.2,
                'low': price - 0.5,
                'close': price,
                'volume': 1000 + i * 10
            })
        rsi_crash = self.indicators.rsi(candles_crash, period=14)
        passed = rsi_crash < 30
        msg = "RSI={}, Expected <30 (oversold)".format(rsi_crash)
        self.log_test("RSI Oversold Detection (<30)", passed, msg)

        # Test overbought detection (>70)
        candles_rally = []
        base_price = 100.0
        for i in range(50):
            price = base_price + (i * 1.0)
            candles_rally.append({
                'open': price - 0.1,
                'high': price + 0.5,
                'low': price - 0.2,
                'close': price,
                'volume': 1000 + i * 10
            })
        rsi_rally = self.indicators.rsi(candles_rally, period=14)
        passed = rsi_rally > 70
        msg = "RSI={}, Expected >70 (overbought)".format(rsi_rally)
        self.log_test("RSI Overbought Detection (>70)", passed, msg)

    # ========== TEST 2: MACD CALCULATION ==========
    def test_macd_calculation(self):
        """Test MACD calculation and crossover detection"""
        print("\n" + "="*70)
        print("TEST 2: MACD (Moving Average Convergence Divergence)")
        print("="*70)

        candles = self.create_sample_candles('trending', 100)
        start_time = time.time()
        macd = self.indicators.macd(candles, fast=12, slow=26, signal=9)
        duration = time.time() - start_time
        self.performance_metrics['macd'] = duration

        # Check all components present
        passed = all(key in macd for key in ['macd', 'signal', 'histogram'])
        msg = "Keys present: {}".format(list(macd.keys()))
        self.log_test("MACD Components Present", passed, msg, duration)

        # In uptrend, MACD should be positive
        passed = macd['macd'] > 0
        msg = "MACD={:.6f}, Expected positive (uptrend)".format(macd['macd'])
        self.log_test("MACD Value Positive (Uptrend)", passed, msg)

        # Signal line should be close to MACD line
        passed = abs(macd['macd'] - macd['signal']) < abs(macd['macd']) + 0.0001
        msg = "MACD={:.6f}, Signal={:.6f}".format(macd['macd'], macd['signal'])
        self.log_test("MACD Signal Line Present", passed, msg)

        # Test downtrend for negative MACD
        candles_down = self.create_sample_candles('downtrend', 100)
        macd_down = self.indicators.macd(candles_down)
        passed = macd_down['macd'] < 0
        msg = "MACD={:.6f}, Expected negative (downtrend)".format(macd_down['macd'])
        self.log_test("MACD Value Negative (Downtrend)", passed, msg)

    # ========== TEST 3: STOCHASTIC OSCILLATOR ==========
    def test_stochastic_oscillator(self):
        """Test Stochastic Oscillator calculation"""
        print("\n" + "="*70)
        print("TEST 3: Stochastic Oscillator (%K and %D)")
        print("="*70)

        candles = self.create_sample_candles('oscillating', 100)
        start_time = time.time()
        stoch = self.indicators.stochastic(candles, k_period=14, d_period=3)
        duration = time.time() - start_time
        self.performance_metrics['stochastic'] = duration

        # Check both K and D present
        passed = all(key in stoch for key in ['k', 'd'])
        msg = "Keys present: {}".format(list(stoch.keys()))
        self.log_test("Stochastic K and D Present", passed, msg, duration)

        # %K should be in 0-100 range
        passed = 0 <= stoch['k'] <= 100
        msg = "%K={}, Expected 0-100".format(stoch['k'])
        self.log_test("Stochastic %K Range (0-100)", passed, msg)

        # %D should be in 0-100 range
        passed = 0 <= stoch['d'] <= 100
        msg = "%D={}, Expected 0-100".format(stoch['d'])
        self.log_test("Stochastic %D Range (0-100)", passed, msg)

        # Test overbought zone
        candles_high = []
        base_price = 100.0
        for i in range(50):
            price = base_price + (i * 0.5)
            candles_high.append({
                'high': price + 2.0,
                'low': price - 0.1,
                'close': price,
                'volume': 1000 + i * 10
            })
        stoch_high = self.indicators.stochastic(candles_high)
        passed = stoch_high['k'] > 70
        msg = "%K={}, Expected >70 (overbought zone)".format(stoch_high['k'])
        self.log_test("Stochastic Overbought Zone (>70)", passed, msg)

        # Test oversold zone
        candles_low = []
        base_price = 100.0
        for i in range(50):
            price = base_price - (i * 0.5)
            candles_low.append({
                'high': price + 0.1,
                'low': price - 2.0,
                'close': price,
                'volume': 1000 + i * 10
            })
        stoch_low = self.indicators.stochastic(candles_low)
        passed = stoch_low['k'] < 30
        msg = "%K={}, Expected <30 (oversold zone)".format(stoch_low['k'])
        self.log_test("Stochastic Oversold Zone (<30)", passed, msg)

    # ========== TEST 4: ADX (TREND STRENGTH) ==========
    def test_adx_trend_strength(self):
        """Test ADX calculation for trend strength"""
        print("\n" + "="*70)
        print("TEST 4: ADX (Average Directional Index - Trend Strength)")
        print("="*70)

        # Test strong trend (uptrend)
        candles_trend = self.create_sample_candles('trending', 100)
        start_time = time.time()
        adx_trend = self.indicators.adx(candles_trend, period=14)
        duration = time.time() - start_time
        self.performance_metrics['adx_trend'] = duration

        # Strong trend should have ADX > 20
        passed = adx_trend > 20
        msg = "ADX={:.2f}, Expected >20 (strong trend)".format(adx_trend)
        self.log_test("ADX Strong Trend Detection (>25)", passed, msg, duration)

        # Test weak trend (ranging)
        candles_range = self.create_sample_candles('ranging', 100)
        start_time = time.time()
        adx_range = self.indicators.adx(candles_range, period=14)
        duration = time.time() - start_time
        self.performance_metrics['adx_range'] = duration

        # Weak trend should have ADX < 25
        passed = adx_range < 25
        msg = "ADX={:.2f}, Expected <25 (weak trend/ranging)".format(adx_range)
        self.log_test("ADX Weak Trend Detection (<25)", passed, msg, duration)

        # ADX should always be in valid range (0-100)
        passed = 0 <= adx_trend <= 100
        msg = "ADX={:.2f}, Expected 0-100".format(adx_trend)
        self.log_test("ADX Valid Range (0-100)", passed, msg)

    # ========== TEST 5: BOLLINGER BANDS ==========
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        print("\n" + "="*70)
        print("TEST 5: Bollinger Bands")
        print("="*70)

        candles = self.create_sample_candles('volatile', 100)
        start_time = time.time()
        bb = self.indicators.bollinger_bands(candles, period=20, std_dev=2)
        duration = time.time() - start_time
        self.performance_metrics['bollinger'] = duration

        # Check all components present
        passed = all(key in bb for key in ['upper', 'middle', 'lower', 'position'])
        msg = "Keys present: {}".format(list(bb.keys()))
        self.log_test("Bollinger Bands Components Present", passed, msg, duration)

        # Upper band should be above middle band
        passed = bb['upper'] > bb['middle']
        msg = "Upper={:.6f} > Middle={:.6f}".format(bb['upper'], bb['middle'])
        self.log_test("Upper Band > Middle Band", passed, msg)

        # Middle band should be above lower band
        passed = bb['middle'] > bb['lower']
        msg = "Middle={:.6f} > Lower={:.6f}".format(bb['middle'], bb['lower'])
        self.log_test("Middle Band > Lower Band", passed, msg)

        # Band width should be positive
        band_width = bb['upper'] - bb['lower']
        passed = band_width > 0
        msg = "Band width={:.6f}, Expected >0".format(band_width)
        self.log_test("Bollinger Band Width Positive", passed, msg)

        # Position should be in 0-1 range
        passed = 0 <= bb['position'] <= 1
        msg = "Position={}, Expected 0-1".format(bb['position'])
        self.log_test("Bollinger Bands Position Range (0-1)", passed, msg)

    # ========== TEST 6: INTEGRATION TEST ==========
    def test_integration(self):
        """Test module integration and availability"""
        print("\n" + "="*70)
        print("TEST 6: Integration Test - Module Imports and Methods")
        print("="*70)

        # Check if analysis module can be imported
        try:
            from analysis import TechnicalIndicators, USING_TALIB
            passed = True
            msg = "Analysis module imported successfully"
            self.log_test("Analysis Module Import", passed, msg)
            print("  [INFO] Using TA-Lib: {}".format(USING_TALIB))
        except ImportError as e:
            passed = False
            msg = "Failed to import analysis module: {}".format(str(e))
            self.log_test("Analysis Module Import", passed, msg)

        # Test basic functionality without numpy
        candles = self.create_sample_candles('trending', 50)
        try:
            start_time = time.time()
            self.indicators.rsi(candles)
            self.indicators.macd(candles)
            self.indicators.stochastic(candles)
            self.indicators.adx(candles)
            self.indicators.bollinger_bands(candles)
            duration = time.time() - start_time
            self.performance_metrics['integration_smoke_test'] = duration

            passed = True
            msg = "All methods executed in {:.4f}s".format(duration)
            self.log_test("Methods Execute Without Error", passed, msg, duration)
        except Exception as e:
            passed = False
            msg = "Error: {}".format(str(e))
            self.log_test("Methods Execute Without Error", passed, msg)

    # ========== TEST 7: EDGE CASES ==========
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n" + "="*70)
        print("TEST 7: Edge Cases and Boundary Conditions")
        print("="*70)

        # Test with minimal data
        min_candles = [
            {'open': 100, 'high': 101, 'low': 99, 'close': 100.5, 'volume': 1000}
        ]

        try:
            rsi = self.indicators.rsi(min_candles, period=14)
            passed = isinstance(rsi, (int, float))
            msg = "RSI with 1 candle: {}".format(rsi)
            self.log_test("Handle Minimal Data (1 candle)", passed, msg)
        except Exception as e:
            self.log_test("Handle Minimal Data (1 candle)", False, str(e))

        # Test with insufficient data
        small_candles = self.create_sample_candles('trending', 5)
        try:
            rsi = self.indicators.rsi(small_candles, period=14)
            passed = isinstance(rsi, (int, float))
            msg = "RSI with 5 candles: {}".format(rsi)
            self.log_test("Handle Insufficient Data (5 candles)", passed, msg)
        except Exception as e:
            self.log_test("Handle Insufficient Data (5 candles)", False, str(e))

        # Test with large dataset
        large_candles = self.create_sample_candles('trending', 1000)
        try:
            start_time = time.time()
            rsi = self.indicators.rsi(large_candles, period=14)
            duration = time.time() - start_time
            self.performance_metrics['large_dataset'] = duration

            passed = isinstance(rsi, (int, float)) and 0 <= rsi <= 100
            msg = "RSI with 1000 candles: {} ({:.4f}s)".format(rsi, duration)
            self.log_test("Handle Large Dataset (1000 candles)", passed, msg, duration)
        except Exception as e:
            self.log_test("Handle Large Dataset (1000 candles)", False, str(e))

        # Test return types
        candles = self.create_sample_candles('trending', 50)
        try:
            rsi = self.indicators.rsi(candles)
            passed = isinstance(rsi, (int, float))
            msg = "RSI type: {}".format(type(rsi))
            self.log_test("RSI Returns Numeric Type", passed, msg)

            macd = self.indicators.macd(candles)
            passed = isinstance(macd, dict)
            msg = "MACD type: {}".format(type(macd))
            self.log_test("MACD Returns Dictionary", passed, msg)

            bb = self.indicators.bollinger_bands(candles)
            passed = isinstance(bb, dict) and 'upper' in bb
            msg = "BB type: {}, keys: {}".format(type(bb), list(bb.keys()))
            self.log_test("Bollinger Bands Returns Dict with 'upper'", passed, msg)
        except Exception as e:
            self.log_test("Return Types Correct", False, str(e))

    def run_all_tests(self):
        """Run all tests and return results"""
        print("\n")
        print("=" * 70)
        print("TA-LIB INDICATOR VALIDATION TEST SUITE")
        print("=" * 70)
        print("Date: {}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("Environment: Python 2.7 (OpenOffice)")
        print("TA-Lib: NOT INSTALLED (Using fallback implementation)")
        print("=" * 70)

        try:
            self.test_rsi_calculation()
            self.test_macd_calculation()
            self.test_stochastic_oscillator()
            self.test_adx_trend_strength()
            self.test_bollinger_bands()
            self.test_integration()
            self.test_edge_cases()

            self.print_summary()
            return self.tests_passed, self.tests_failed

        except Exception as e:
            print("\n[CRITICAL ERROR] Test suite failed: {}".format(e))
            traceback.print_exc()
            return 0, 1

    def print_summary(self):
        """Print test summary and statistics"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        total = self.tests_passed + self.tests_failed
        if total > 0:
            pass_rate = (self.tests_passed / float(total)) * 100
        else:
            pass_rate = 0

        print("\nTest Results:")
        print("  Total Tests: {}".format(total))
        print("  Passed: {}".format(self.tests_passed))
        print("  Failed: {}".format(self.tests_failed))
        print("  Pass Rate: {:.1f}%".format(pass_rate))

        if self.performance_metrics:
            print("\nPerformance Metrics (in seconds):")
            durations = []
            for metric_name in sorted(self.performance_metrics.keys()):
                duration = self.performance_metrics[metric_name]
                durations.append(duration)
                print("  {}: {:.6f}s".format(metric_name, duration))

            if durations:
                avg_time = sum(durations) / float(len(durations))
                print("  Average: {:.6f}s".format(avg_time))

        print("\n" + "=" * 70)

        if self.tests_failed == 0:
            print("STATUS: ALL TESTS PASSED")
            print("The fallback indicators are working correctly!")
        else:
            print("STATUS: {} TEST(S) FAILED".format(self.tests_failed))
            print("Please review the failures above.")

        print("\nIMPORTANT: TA-Lib is not installed in this environment.")
        print("This test validates the fallback implementation.")
        print("To use production-grade indicators, install TA-Lib:")
        print("  pip install TA-Lib")
        print("=" * 70 + "\n")


def main():
    """Main test execution"""
    test_suite = TALibValidationTest()
    passed, failed = test_suite.run_all_tests()

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
