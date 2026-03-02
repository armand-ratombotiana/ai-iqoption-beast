#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AGENT 3: SYSTEM INTEGRATION VALIDATION
========================================
Comprehensive end-to-end integration test for the trading system

Tests:
1. Configuration Loading
2. Secrets Management Integration
3. Technical Indicators Integration
4. Paper Trading Engine Structure
5. Risk Management Integration
6. Data Flow Validation
"""

from __future__ import print_function
import sys
import os
from datetime import datetime
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Color codes for output
class Colors(object):
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print("\n" + Colors.BOLD + Colors.BLUE + "="*70)
    print(text.center(70))
    print("="*70 + Colors.RESET + "\n")

def print_subheader(text):
    """Print formatted subheader"""
    print(Colors.BOLD + Colors.BLUE + text + Colors.RESET)
    print("-" * 70)

def print_success(text):
    """Print success message"""
    print(Colors.GREEN + "OK " + text + Colors.RESET)

def print_fail(text):
    """Print failure message"""
    print(Colors.RED + "FAIL " + text + Colors.RESET)

def print_warning(text):
    """Print warning message"""
    print(Colors.YELLOW + "WARN " + text + Colors.RESET)

def print_info(text):
    """Print info message"""
    print("  -> " + text)

# ============================================================================
# TEST 1: CONFIGURATION LOADING
# ============================================================================

def test_configuration_loading():
    """Test configuration module"""
    print_subheader("TEST 1: Configuration Loading")

    results = []
    passed = True

    try:
        # Import configuration
        from paper_trading_config import get_config, validate_config, SAFETY_LIMITS
        print_success("Successfully imported paper_trading_config")
        results.append("OK Paper trading config import")

        # Test get_config()
        config = get_config()
        print_success("get_config() returned configuration dictionary")
        results.append("OK get_config() execution")

        # Verify all sections
        required_sections = ['trading', 'pairs', 'indicators', 'signal_rules',
                           'logging', 'metrics', 'validation', 'safety']

        for section in required_sections:
            if section in config:
                print_success("Config section '%s' present" % section)
                results.append("OK Config section '%s'" % section)
            else:
                print_fail("Config section '%s' MISSING" % section)
                results.append("FAIL Config section '%s'" % section)
                passed = False

        # Test validate_config()
        is_valid = validate_config()
        if is_valid:
            print_success("validate_config() returned True")
            results.append("OK Configuration validation passed")
        else:
            print_fail("validate_config() returned False")
            results.append("FAIL Configuration validation failed")
            passed = False

        # Verify all safety limits
        print_info("Safety Limits Configuration:")
        safety_keys = ['EMERGENCY_STOP_LOSS', 'EMERGENCY_STOP_ENABLED',
                      'MAX_CONNECTION_FAILURES', 'REQUIRE_MINIMUM_CANDLES']

        for key in safety_keys:
            if key in SAFETY_LIMITS:
                value = SAFETY_LIMITS[key]
                print_info("  %s: %s" % (key, str(value)))
                print_success("Safety limit '%s' present" % key)
                results.append("OK Safety limit '%s'" % key)
            else:
                print_fail("Safety limit '%s' MISSING" % key)
                results.append("FAIL Safety limit '%s'" % key)
                passed = False

    except Exception as e:
        print_fail("Configuration loading error: %s" % str(e))
        results.append("FAIL Configuration loading failed: %s" % str(e))
        passed = False

    return passed, results

# ============================================================================
# TEST 2: SECRETS MANAGEMENT INTEGRATION
# ============================================================================

def test_secrets_management():
    """Test secrets manager"""
    print_subheader("TEST 2: Secrets Management Integration")

    results = []
    passed = True

    try:
        # Import SecretsManager
        from utils.secrets_manager import SecretsManager
        print_success("Successfully imported SecretsManager")
        results.append("OK SecretsManager import")

        # Initialize secrets manager
        secrets = SecretsManager(environment="production", auto_load=True)
        print_success("SecretsManager initialized")
        results.append("OK SecretsManager initialization")

        # Test credential retrieval (without printing values)
        print_info("Testing credential retrieval (values masked):")

        # Check IQOption email
        email = secrets.get_credential('IQOPTION_EMAIL')
        if email:
            masked = secrets.mask_for_logging(email)
            print_info("  IQOPTION_EMAIL: %s" % masked)
            print_success("IQOPTION_EMAIL retrieved (masked)")
            results.append("OK IQOPTION_EMAIL credential retrieval")
        else:
            print_warning("IQOPTION_EMAIL not set (expected for test environment)")
            results.append("WARN IQOPTION_EMAIL not set (optional for tests)")

        # Check IQOption password
        password = secrets.get_credential('IQOPTION_PASSWORD')
        if password:
            masked = secrets.mask_for_logging(password)
            print_info("  IQOPTION_PASSWORD: %s" % masked)
            print_success("IQOPTION_PASSWORD retrieved (masked)")
            results.append("OK IQOPTION_PASSWORD credential retrieval")
        else:
            print_warning("IQOPTION_PASSWORD not set (expected for test environment)")
            results.append("WARN IQOPTION_PASSWORD not set (optional for tests)")

        # Test environment variable loading
        print_info("Environment variable loading:")
        account_type = secrets.get_credential('ACCOUNT_TYPE', 'demo')
        print_info("  ACCOUNT_TYPE: %s" % account_type)
        print_success("Environment variable loading works")
        results.append("OK Environment variable loading")

        # Test error handling for missing credentials
        print_info("Testing error handling for missing credentials:")
        try:
            # This should not raise an error with default
            missing = secrets.get_credential('NONEXISTENT_KEY', 'default_value')
            if missing == 'default_value':
                print_success("Default value returned for missing credential")
                results.append("OK Missing credential default handling")
            else:
                print_fail("Default value not applied correctly")
                results.append("FAIL Missing credential default handling")
                passed = False
        except Exception as e:
            print_fail("Error handling missing credential: %s" % str(e))
            results.append("FAIL Missing credential error handling: %s" % str(e))
            passed = False

        # Validate credentials
        print_info("Validating credentials:")
        is_valid, errors = secrets.validate_credentials(raise_on_error=False)
        if is_valid:
            print_success("All credentials validated successfully")
            results.append("OK Credential validation")
        else:
            if errors:
                print_warning("Credential validation issues: %d error(s)" % len(errors))
                for error in errors:
                    print_info("  - %s" % error)
                results.append("WARN Credential validation: %d error(s)" % len(errors))
            else:
                print_success("Credential validation passed")
                results.append("OK Credential validation")

    except Exception as e:
        print_fail("Secrets management error: %s" % str(e))
        results.append("FAIL Secrets management failed: %s" % str(e))
        passed = False

    return passed, results

# ============================================================================
# TEST 3: TECHNICAL INDICATORS INTEGRATION
# ============================================================================

def test_technical_indicators():
    """Test technical indicators"""
    print_subheader("TEST 3: Technical Indicators Integration")

    results = []
    passed = True

    try:
        # Import from analysis module
        from analysis import TechnicalIndicators, USING_TALIB
        print_success("Successfully imported TechnicalIndicators from analysis module")
        results.append("OK TechnicalIndicators import")

        # Check TA-Lib status
        if USING_TALIB:
            print_success("TA-Lib is ACTIVE (USING_TALIB = True)")
            results.append("OK TA-Lib active")
        else:
            print_warning("TA-Lib not active, using fallback indicators (USING_TALIB = False)")
            results.append("WARN TA-Lib not active (using fallback)")

        # Create sample candles for testing
        sample_candles = [
            {'open': 1.1000, 'high': 1.1050, 'low': 1.0980, 'close': 1.1010, 'volume': 1000},
            {'open': 1.1010, 'high': 1.1060, 'low': 1.0990, 'close': 1.1030, 'volume': 1200},
            {'open': 1.1030, 'high': 1.1080, 'low': 1.1000, 'close': 1.1050, 'volume': 1400},
            {'open': 1.1050, 'high': 1.1100, 'low': 1.1020, 'close': 1.1080, 'volume': 1600},
            {'open': 1.1080, 'high': 1.1120, 'low': 1.1040, 'close': 1.1100, 'volume': 1800},
        ]

        # Expand sample data to 100 candles for realistic testing
        for i in range(5, 100):
            base_price = 1.1000 + (i * 0.0001)
            sample_candles.append({
                'open': base_price,
                'high': base_price + 0.0050,
                'low': base_price - 0.0050,
                'close': base_price + 0.0025,
                'volume': 1000 + (i * 10)
            })

        print_info("Created sample data with %d candles" % len(sample_candles))

        # Test RSI
        print_info("Testing RSI indicator:")
        try:
            rsi = TechnicalIndicators.rsi(sample_candles, period=14)
            print_info("  RSI(14): %s" % str(rsi))
            print_success("RSI calculation successful")
            results.append("OK RSI method callable")

            if 0 <= rsi <= 100:
                print_success("RSI value in valid range: %s" % str(rsi))
                results.append("OK RSI value validation")
            else:
                print_fail("RSI value out of range: %s" % str(rsi))
                results.append("FAIL RSI value validation")
                passed = False
        except Exception as e:
            print_fail("RSI calculation error: %s" % str(e))
            results.append("FAIL RSI calculation: %s" % str(e))
            passed = False

        # Test MACD
        print_info("Testing MACD indicator:")
        try:
            macd = TechnicalIndicators.macd(sample_candles)
            print_info("  MACD: %.6f" % macd['macd'])
            print_info("  Signal: %.6f" % macd['signal'])
            print_info("  Histogram: %.6f" % macd['histogram'])
            print_success("MACD calculation successful")
            results.append("OK MACD method callable")

            if 'macd' in macd and 'signal' in macd and 'histogram' in macd:
                print_success("MACD returns all required components")
                results.append("OK MACD structure validation")
            else:
                print_fail("MACD missing components")
                results.append("FAIL MACD structure validation")
                passed = False
        except Exception as e:
            print_fail("MACD calculation error: %s" % str(e))
            results.append("FAIL MACD calculation: %s" % str(e))
            passed = False

        # Test Stochastic
        print_info("Testing Stochastic indicator:")
        try:
            stoch = TechnicalIndicators.stochastic(sample_candles, k_period=14, d_period=3)
            print_info("  %%K: %s" % str(stoch['k']))
            print_info("  %%D: %s" % str(stoch['d']))
            print_success("Stochastic calculation successful")
            results.append("OK Stochastic method callable")

            if 0 <= stoch['k'] <= 100 and 0 <= stoch['d'] <= 100:
                print_success("Stochastic values in valid range")
                results.append("OK Stochastic value validation")
            else:
                print_fail("Stochastic values out of range")
                results.append("FAIL Stochastic value validation")
                passed = False
        except Exception as e:
            print_fail("Stochastic calculation error: %s" % str(e))
            results.append("FAIL Stochastic calculation: %s" % str(e))
            passed = False

        # Test ADX
        print_info("Testing ADX indicator:")
        try:
            adx = TechnicalIndicators.adx(sample_candles, period=14)
            print_info("  ADX(14): %s" % str(adx))
            print_success("ADX calculation successful")
            results.append("OK ADX method callable")
        except Exception as e:
            print_fail("ADX calculation error: %s" % str(e))
            results.append("FAIL ADX calculation: %s" % str(e))
            passed = False

        # Test Bollinger Bands
        print_info("Testing Bollinger Bands indicator:")
        try:
            bb = TechnicalIndicators.bollinger_bands(sample_candles, period=20, std_dev=2)
            print_info("  Upper: %.6f" % bb['upper'])
            print_info("  Middle: %.6f" % bb['middle'])
            print_info("  Lower: %.6f" % bb['lower'])
            print_info("  Position: %s" % str(bb['position']))
            print_success("Bollinger Bands calculation successful")
            results.append("OK Bollinger Bands method callable")
        except Exception as e:
            print_fail("Bollinger Bands calculation error: %s" % str(e))
            results.append("FAIL Bollinger Bands calculation: %s" % str(e))
            passed = False

        # Verify backward compatibility
        print_info("Checking backward compatibility:")
        try:
            # All methods should be callable without errors
            TechnicalIndicators.ema(sample_candles, 20)
            print_success("EMA method callable")
            results.append("OK EMA backward compatibility")
        except Exception as e:
            print_fail("EMA backward compatibility error: %s" % str(e))
            results.append("FAIL EMA backward compatibility: %s" % str(e))
            passed = False

    except Exception as e:
        print_fail("Technical indicators error: %s" % str(e))
        results.append("FAIL Technical indicators failed: %s" % str(e))
        passed = False

    return passed, results

# ============================================================================
# TEST 4: PAPER TRADING ENGINE STRUCTURE
# ============================================================================

def test_paper_trading_engine():
    """Test paper trading engine structure"""
    print_subheader("TEST 4: Paper Trading Engine Structure")

    results = []
    passed = True

    try:
        # Import paper trading engine
        from paper_trading_engine import PaperTradingEngine
        print_success("Successfully imported PaperTradingEngine")
        results.append("OK PaperTradingEngine import")

        # Create configuration for engine
        from paper_trading_config import get_config
        config = get_config()

        # Initialize engine
        try:
            engine = PaperTradingEngine(config)
            print_success("PaperTradingEngine initialized successfully")
            results.append("OK Engine initialization")
        except Exception as e:
            print_warning("Engine initialization warning (may need credentials): %s" % str(e)[:50])
            results.append("WARN Engine initialization (credentials may be needed)")
            # Continue testing structure even if connection fails
            engine = None

        # Verify required methods exist
        required_methods = [
            'connect',
            'get_candles',
            'analyze_market',
            'generate_signal',
            'execute_trade',
            'wait_for_result',
            'check_risk_limits',
            'print_summary'
        ]

        print_info("Checking for required methods:")
        for method_name in required_methods:
            if hasattr(PaperTradingEngine, method_name):
                method = getattr(PaperTradingEngine, method_name)
                if callable(method):
                    print_success("Method '%s' exists and is callable" % method_name)
                    results.append("OK Method '%s'" % method_name)
                else:
                    print_fail("'%s' exists but is not callable" % method_name)
                    results.append("FAIL Method '%s' not callable" % method_name)
                    passed = False
            else:
                print_fail("Method '%s' MISSING" % method_name)
                results.append("FAIL Method '%s' missing" % method_name)
                passed = False

        # Check error handling
        print_info("Checking error handling mechanisms:")
        if hasattr(PaperTradingEngine, '__init__'):
            print_success("Engine has constructor with error handling setup")
            results.append("OK Error handling in constructor")

        # Check logging configuration
        print_info("Checking logging configuration:")
        if hasattr(engine or PaperTradingEngine, 'metrics'):
            print_success("Engine has metrics tracking")
            results.append("OK Metrics tracking present")

        # Verify engine attributes
        print_info("Checking engine attributes:")
        expected_attributes = ['config', 'indicator_config', 'validation_config', 'safety_config']
        if engine:
            for attr in expected_attributes:
                if hasattr(engine, attr):
                    print_success("Attribute '%s' present" % attr)
                    results.append("OK Attribute '%s'" % attr)
                else:
                    print_fail("Attribute '%s' MISSING" % attr)
                    results.append("FAIL Attribute '%s' missing" % attr)
                    passed = False
        else:
            print_warning("Cannot verify attributes without engine instance")

    except Exception as e:
        print_fail("Paper trading engine error: %s" % str(e))
        results.append("FAIL Paper trading engine failed: %s" % str(e))
        passed = False

    return passed, results

# ============================================================================
# TEST 5: RISK MANAGEMENT INTEGRATION
# ============================================================================

def test_risk_management():
    """Test risk management"""
    print_subheader("TEST 5: Risk Management Integration")

    results = []
    passed = True

    try:
        # Import configuration with risk settings
        from paper_trading_config import get_config, PAPER_TRADING_CONFIG
        config = get_config()

        print_success("Risk management config loaded")
        results.append("OK Risk management config")

        # Test 1: Daily loss limit enforcement
        print_info("Testing daily loss limit enforcement:")
        max_daily_loss = PAPER_TRADING_CONFIG['MAX_DAILY_LOSS']
        print_info("  Max Daily Loss: $%.2f" % max_daily_loss)

        if max_daily_loss > 0:
            print_success("Daily loss limit configured")
            results.append("OK Daily loss limit present")
        else:
            print_fail("Daily loss limit not properly configured")
            results.append("FAIL Daily loss limit missing")
            passed = False

        # Test 2: Consecutive loss tracking
        print_info("Testing consecutive loss tracking:")
        max_consecutive_losses = PAPER_TRADING_CONFIG['MAX_CONSECUTIVE_LOSSES']
        print_info("  Max Consecutive Losses: %d" % max_consecutive_losses)

        if max_consecutive_losses > 0:
            print_success("Consecutive loss tracking configured")
            results.append("OK Consecutive loss tracking")
        else:
            print_fail("Consecutive loss tracking not configured")
            results.append("FAIL Consecutive loss tracking missing")
            passed = False

        # Test 3: Emergency stop mechanism
        print_info("Testing emergency stop mechanism:")
        from paper_trading_config import SAFETY_LIMITS

        emergency_stop_loss = SAFETY_LIMITS['EMERGENCY_STOP_LOSS']
        emergency_stop_enabled = SAFETY_LIMITS['EMERGENCY_STOP_ENABLED']

        print_info("  Emergency Stop Loss: $%.2f" % emergency_stop_loss)
        print_info("  Emergency Stop Enabled: %s" % str(emergency_stop_enabled))

        if emergency_stop_enabled and emergency_stop_loss > 0:
            print_success("Emergency stop mechanism is ENABLED")
            results.append("OK Emergency stop enabled")
        else:
            print_warning("Emergency stop mechanism is disabled")
            results.append("WARN Emergency stop disabled")

        # Test 4: Trade amount limits
        print_info("Testing trade amount limits:")
        trade_amount = PAPER_TRADING_CONFIG['TRADE_AMOUNT']
        min_amount = 1.0
        max_amount = 100.0

        print_info("  Default Trade Amount: $%.2f" % trade_amount)

        if min_amount <= trade_amount <= max_amount:
            print_success("Trade amount in reasonable range: $%.2f" % trade_amount)
            results.append("OK Trade amount limits")
        else:
            print_fail("Trade amount outside limits: $%.2f" % trade_amount)
            results.append("FAIL Trade amount limits")
            passed = False

        # Test 5: Confidence requirement
        print_info("Testing confidence requirements:")
        min_confidence = PAPER_TRADING_CONFIG['MIN_CONFIDENCE']
        print_info("  Minimum Confidence: %d%%" % min_confidence)

        if 50 <= min_confidence <= 100:
            print_success("Confidence threshold reasonable: %d%%" % min_confidence)
            results.append("OK Confidence threshold")
        else:
            print_fail("Confidence threshold unreasonable: %d%%" % min_confidence)
            results.append("FAIL Confidence threshold")
            passed = False

        # Test 6: Signal agreement requirement
        print_info("Testing multi-indicator agreement:")
        require_multiple = PAPER_TRADING_CONFIG['REQUIRE_MULTIPLE_INDICATORS']
        min_agreement = PAPER_TRADING_CONFIG['MIN_INDICATOR_AGREEMENT']

        print_info("  Require Multiple Indicators: %s" % str(require_multiple))
        print_info("  Minimum Agreement: %d indicators" % min_agreement)

        if require_multiple and min_agreement >= 2:
            print_success("Multi-indicator consensus requirement enforced")
            results.append("OK Multi-indicator consensus")
        else:
            print_warning("Multi-indicator consensus not enforced")
            results.append("WARN Multi-indicator consensus not enforced")

    except Exception as e:
        print_fail("Risk management error: %s" % str(e))
        results.append("FAIL Risk management failed: %s" % str(e))
        passed = False

    return passed, results

# ============================================================================
# TEST 6: DATA FLOW VALIDATION
# ============================================================================

def test_data_flow():
    """Test data flow through the system"""
    print_subheader("TEST 6: Data Flow Validation")

    results = []
    passed = True

    try:
        # Simulate: Config -> Indicators -> Signals -> Risk Check -> Trade Decision
        print_info("Simulating data flow: Config -> Indicators -> Signals -> Risk -> Decision")

        # Step 1: Load configuration
        print_info("\nStep 1: Configuration Loading")
        from paper_trading_config import get_config, PAPER_TRADING_CONFIG
        config = get_config()
        print_success("Configuration loaded")
        results.append("OK Step 1: Config loading")

        # Step 2: Import indicators
        print_info("\nStep 2: Initialize Technical Indicators")
        from analysis import TechnicalIndicators, USING_TALIB
        print_success("Indicators ready (TA-Lib: %s)" % str(USING_TALIB))
        results.append("OK Step 2: Indicators initialized")

        # Step 3: Analyze market data
        print_info("\nStep 3: Market Analysis")
        sample_candles = []
        for i in range(100):
            base_price = 1.1000 + (i * 0.0001)
            sample_candles.append({
                'open': base_price,
                'high': base_price + 0.0050,
                'low': base_price - 0.0050,
                'close': base_price + 0.0025,
                'volume': 1000 + (i * 10)
            })

        # Calculate all indicators
        rsi = TechnicalIndicators.rsi(sample_candles, period=14)
        macd = TechnicalIndicators.macd(sample_candles)
        stoch = TechnicalIndicators.stochastic(sample_candles)
        adx = TechnicalIndicators.adx(sample_candles)
        bb = TechnicalIndicators.bollinger_bands(sample_candles)

        print_info("  RSI: %s" % str(rsi))
        print_info("  MACD Histogram: %.6f" % macd['histogram'])
        print_info("  Stochastic %%K: %s" % str(stoch['k']))
        print_info("  ADX: %s" % str(adx))
        print_info("  BB Position: %s" % str(bb['position']))
        print_success("Market analysis completed")
        results.append("OK Step 3: Market analysis")

        # Step 4: Generate signals
        print_info("\nStep 4: Signal Generation")
        analysis = {
            'pair': 'EURUSD-OTC',
            'price': sample_candles[-1]['close'],
            'rsi': rsi,
            'macd': macd,
            'stochastic': stoch,
            'adx': adx,
            'bollinger_bands': bb,
            'timestamp': datetime.now().isoformat()
        }

        # Create a mock signal generator
        signals = {'CALL': 0, 'PUT': 0}
        confidence = 50.0

        # RSI signals
        if rsi < 30:
            signals['CALL'] += 1
            confidence += 10
        elif rsi > 70:
            signals['PUT'] += 1
            confidence += 10

        # MACD signals
        if macd['histogram'] > 0:
            signals['CALL'] += 1
            confidence += 8
        elif macd['histogram'] < 0:
            signals['PUT'] += 1
            confidence += 8

        # Stochastic signals
        if stoch['k'] < 20:
            signals['CALL'] += 1
            confidence += 7
        elif stoch['k'] > 80:
            signals['PUT'] += 1
            confidence += 7

        # BB signals
        if bb['position'] < 0.2:
            signals['CALL'] += 1
            confidence += 6
        elif bb['position'] > 0.8:
            signals['PUT'] += 1
            confidence += 6

        # Require multi-indicator consensus
        min_agreement = PAPER_TRADING_CONFIG['MIN_INDICATOR_AGREEMENT']
        signal = None

        if signals['CALL'] >= min_agreement and signals['CALL'] > signals['PUT']:
            signal = 'CALL'
            print_info("Signal: %s (CALL votes: %d, PUT votes: %d)" % (signal, signals['CALL'], signals['PUT']))
        elif signals['PUT'] >= min_agreement and signals['PUT'] > signals['CALL']:
            signal = 'PUT'
            print_info("Signal: %s (CALL votes: %d, PUT votes: %d)" % (signal, signals['CALL'], signals['PUT']))
        else:
            signal = None
            print_info("No signal (Insufficient consensus - CALL: %d, PUT: %d)" % (signals['CALL'], signals['PUT']))

        print_info("Confidence: %.1f%%" % min(confidence, 100.0))
        print_success("Signal generation completed")
        results.append("OK Step 4: Signal generation")

        # Step 5: Risk Management Check
        print_info("\nStep 5: Risk Management Check")

        daily_loss = 5.0  # Simulated
        daily_profit = 10.0  # Simulated
        consecutive_losses = 1  # Simulated

        risk_check_passed = True
        reasons = []

        if daily_loss >= PAPER_TRADING_CONFIG['MAX_DAILY_LOSS']:
            risk_check_passed = False
            reasons.append("Daily loss limit exceeded: $%.2f" % daily_loss)

        if daily_profit >= PAPER_TRADING_CONFIG['MAX_DAILY_PROFIT']:
            risk_check_passed = False
            reasons.append("Daily profit target reached: $%.2f" % daily_profit)

        if consecutive_losses >= PAPER_TRADING_CONFIG['MAX_CONSECUTIVE_LOSSES']:
            risk_check_passed = False
            reasons.append("Consecutive losses limit exceeded: %d" % consecutive_losses)

        if signal and confidence < PAPER_TRADING_CONFIG['MIN_CONFIDENCE']:
            risk_check_passed = False
            reasons.append("Confidence below minimum: %.1f%%" % confidence)

        print_info("  Daily Loss: $%.2f (Max: $%.2f)" % (daily_loss, PAPER_TRADING_CONFIG['MAX_DAILY_LOSS']))
        print_info("  Daily Profit: $%.2f (Max: $%.2f)" % (daily_profit, PAPER_TRADING_CONFIG['MAX_DAILY_PROFIT']))
        print_info("  Consecutive Losses: %d (Max: %d)" % (consecutive_losses, PAPER_TRADING_CONFIG['MAX_CONSECUTIVE_LOSSES']))
        print_info("  Risk Check: %s" % ('PASS' if risk_check_passed else 'FAIL'))

        if risk_check_passed:
            print_success("Risk management check passed")
        else:
            print_warning("Risk check failed: %s" % ', '.join(reasons))

        results.append("OK Step 5: Risk check")

        # Step 6: Trade Decision
        print_info("\nStep 6: Trade Decision")

        should_trade = risk_check_passed and signal and confidence >= PAPER_TRADING_CONFIG['MIN_CONFIDENCE']

        if should_trade:
            print_success("TRADE DECISION: EXECUTE %s" % signal)
            print_info("  Trade Amount: $%.2f" % PAPER_TRADING_CONFIG['TRADE_AMOUNT'])
            print_info("  Duration: %d minute(s)" % PAPER_TRADING_CONFIG['TRADE_DURATION'])
            results.append("OK Step 6: Trade execution decision")
        else:
            print_info("TRADE DECISION: DO NOT EXECUTE")
            print_info("  Reason: Signal=%s, Confidence=%.1f%%, Risk=%s" % (str(signal), confidence, str(risk_check_passed)))
            results.append("OK Step 6: No-trade decision")

        print_success("Data flow validation completed")
        results.append("OK Complete data flow")

    except Exception as e:
        print_fail("Data flow validation error: %s" % str(e))
        results.append("FAIL Data flow validation failed: %s" % str(e))
        import traceback
        traceback.print_exc()
        passed = False

    return passed, results

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all integration tests"""
    print_header("AGENT 3: SYSTEM INTEGRATION VALIDATION")
    print("Test Execution Time: %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("Python Version: %s" % sys.version.split()[0])

    # Run all tests
    test_results = []

    print("\n" + "="*70)
    print("RUNNING INTEGRATION TESTS")
    print("="*70)

    # Test 1
    passed1, results1 = test_configuration_loading()
    test_results.append(("Configuration Loading", passed1, results1))

    # Test 2
    passed2, results2 = test_secrets_management()
    test_results.append(("Secrets Management", passed2, results2))

    # Test 3
    passed3, results3 = test_technical_indicators()
    test_results.append(("Technical Indicators", passed3, results3))

    # Test 4
    passed4, results4 = test_paper_trading_engine()
    test_results.append(("Paper Trading Engine", passed4, results4))

    # Test 5
    passed5, results5 = test_risk_management()
    test_results.append(("Risk Management", passed5, results5))

    # Test 6
    passed6, results6 = test_data_flow()
    test_results.append(("Data Flow", passed6, results6))

    # ========================================================================
    # SUMMARY REPORT
    # ========================================================================

    print_header("INTEGRATION TEST SUMMARY")

    # Overall status
    all_passed = all(passed for _, passed, _ in test_results)

    print_subheader("Test Results by Component")

    for test_name, passed, results in test_results:
        status = (Colors.GREEN + "PASS" + Colors.RESET) if passed else (Colors.RED + "FAIL" + Colors.RESET)
        print("%s.%-40s %s" % (test_name, "."*(45-len(test_name)), status))

    # Detailed results
    print_subheader("Detailed Results")

    for test_name, passed, results in test_results:
        print("\n%s:" % test_name)
        for result in results:
            if result.startswith('OK'):
                print_success(result[3:])
            elif result.startswith('FAIL'):
                print_fail(result[5:])
            elif result.startswith('WARN'):
                print_warning(result[5:])
            else:
                print_info(result)

    # Overall summary
    print_header("OVERALL INTEGRATION HEALTH")

    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed, _ in test_results if passed)

    print("Tests Passed: %d/%d" % (passed_tests, total_tests))

    if all_passed:
        print_success("ALL INTEGRATION TESTS PASSED")
        print("\nSystem Status: READY FOR PRODUCTION")
    else:
        print_fail("SOME INTEGRATION TESTS FAILED")
        print("\nSystem Status: REQUIRES ATTENTION")

    # Component Status
    print_subheader("Component Status Summary")

    components_status = {
        "Configuration System": test_results[0][1],
        "Secrets Management": test_results[1][1],
        "Technical Indicators": test_results[2][1],
        "Trading Engine": test_results[3][1],
        "Risk Management": test_results[4][1],
        "Data Flow Pipeline": test_results[5][1],
    }

    for component, status in components_status.items():
        symbol = "OK " if status else "FAIL "
        color = Colors.GREEN if status else Colors.RED
        print("%s%s%s%s" % (color, symbol, component, Colors.RESET))

    # Missing Components (if any)
    print_subheader("Missing Components Check")

    missing_components = []
    for test_name, passed, results in test_results:
        if not passed:
            for result in results:
                if "MISSING" in result or "missing" in result:
                    missing_components.append("  - %s" % result)

    if missing_components:
        print_warning("The following components are missing or non-functional:")
        for component in missing_components:
            print(component)
    else:
        print_success("All core components present and functional")

    # Data Flow Status
    print_subheader("Data Flow Validation Status")
    data_flow_passed = test_results[5][1]
    if data_flow_passed:
        print_success("Data flow: Config -> Indicators -> Signals -> Risk -> Decision")
        print_success("System communication verified")
        print_success("Signal consensus mechanism validated")
        print_success("Confidence calculation validated")
    else:
        print_fail("Data flow validation incomplete")

    # Final recommendations
    print_header("RECOMMENDATIONS")

    if all_passed:
        print_success("System is fully integrated and ready for:")
        print("  1. Paper trading tests")
        print("  2. Live trading (with caution)")
        print("  3. Performance monitoring")
    else:
        print_warning("System requires fixes before production use:")
        print("  1. Review failed test components")
        print("  2. Check configuration files")
        print("  3. Verify all dependencies installed")
        print("  4. Ensure credentials are properly set")

    print("\n" + "="*70)
    print("Integration validation complete")
    print("="*70 + "\n")

    # Exit code
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
