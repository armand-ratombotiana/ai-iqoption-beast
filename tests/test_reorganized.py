#!/usr/bin/env python3
"""
Comprehensive test suite for reorganized project
Tests all modules, API endpoints, and integration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)

    try:
        from src.models.signal import Signal
        from src.models.trade import Trade, TradeStatus
        from src.models.state import TradingState
        from src.core.signal_validator import SignalValidator
        from src.core.risk_manager import RiskManager
        from src.core.position_sizer import PositionSizer
        from src.core.state_manager import StateManager
        from src.utils.config import Config
        from src.utils.logger import setup_logger

        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_models():
    """Test data models"""
    print("\n" + "=" * 60)
    print("TEST 2: Data Models")
    print("=" * 60)

    from src.models.signal import Signal
    from src.models.trade import Trade
    from src.models.state import TradingState

    # Test Signal
    try:
        signal = Signal(action='call', pair='EURUSD', confidence=75)
        assert signal.action == 'call'
        assert signal.confidence == 75
        assert signal.is_valid(60) == True
        print("✓ Signal model working")
    except Exception as e:
        print(f"✗ Signal model failed: {e}")
        return False

    # Test Trade
    try:
        trade = Trade(
            pair='EURUSD',
            action='call',
            amount=1.5,
            duration=2,
            confidence=75
        )
        assert trade.amount == 1.5
        assert trade.is_complete == False
        print("✓ Trade model working")
    except Exception as e:
        print(f"✗ Trade model failed: {e}")
        return False

    # Test TradingState
    try:
        state = TradingState()
        state.record_win(1.5)
        assert state.consecutive_wins == 1
        assert state.daily_profit == 1.5
        state.record_loss(-1.0)
        assert state.consecutive_losses == 1
        assert state.martingale_level == 1
        print("✓ TradingState model working")
    except Exception as e:
        print(f"✗ TradingState model failed: {e}")
        return False

    return True


def test_core_logic():
    """Test core business logic"""
    print("\n" + "=" * 60)
    print("TEST 3: Core Business Logic")
    print("=" * 60)

    from src.models.signal import Signal
    from src.models.state import TradingState
    from src.core.signal_validator import SignalValidator
    from src.core.risk_manager import RiskManager
    from src.core.position_sizer import PositionSizer

    # Test SignalValidator
    try:
        validator = SignalValidator(min_confidence=60)
        signal1 = Signal(action='call', pair='EURUSD', confidence=75)
        signal2 = Signal(action='call', pair='EURUSD', confidence=50)

        valid1, _ = validator.validate(signal1)
        valid2, _ = validator.validate(signal2)

        assert valid1 == True
        assert valid2 == False
        print("✓ SignalValidator working")
    except Exception as e:
        print(f"✗ SignalValidator failed: {e}")
        return False

    # Test RiskManager
    try:
        config = {
            'MAX_DAILY_LOSS': 50,
            'MAX_DAILY_PROFIT': 100,
            'MAX_CONSECUTIVE_LOSSES': 3,
            'MIN_BALANCE': 50,
            'MAX_MARTINGALE_LEVEL': 4
        }

        risk_manager = RiskManager(config)
        state = TradingState()

        allowed1, _ = risk_manager.check_risk_guards(state, 100)
        assert allowed1 == True

        state.consecutive_losses = 3
        allowed2, _ = risk_manager.check_risk_guards(state, 100)
        assert allowed2 == False

        print("✓ RiskManager working")
    except Exception as e:
        print(f"✗ RiskManager failed: {e}")
        return False

    # Test PositionSizer
    try:
        config = {
            'BASE_TRADE_AMOUNT': 1.0,
            'MARTINGALE_MULTIPLIER': 1.5,
            'MAX_TRADE_MULTIPLIER': 5.0
        }

        position_sizer = PositionSizer(config)
        amount = position_sizer.calculate_trade_amount(75, 1000, 0)
        duration = position_sizer.calculate_expiration(90)

        assert amount == 0.75  # 1.0 * 1.5^0 * 0.75
        assert duration == 1  # 90% confidence = 1 minute

        print("✓ PositionSizer working")
    except Exception as e:
        print(f"✗ PositionSizer failed: {e}")
        return False

    return True


def test_config():
    """Test configuration management"""
    print("\n" + "=" * 60)
    print("TEST 4: Configuration")
    print("=" * 60)

    from src.utils.config import Config

    try:
        config = Config()

        # Check defaults loaded
        assert config['MAX_DAILY_LOSS'] == 50.0
        assert config['MIN_CONFIDENCE_THRESHOLD'] == 60

        # Test get/set
        config.set('TEST_VALUE', 123)
        assert config.get('TEST_VALUE') == 123

        # Test to_dict
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert 'MAX_DAILY_LOSS' in config_dict

        print("✓ Config management working")
        return True
    except Exception as e:
        print(f"✗ Config failed: {e}")
        return False


def test_flask_app():
    """Test Flask application creation"""
    print("\n" + "=" * 60)
    print("TEST 5: Flask Application")
    print("=" * 60)

    try:
        from src.api.app import create_app
        from src.utils.config import Config

        config = Config()
        app = create_app(config)

        # Check app created
        assert app is not None
        assert app.config['TRADING_CONFIG'] is not None

        # Check routes registered
        with app.app_context():
            routes = [str(rule) for rule in app.url_map.iter_rules()]

            assert any('/health' in r for r in routes)
            assert any('/status' in r for r in routes)
            assert any('/trade' in r for r in routes)
            assert any('/reset' in r for r in routes)

        print("✓ Flask app creation working")
        print(f"  Registered routes: {len(routes)}")
        return True
    except Exception as e:
        print(f"✗ Flask app failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print("\n" + "=" * 60)
    print("TEST 6: API Endpoints")
    print("=" * 60)

    try:
        from src.api.app import create_app
        from src.utils.config import Config

        config = Config()
        app = create_app(config)
        client = app.test_client()

        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        print("✓ GET /health working")

        # Test status endpoint
        response = client.get('/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'tradingState' in data
        assert 'config' in data
        print("✓ GET /status working")

        # Test reset endpoint
        response = client.post('/reset', json={'type': 'daily'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        print("✓ POST /reset working")

        # Test trade endpoint validation
        response = client.post('/trade', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        print("✓ POST /trade validation working")

        return True
    except Exception as e:
        print(f"✗ API endpoints failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("REORGANIZED PROJECT TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        ("Module Imports", test_imports),
        ("Data Models", test_models),
        ("Core Logic", test_core_logic),
        ("Configuration", test_config),
        ("Flask App", test_flask_app),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("STATUS: ✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("STATUS: ❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
