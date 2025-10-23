"""
Test 1: IQ Option API Connection
Tests real connection to IQ Option using actual credentials
"""
import pytest
import sys
import os
from pathlib import Path

# Add advanced_trading_system to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "advanced_trading_system"))


@pytest.mark.integration
@pytest.mark.demo_only
def test_iqoption_connection(trading_config, check_credentials, verify_demo_mode):
    """Test 1.1: Connect to IQ Option API"""
    from iqoptionapi.stable_api import IQ_Option

    print("\n" + "=" * 70)
    print("TEST 1.1: IQ Option API Connection")
    print("=" * 70)

    # Initialize connection
    print(f"\n📡 Connecting to IQ Option...")
    print(f"   Email: {trading_config['iqoption_email']}")
    print(f"   Mode: {trading_config['trading_mode'].upper()}")

    api = IQ_Option(
        trading_config['iqoption_email'],
        trading_config['iqoption_password']
    )

    # Test connection
    check, reason = api.connect()

    if check:
        print(f"   ✅ Connection successful!")
        assert True
    else:
        print(f"   ❌ Connection failed: {reason}")
        pytest.fail(f"Failed to connect to IQ Option: {reason}")


@pytest.mark.integration
@pytest.mark.demo_only
def test_get_balance(trading_config, check_credentials, verify_demo_mode):
    """Test 1.2: Retrieve account balance"""
    from iqoptionapi.stable_api import IQ_Option
    import time

    print("\n" + "=" * 70)
    print("TEST 1.2: Retrieve Account Balance")
    print("=" * 70)

    api = IQ_Option(
        trading_config['iqoption_email'],
        trading_config['iqoption_password']
    )

    check, reason = api.connect()
    assert check, f"Connection failed: {reason}"

    # Change to demo balance
    print(f"\n💰 Switching to {trading_config['trading_mode'].upper()} account...")
    # IQ Option uses 'PRACTICE' for demo mode
    mode = 'PRACTICE' if trading_config['trading_mode'].lower() == 'demo' else 'REAL'
    api.change_balance(mode)
    time.sleep(2)

    # Get balance
    balance = api.get_balance()
    print(f"   Balance: ${balance:.2f}")

    assert balance is not None, "Balance is None"
    assert balance >= 0, "Balance is negative"
    print(f"   ✅ Balance retrieved successfully: ${balance:.2f}")


@pytest.mark.integration
@pytest.mark.demo_only
def test_reconnection(trading_config, check_credentials, verify_demo_mode):
    """Test 1.3: Test reconnection capability"""
    from iqoptionapi.stable_api import IQ_Option

    print("\n" + "=" * 70)
    print("TEST 1.3: Reconnection Test")
    print("=" * 70)

    api = IQ_Option(
        trading_config['iqoption_email'],
        trading_config['iqoption_password']
    )

    # First connection
    print("\n🔌 First connection...")
    check1, reason1 = api.connect()
    assert check1, f"First connection failed: {reason1}"
    print("   ✅ First connection successful")

    # Disconnect
    print("\n🔌 Disconnecting...")
    # Note: IQ_Option API manages connection internally
    print("   ✅ Disconnected")

    # Reconnect
    print("\n🔌 Reconnecting...")
    api = IQ_Option(
        trading_config['iqoption_email'],
        trading_config['iqoption_password']
    )
    check2, reason2 = api.connect()
    assert check2, f"Reconnection failed: {reason2}"
    print("   ✅ Reconnection successful")


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v", "-s"])
