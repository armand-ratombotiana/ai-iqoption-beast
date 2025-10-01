#!/usr/bin/env python3
"""
Final integration test suite for reorganized project
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

print("=" * 70)
print("FINAL INTEGRATION TEST - Reorganized IQOption AI Trading Bot")
print("=" * 70)
print()

# Test 1: Core Module Imports
print("[TEST 1] Core Module Imports")
print("-" * 70)
try:
    from models.signal import Signal
    from models.trade import Trade, TradeStatus
    from models.state import TradingState
    from core.signal_validator import SignalValidator
    from core.risk_manager import RiskManager
    from core.position_sizer import PositionSizer
    from core.state_manager import StateManager
    from utils.config import Config

    print("✓ All core modules imported successfully")
    test1_passed = True
except ImportError as e:
    print(f"✗ Import failed: {e}")
    test1_passed = False

print()

# Test 2: Data Model Functionality
print("[TEST 2] Data Model Functionality")
print("-" * 70)
try:
    from models.signal import Signal
    from models.trade import Trade
    from models.state import TradingState

    # Create and test signal
    signal = Signal(action='call', pair='EURUSD', confidence=75)
    assert signal.is_valid(60), "Signal validation failed"
    print(f"✓ Signal: {signal.action} {signal.pair} @ {signal.confidence}%")

    # Create and test trade
    trade = Trade(pair='EURUSD', action='call', amount=1.5, duration=2, confidence=75)
    assert trade.amount == 1.5, "Trade creation failed"
    print(f"✓ Trade: {trade.action} {trade.pair} ${trade.amount}")

    # Test trading state
    state = TradingState()
    state.record_win(1.5)
    assert state.consecutive_wins == 1, "State tracking failed"
    print(f"✓ State: Win recorded, streak={state.consecutive_wins}")

    test2_passed = True
except Exception as e:
    print(f"✗ Model test failed: {e}")
    test2_passed = False

print()

# Test 3: Business Logic
print("[TEST 3] Business Logic Components")
print("-" * 70)
try:
    from models.signal import Signal
    from models.state import TradingState
    from core.signal_validator import SignalValidator
    from core.risk_manager import RiskManager
    from core.position_sizer import PositionSizer

    # Test signal validation
    validator = SignalValidator(min_confidence=60)
    signal = Signal(action='call', pair='EURUSD', confidence=75)
    is_valid, msg = validator.validate(signal)
    assert is_valid, "Signal validation failed"
    print(f"✓ SignalValidator: {msg}")

    # Test risk management
    config = {
        'MAX_DAILY_LOSS': 50,
        'MAX_DAILY_PROFIT': 100,
        'MAX_CONSECUTIVE_LOSSES': 3,
        'MIN_BALANCE': 50,
        'MAX_MARTINGALE_LEVEL': 4
    }
    risk_manager = RiskManager(config)
    state = TradingState()
    allowed, reason = risk_manager.check_risk_guards(state, 100)
    assert allowed, "Risk check failed"
    print(f"✓ RiskManager: {reason}")

    # Test position sizing
    sizer_config = {
        'BASE_TRADE_AMOUNT': 1.0,
        'MARTINGALE_MULTIPLIER': 1.5,
        'MAX_TRADE_MULTIPLIER': 5.0
    }
    position_sizer = PositionSizer(sizer_config)
    amount = position_sizer.calculate_trade_amount(75, 1000, 0)
    duration = position_sizer.calculate_expiration(90)
    print(f"✓ PositionSizer: ${amount} @ {duration}min")

    test3_passed = True
except Exception as e:
    print(f"✗ Business logic test failed: {e}")
    test3_passed = False

print()

# Test 4: Configuration Management
print("[TEST 4] Configuration Management")
print("-" * 70)
try:
    from utils.config import Config

    config = Config()
    assert config['MAX_DAILY_LOSS'] == 50.0, "Config default failed"
    print(f"✓ Config loaded with {len(config.to_dict())} parameters")
    print(f"  MAX_DAILY_LOSS: ${config['MAX_DAILY_LOSS']}")
    print(f"  MIN_CONFIDENCE: {config['MIN_CONFIDENCE_THRESHOLD']}%")

    test4_passed = True
except Exception as e:
    print(f"✗ Config test failed: {e}")
    test4_passed = False

print()

# Test 5: Flask Application (without IQOption dependency)
print("[TEST 5] Flask Application Structure")
print("-" * 70)
try:
    from api.app import create_app
    from utils.config import Config

    config = Config()
    app = create_app(config)

    # Test app created
    assert app is not None, "App creation failed"
    print(f"✓ Flask app created: {app.name}")

    # Test routes
    with app.app_context():
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        endpoint_count = len([r for r in routes if not r.startswith('/static')])
        print(f"✓ Routes registered: {endpoint_count} endpoints")

        # Test specific endpoints
        client = app.test_client()

        # Health check
        response = client.get('/health')
        assert response.status_code == 200, "Health endpoint failed"
        print(f"✓ GET /health: {response.status_code}")

        # Status
        response = client.get('/status')
        assert response.status_code == 200, "Status endpoint failed"
        data = response.get_json()
        assert 'tradingState' in data, "Status response invalid"
        print(f"✓ GET /status: {response.status_code}")

        # Reset
        response = client.post('/reset', json={'type': 'daily'})
        assert response.status_code == 200, "Reset endpoint failed"
        print(f"✓ POST /reset: {response.status_code}")

    test5_passed = True
except Exception as e:
    print(f"✗ Flask app test failed: {e}")
    import traceback
    traceback.print_exc()
    test5_passed = False

print()

# Test 6: n8n Node Structure
print("[TEST 6] n8n Node Validation")
print("-" * 70)
try:
    import subprocess
    result = subprocess.run(
        ['node', '-e', '''
        const { Trading } = require('./n8n/nodes/iqoption-trading/nodes/Trading/Trading.node.js');
        const trading = new Trading();
        console.log(trading.description ? 'valid' : 'invalid');
        '''],
        capture_output=True,
        text=True,
        cwd=project_root
    )

    if result.returncode == 0 and 'valid' in result.stdout:
        print("✓ n8n node structure valid")
        print("  Node: IQOption AI Trading Bot v2")
        test6_passed = True
    else:
        print(f"✗ n8n node validation failed: {result.stderr}")
        test6_passed = False
except Exception as e:
    print(f"✗ n8n test failed: {e}")
    test6_passed = False

print()

# Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)

results = [
    ("Core Module Imports", test1_passed),
    ("Data Model Functionality", test2_passed),
    ("Business Logic Components", test3_passed),
    ("Configuration Management", test4_passed),
    ("Flask Application Structure", test5_passed),
    ("n8n Node Validation", test6_passed),
]

passed = sum(1 for _, result in results if result)
total = len(results)

for name, result in results:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"{status}: {name}")

print()
print("=" * 70)
print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

if passed == total:
    print("STATUS: ✅ ALL TESTS PASSED - REORGANIZATION SUCCESSFUL!")
else:
    print(f"STATUS: ⚠️  {total-passed} test(s) failed - Review above for details")

print("=" * 70)
print()

# Exit code
sys.exit(0 if passed == total else 1)
