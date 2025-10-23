"""
Test 2: Data Ingestion Components
Tests real market data fetching and validation
"""
import pytest
import sys
import os
import time
from pathlib import Path

# Add advanced_trading_system to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "advanced_trading_system"))


@pytest.mark.integration
@pytest.mark.data
@pytest.mark.demo_only
def test_connection_manager(trading_config, check_credentials, verify_demo_mode):
    """Test 2.1: Connection Manager"""
    from data_ingestion.connection_manager import ConnectionManager

    print("\n" + "=" * 70)
    print("TEST 2.1: Connection Manager")
    print("=" * 70)

    print("\n🔌 Testing ConnectionManager...")
    conn_manager = ConnectionManager(
        email=trading_config['iqoption_email'],
        password=trading_config['iqoption_password'],
        account_type=trading_config['trading_mode']
    )

    # Test connection
    print("   Connecting...")
    result = conn_manager.connect()
    assert result, "ConnectionManager failed to connect"
    print("   ✅ Connection successful")

    # Test connection status
    assert conn_manager.is_connected(), "Connection status check failed"
    print("   ✅ Connection status verified")

    # Test balance retrieval
    balance = conn_manager.get_balance()
    print(f"   Balance: ${balance:.2f}")
    assert balance >= 0, "Invalid balance"
    print("   ✅ Balance retrieved")

    # Cleanup
    conn_manager.disconnect()
    print("   ✅ Disconnected successfully")


@pytest.mark.integration
@pytest.mark.data
@pytest.mark.demo_only
def test_market_data_provider(trading_config, check_credentials, verify_demo_mode):
    """Test 2.2: Market Data Provider"""
    from data_ingestion.connection_manager import ConnectionManager
    from data_ingestion.market_data_provider import MarketDataProvider

    print("\n" + "=" * 70)
    print("TEST 2.2: Market Data Provider")
    print("=" * 70)

    # Connect
    conn_manager = ConnectionManager(
        email=trading_config['iqoption_email'],
        password=trading_config['iqoption_password'],
        account_type=trading_config['trading_mode']
    )
    conn_manager.connect()
    time.sleep(2)

    # Initialize data provider
    print("\n📊 Testing MarketDataProvider...")
    data_provider = MarketDataProvider(conn_manager)

    # Test getting available assets
    print("\n   Getting available assets...")
    assets = data_provider.get_available_assets()

    assert assets is not None, "Failed to get assets"
    assert len(assets) > 0, "No assets available"
    print(f"   ✅ Found {len(assets)} available assets")
    print(f"   First 10: {assets[:10]}")

    # Test getting candles for first asset
    if assets:
        asset = assets[0]
        print(f"\n   Fetching candles for {asset}...")

        candles = data_provider.get_candles(asset, size=60, count=100)

        assert candles is not None, f"Failed to get candles for {asset}"
        assert len(candles) > 0, f"No candles returned for {asset}"
        print(f"   ✅ Retrieved {len(candles)} candles for {asset}")

        # Validate candle structure
        first_candle = candles[0]
        required_fields = ['open', 'close', 'high', 'low', 'volume']

        for field in required_fields:
            assert field in first_candle, f"Missing field: {field}"

        print(f"   ✅ Candle structure validated")
        print(f"   Sample candle: {first_candle}")

    # Cleanup
    conn_manager.disconnect()


@pytest.mark.integration
@pytest.mark.data
@pytest.mark.demo_only
def test_realtime_price_data(trading_config, check_credentials, verify_demo_mode):
    """Test 2.3: Real-time Price Data"""
    from data_ingestion.connection_manager import ConnectionManager
    from data_ingestion.market_data_provider import MarketDataProvider

    print("\n" + "=" * 70)
    print("TEST 2.3: Real-time Price Data")
    print("=" * 70)

    # Connect
    conn_manager = ConnectionManager(
        email=trading_config['iqoption_email'],
        password=trading_config['iqoption_password'],
        account_type=trading_config['trading_mode']
    )
    conn_manager.connect()
    time.sleep(2)

    data_provider = MarketDataProvider(conn_manager)

    # Test price fetching
    assets_to_test = ['EURUSD', 'GBPUSD', 'USDJPY']

    print(f"\n💹 Testing real-time prices for: {assets_to_test}")

    for asset in assets_to_test:
        try:
            price = data_provider.get_current_price(asset)

            if price:
                print(f"   {asset}: ${price:.5f} ✅")
                assert price > 0, f"Invalid price for {asset}"
            else:
                print(f"   {asset}: Not available ⚠️")

        except Exception as e:
            print(f"   {asset}: Error - {e} ❌")

    # Cleanup
    conn_manager.disconnect()


@pytest.mark.integration
@pytest.mark.data
@pytest.mark.demo_only
def test_data_validator(trading_config, check_credentials, verify_demo_mode):
    """Test 2.4: Data Validation"""
    from data_ingestion.connection_manager import ConnectionManager
    from data_ingestion.market_data_provider import MarketDataProvider
    from data_ingestion.data_validator import DataValidator

    print("\n" + "=" * 70)
    print("TEST 2.4: Data Validation")
    print("=" * 70)

    # Connect and get data
    conn_manager = ConnectionManager(
        email=trading_config['iqoption_email'],
        password=trading_config['iqoption_password'],
        mode=trading_config['trading_mode']
    )
    conn_manager.connect()
    time.sleep(2)

    data_provider = MarketDataProvider(conn_manager)
    assets = data_provider.get_available_assets()

    if assets:
        asset = assets[0]
        candles = data_provider.get_candles(asset, size=60, count=100)

        print(f"\n🔍 Validating data for {asset}...")

        # Initialize validator
        validator = DataValidator()

        # Test validation
        is_valid, errors = validator.validate_candles(candles)

        print(f"   Validation result: {'✅ VALID' if is_valid else '❌ INVALID'}")

        if not is_valid:
            print(f"   Errors found:")
            for error in errors:
                print(f"     - {error}")

        assert is_valid, f"Data validation failed: {errors}"

    # Cleanup
    conn_manager.disconnect()


@pytest.mark.integration
@pytest.mark.data
@pytest.mark.demo_only
def test_payout_rates(trading_config, check_credentials, verify_demo_mode):
    """Test 2.5: Payout Rates Fetching"""
    from data_ingestion.connection_manager import ConnectionManager
    from data_ingestion.market_data_provider import MarketDataProvider

    print("\n" + "=" * 70)
    print("TEST 2.5: Payout Rates")
    print("=" * 70)

    # Connect
    conn_manager = ConnectionManager(
        email=trading_config['iqoption_email'],
        password=trading_config['iqoption_password'],
        account_type=trading_config['trading_mode']
    )
    conn_manager.connect()
    time.sleep(2)

    data_provider = MarketDataProvider(conn_manager)
    assets = data_provider.get_available_assets()

    print(f"\n💰 Fetching payout rates for first 5 assets...")

    for asset in assets[:5]:
        try:
            payout = data_provider.get_payout_rate(asset)

            if payout:
                print(f"   {asset}: {payout*100:.1f}% ✅")
                assert 0.0 < payout <= 1.0, f"Invalid payout for {asset}: {payout}"
            else:
                print(f"   {asset}: Not available ⚠️")

        except Exception as e:
            print(f"   {asset}: Error - {e} ❌")

    # Cleanup
    conn_manager.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
