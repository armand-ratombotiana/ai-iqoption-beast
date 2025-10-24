#!/usr/bin/env python3
"""
Direct Real Credentials Testing
Tests each component with tombokael4@gmail.com / tombokael04
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
import time

# Credentials
EMAIL = "tombokael4@gmail.com"
PASSWORD = "tombokael04"

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_1_connection():
    """Test 1: IQOption Connection"""
    print_header("TEST 1: IQOption Connection & Authentication")
    try:
        from core.iqoption_client import IQOptionClient

        client = IQOptionClient(EMAIL, PASSWORD)
        connected = client.connect()

        if connected:
            print(f"✓ Connected successfully as {EMAIL}")
            print(f"✓ Connection status: {client.is_connected()}")

            # Get balance
            balance = client.get_balance()
            print(f"✓ Account balance: ${balance}")

            client.disconnect()
            return True
        else:
            print("✗ Connection failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_2_market_data():
    """Test 2: Market Data Retrieval"""
    print_header("TEST 2: Market Data Retrieval")
    try:
        from core.iqoption_client import IQOptionClient

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        # Get candles
        print("Fetching EURUSD candles...")
        candles = client.get_candles("EURUSD", 60, 100)
        print(f"✓ Retrieved {len(candles)} candles")
        print(f"  Columns: {list(candles.columns)}")
        print(f"  Latest close: {candles['close'].iloc[-1]}")

        # Check market status
        is_open = client.check_asset_open("EURUSD")
        print(f"✓ EURUSD market status: {'OPEN' if is_open else 'CLOSED'}")

        # Get all open times
        open_times = client.get_all_open_time()
        print(f"✓ Retrieved market times for {len(open_times)} assets")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_signal_generation():
    """Test 3: Signal Generation"""
    print_header("TEST 3: Signal Generation")
    try:
        from core.iqoption_client import IQOptionClient
        from core.signal_generator import SignalGenerator

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        generator = SignalGenerator(client)
        signal = generator.generate_signal("EURUSD", timeframe=60)

        print(f"✓ Generated signal:")
        print(f"  Action: {signal.get('action', 'N/A')}")
        print(f"  Confidence: {signal.get('confidence', 0)}%")
        print(f"  Asset: {signal.get('asset', 'N/A')}")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_signal_validation():
    """Test 4: Signal Validation"""
    print_header("TEST 4: Signal Validation")
    try:
        from core.signal_validator import SignalValidator

        validator = SignalValidator()

        test_signal = {
            'action': 'call',
            'confidence': 75,
            'asset': 'EURUSD',
            'timeframe': 60
        }

        is_valid = validator.validate(test_signal)
        print(f"✓ Signal validation result: {'VALID' if is_valid else 'INVALID'}")
        print(f"  Test signal: {test_signal}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_risk_management():
    """Test 5: Risk Management"""
    print_header("TEST 5: Risk Management")
    try:
        from core.iqoption_client import IQOptionClient
        from core.risk_manager import RiskManager

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        risk_manager = RiskManager(
            max_risk_per_trade=0.02,
            max_daily_loss=0.1,
            max_concurrent_trades=3
        )

        balance = client.get_balance()
        can_trade = risk_manager.can_open_trade(balance, current_trades=0)

        print(f"✓ Balance: ${balance}")
        print(f"✓ Can open trade: {can_trade}")
        print(f"  Max risk per trade: 2%")
        print(f"  Max daily loss: 10%")
        print(f"  Max concurrent: 3")

        # Test with max trades
        can_trade_max = risk_manager.can_open_trade(balance, current_trades=3)
        print(f"✓ Can trade with 3 open: {can_trade_max}")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_position_sizing():
    """Test 6: Position Sizing"""
    print_header("TEST 6: Position Sizing")
    try:
        from core.iqoption_client import IQOptionClient
        from core.position_sizer import PositionSizer

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        sizer = PositionSizer(
            risk_per_trade=0.02,
            max_position_size=100
        )

        balance = client.get_balance()
        position_size = sizer.calculate_size(balance, risk_percent=2)

        print(f"✓ Balance: ${balance}")
        print(f"✓ Position size (2% risk): ${position_size}")
        print(f"✓ Max position size: $100")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_7_trade_executor():
    """Test 7: Trade Executor (dry run)"""
    print_header("TEST 7: Trade Executor")
    try:
        from core.iqoption_client import IQOptionClient
        from core.trade_executor import TradeExecutor

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        executor = TradeExecutor(client)

        # Check if market is open
        is_open = client.check_asset_open("EURUSD")
        print(f"✓ Trade executor initialized")
        print(f"✓ EURUSD market: {'OPEN' if is_open else 'CLOSED'}")

        if is_open:
            print("  Note: Market is open - trade execution possible")
        else:
            print("  Note: Market closed - skipping actual trade")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_8_technical_analysis():
    """Test 8: Technical Analysis"""
    print_header("TEST 8: Technical Analysis")
    try:
        from core.iqoption_client import IQOptionClient
        from analysis.technical_analyzer import TechnicalAnalyzer

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        analyzer = TechnicalAnalyzer()
        candles = client.get_candles("EURUSD", 60, 100)

        indicators = analyzer.calculate_indicators(candles)

        print(f"✓ Technical indicators calculated:")
        for key, value in indicators.items():
            if isinstance(value, (int, float)):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_9_market_analysis():
    """Test 9: Market Analysis"""
    print_header("TEST 9: Market Analysis")
    try:
        from core.iqoption_client import IQOptionClient
        from analysis.market_analyzer import MarketAnalyzer

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        analyzer = MarketAnalyzer(client)
        analysis = analyzer.analyze("EURUSD", timeframe=60)

        print(f"✓ Market analysis completed:")
        print(f"  Trend: {analysis.get('trend', 'N/A')}")
        print(f"  Strength: {analysis.get('strength', 'N/A')}")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_10_pattern_detection():
    """Test 10: Pattern Detection"""
    print_header("TEST 10: Pattern Detection")
    try:
        from core.iqoption_client import IQOptionClient
        from analysis.pattern_detector import PatternDetector

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        detector = PatternDetector()
        candles = client.get_candles("EURUSD", 60, 100)

        patterns = detector.detect(candles)

        print(f"✓ Pattern detection completed:")
        if isinstance(patterns, list):
            print(f"  Patterns found: {len(patterns)}")
            for pattern in patterns[:3]:  # Show first 3
                print(f"  - {pattern}")
        else:
            print(f"  Result: {patterns}")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_11_ai_sentiment():
    """Test 11: AI Sentiment Analysis"""
    print_header("TEST 11: AI Sentiment Analysis")
    try:
        from ai_models.sentiment_analyzer import SentimentAnalyzer

        analyzer = SentimentAnalyzer()
        sentiment = analyzer.analyze("EURUSD")

        print(f"✓ Sentiment analysis:")
        print(f"  Result: {sentiment}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_12_ai_trend_prediction():
    """Test 12: AI Trend Prediction"""
    print_header("TEST 12: AI Trend Prediction")
    try:
        from core.iqoption_client import IQOptionClient
        from ai_models.trend_predictor import TrendPredictor

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        predictor = TrendPredictor()
        candles = client.get_candles("EURUSD", 60, 100)

        prediction = predictor.predict(candles)

        print(f"✓ Trend prediction:")
        print(f"  Result: {prediction}")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_13_database_operations():
    """Test 13: Database Operations"""
    print_header("TEST 13: Database Operations")
    try:
        from database.trade_storage import TradeDatabase

        db = TradeDatabase(":memory:")  # Use in-memory DB

        # Insert test trade
        trade_data = {
            'timestamp': datetime.now(),
            'asset': 'EURUSD',
            'action': 'call',
            'amount': 10,
            'duration': 60,
            'result': 'win',
            'profit': 8.5
        }

        db.insert_trade(trade_data)
        print(f"✓ Trade inserted successfully")

        # Retrieve trades
        trades = db.get_trades(limit=10)
        print(f"✓ Retrieved {len(trades)} trades")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_14_parallel_engine():
    """Test 14: Parallel Trading Engine"""
    print_header("TEST 14: Parallel Trading Engine")
    try:
        from core.iqoption_client import IQOptionClient
        from parallel_trading_engine import ParallelTradingEngine

        client = IQOptionClient(EMAIL, PASSWORD)
        client.connect()

        engine = ParallelTradingEngine(client, max_workers=3)

        assets = ["EURUSD", "GBPUSD", "USDJPY"]
        results = engine.analyze_assets(assets, timeframe=60)

        print(f"✓ Parallel analysis completed:")
        print(f"  Assets analyzed: {len(results)}")
        for asset, result in results.items():
            print(f"  {asset}: {result.get('status', 'N/A')}")

        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*15 + "COMPREHENSIVE REAL CREDENTIALS TESTING" + " "*15 + "║")
    print("╚" + "═"*68 + "╝")
    print(f"\n📧 Account: {EMAIL}")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    tests = [
        test_1_connection,
        test_2_market_data,
        test_3_signal_generation,
        test_4_signal_validation,
        test_5_risk_management,
        test_6_position_sizing,
        test_7_trade_executor,
        test_8_technical_analysis,
        test_9_market_analysis,
        test_10_pattern_detection,
        test_11_ai_sentiment,
        test_12_ai_trend_prediction,
        test_13_database_operations,
        test_14_parallel_engine,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
            results.append((test.__name__, False))

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed

    print(f"\n✅ Passed: {passed}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"\nDetailed Results:")

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")

    print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
