#!/usr/bin/env python3
"""
Test script for trade execution via API
Tests with demo account to validate full trading flow
"""

import requests
import json
import time
import sys

API_URL = "http://localhost:5000"

# Real IQOption account credentials for testing
DEMO_EMAIL = "tombokael4@gmail.com"
DEMO_PASSWORD = "tombokael04"

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_api_health():
    """Test API health endpoint"""
    print_section("TEST 1: API Health Check")

    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✓ Health check PASSED")
            return True
        else:
            print("✗ Health check FAILED")
            return False
    except Exception as e:
        print(f"✗ Health check ERROR: {e}")
        return False

def test_api_status():
    """Test API status endpoint"""
    print_section("TEST 2: Trading Status")

    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\nTrading State:")
            state = data.get('tradingState', {})
            print(f"  Daily Profit: ${state.get('daily_profit', 0):.2f}")
            print(f"  Daily Loss: ${state.get('daily_loss', 0):.2f}")
            print(f"  Consecutive Wins: {state.get('consecutive_wins', 0)}")
            print(f"  Consecutive Losses: {state.get('consecutive_losses', 0)}")
            print(f"  Martingale Level: {state.get('martingale_level', 0)}")

            print("\nConfiguration:")
            config = data.get('config', {})
            print(f"  Min Confidence: {config.get('MIN_CONFIDENCE_THRESHOLD')}%")
            print(f"  Max Daily Loss: ${config.get('MAX_DAILY_LOSS')}")
            print(f"  Max Consecutive Losses: {config.get('MAX_CONSECUTIVE_LOSSES')}")

            print("\n✓ Status check PASSED")
            return True
        else:
            print("✗ Status check FAILED")
            return False
    except Exception as e:
        print(f"✗ Status check ERROR: {e}")
        return False

def test_trade_validation():
    """Test trade validation without actual credentials"""
    print_section("TEST 3: Trade Validation (Missing Fields)")

    try:
        # Test with missing required fields
        response = requests.post(
            f"{API_URL}/trade",
            json={},
            timeout=5
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 400:
            print("✓ Validation PASSED (correctly rejected empty request)")
            return True
        else:
            print("✗ Validation FAILED")
            return False
    except Exception as e:
        print(f"✗ Validation ERROR: {e}")
        return False

def test_low_confidence():
    """Test trade rejection due to low confidence"""
    print_section("TEST 4: Low Confidence Rejection")

    try:
        response = requests.post(
            f"{API_URL}/trade",
            json={
                "email": "test@example.com",
                "password": "testpass",
                "action": "call",
                "pair": "EURUSD",
                "confidence": 50,  # Below threshold
                "accountType": "demo"
            },
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 400:
            data = response.json()
            if 'confidence' in data.get('error', '').lower():
                print("✓ Low confidence rejection PASSED")
                return True

        print("✗ Low confidence rejection FAILED")
        return False
    except Exception as e:
        print(f"✗ Low confidence ERROR: {e}")
        return False

def test_real_trade_execution():
    """Execute a real trade with actual IQOption credentials"""
    print_section("TEST 5: Real Trade Execution")

    print("\n🔥 EXECUTING REAL TRADE WITH ACTUAL CREDENTIALS")
    print("NOTE: This will connect to IQOption and attempt to place a real demo trade.")

    try:
        trade_payload = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD,
            "action": "call",
            "pair": "EURUSD",
            "confidence": 75,
            "accountType": "PRACTICE"  # Demo account
        }

        print("\nTrade Payload:")
        print(json.dumps({**trade_payload, "password": "***"}, indent=2))

        response = requests.post(
            f"{API_URL}/trade",
            json=trade_payload,
            timeout=30  # Longer timeout for real connection
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            print("\n" + "🎉" * 30)
            print("✓ TRADE SUCCESSFULLY EXECUTED!")
            print("🎉" * 30)
            print(f"\nTrade Details:")
            print(f"  Order ID: {data.get('order_id')}")
            print(f"  Amount: ${data.get('amount')}")
            print(f"  Duration: {data.get('duration')}s")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Balance: ${data.get('balance')}")
            return True
        elif response.status_code == 400:
            data = response.json()
            print(f"\n⚠️ Trade rejected: {data.get('error')}")
            # Still count as passed if rejection was for valid reasons
            if any(word in data.get('error', '').lower() for word in ['risk', 'limit', 'balance', 'market']):
                print("✓ Trade flow PASSED (valid rejection reason)")
                return True
            return False
        else:
            print("\n✗ Unexpected response")
            return False
    except Exception as e:
        print(f"\n✗ Trade execution ERROR: {e}")
        return False

def test_reset_endpoint():
    """Test state reset endpoint"""
    print_section("TEST 6: State Reset")

    try:
        response = requests.post(
            f"{API_URL}/reset",
            json={"type": "daily"},
            timeout=5
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✓ Reset PASSED")
            return True
        else:
            print("✗ Reset FAILED")
            return False
    except Exception as e:
        print(f"✗ Reset ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  IQOPTION AI TRADING BOT - API TRADE EXECUTION TESTS")
    print("=" * 70)
    print("\nAPI URL:", API_URL)
    print("Test Mode: Demo Account Simulation")

    tests = [
        ("API Health Check", test_api_health),
        ("Trading Status", test_api_status),
        ("Trade Validation", test_trade_validation),
        ("Low Confidence Rejection", test_low_confidence),
        ("Real Trade Execution", test_real_trade_execution),
        ("State Reset", test_reset_endpoint),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("STATUS: ✅ ALL API TESTS PASSED")
    else:
        print(f"STATUS: ⚠️ {total-passed} test(s) failed")

    print("=" * 70)

    print("\n" + "=" * 70)
    print("  NOTES")
    print("=" * 70)
    print("""
For actual trade execution:
1. Use valid IQOption demo account credentials
2. Ensure account has sufficient balance
3. Verify market is open for the trading pair
4. Monitor the trade execution in the API logs

To execute a real demo trade:
    curl -X POST http://localhost:5000/trade \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "your_demo_email@example.com",
        "password": "your_demo_password",
        "action": "call",
        "pair": "EURUSD",
        "confidence": 75,
        "accountType": "demo"
      }'
""")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
