#!/usr/bin/env python3
"""
Comprehensive Data Ingestion Tests with Real Credentials
Tests all data ingestion components with live market data
"""
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from data_ingestion.connection_manager import ConnectionManager
from data_ingestion.data_validator import DataValidator
from data_ingestion.market_data_provider import MarketDataProvider

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_01_connection_manager():
    """Test 1: Connection Manager"""
    print_section("TEST 1: Connection Manager")

    email = os.getenv('IQOPTION_EMAIL')
    password = os.getenv('IQOPTION_PASSWORD')

    if not email or not password:
        print("❌ Credentials not set in environment")
        return False

    try:
        # Create connection manager
        conn_mgr = ConnectionManager(
            email=email,
            password=password,
            account_type='demo',
            max_retries=3,
            retry_delay=5
        )

        # Test connection
        success, message = conn_mgr.connect()

        if success:
            print(f"✅ Connection successful: {message}")

            # Get connection stats
            stats = conn_mgr.get_connection_stats()
            print(f"\n📊 Connection Statistics:")
            print(f"   Connected: {stats['connected']}")
            print(f"   Account Type: {stats['account_type']}")
            print(f"   Connection Attempts: {stats['connection_attempts']}")
            print(f"   Uptime: {stats['uptime_seconds']:.1f}s")

            # Test connection verification
            if conn_mgr._verify_connection():
                print(f"✅ Connection verification passed")
            else:
                print(f"⚠️  Connection verification failed")

            # Cleanup
            conn_mgr.disconnect()
            print(f"✅ Disconnected successfully")

            return True
        else:
            print(f"❌ Connection failed: {message}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_02_data_validator():
    """Test 2: Data Validator"""
    print_section("TEST 2: Data Validator")

    validator = DataValidator()

    # Test valid candles
    valid_candles = [
        {'open': 1.1000, 'high': 1.1010, 'low': 1.0990, 'close': 1.1005, 'volume': 100, 'time': 1000},
        {'open': 1.1005, 'high': 1.1015, 'low': 1.1000, 'close': 1.1012, 'volume': 150, 'time': 1060},
        {'open': 1.1012, 'high': 1.1020, 'low': 1.1008, 'close': 1.1018, 'volume': 120, 'time': 1120},
    ] * 10  # Repeat to get 30 candles

    print("\n📊 Testing valid candles...")
    if validator.validate_candles(valid_candles, min_count=20):
        print("✅ Valid candles passed validation")
    else:
        print("❌ Valid candles failed validation")
        return False

    # Test invalid candles (high < low)
    invalid_candles = [
        {'open': 1.1000, 'high': 1.0990, 'low': 1.1010, 'close': 1.1005, 'volume': 100, 'time': 1000}
    ]

    print("\n📊 Testing invalid candles...")
    if not validator.validate_candles(invalid_candles, min_count=1):
        print("✅ Invalid candles correctly rejected")
    else:
        print("❌ Invalid candles incorrectly accepted")
        return False

    # Test data quality check
    print("\n📊 Testing data quality assessment...")
    quality = validator.check_data_quality(valid_candles)
    print(f"   Quality Score: {quality['quality_score']}/100")
    print(f"   Valid: {quality['valid']}")
    print(f"   Issues: {quality['issues']}")

    if quality['valid']:
        print("✅ Data quality check passed")
    else:
        print("⚠️  Data quality issues detected")

    # Test sanitization
    print("\n📊 Testing data sanitization...")
    mixed_candles = valid_candles + invalid_candles
    sanitized = validator.sanitize_candles(mixed_candles)
    print(f"   Original: {len(mixed_candles)} candles")
    print(f"   Sanitized: {len(sanitized)} candles")
    print(f"✅ Sanitization completed")

    return True


def test_03_market_data_provider():
    """Test 3: Market Data Provider"""
    print_section("TEST 3: Market Data Provider")

    email = os.getenv('IQOPTION_EMAIL')
    password = os.getenv('IQOPTION_PASSWORD')

    if not email or not password:
        print("❌ Credentials not set in environment")
        return False

    try:
        # Create connection manager
        conn_mgr = ConnectionManager(email, password, 'demo')
        success, _ = conn_mgr.connect()

        if not success:
            print("❌ Connection failed")
            return False

        # Create market data provider
        provider = MarketDataProvider(
            connection_manager=conn_mgr,
            enable_caching=True,
            cache_ttl=300
        )

        # Test getting candles
        print("\n📊 Testing candle retrieval...")
        candles = provider.get_candles('EURUSD', timeframe='1m', count=50)

        if candles:
            print(f"✅ Retrieved {len(candles)} candles")
            print(f"   Latest close: {candles[-1]['close']:.6f}")
            print(f"   Latest high: {candles[-1]['high']:.6f}")
            print(f"   Latest low: {candles[-1]['low']:.6f}")
        else:
            print("❌ Failed to retrieve candles")
            conn_mgr.disconnect()
            return False

        # Test caching
        print("\n📊 Testing caching...")
        start_time = time.time()
        cached_candles = provider.get_candles('EURUSD', timeframe='1m', count=50)
        cache_time = time.time() - start_time

        if cached_candles:
            print(f"✅ Cache hit (retrieved in {cache_time:.3f}s)")
        else:
            print("⚠️  Cache miss")

        # Test current price
        print("\n📊 Testing current price...")
        price = provider.get_current_price('EURUSD')
        if price:
            print(f"✅ Current price: ${price:.6f}")
        else:
            print("❌ Failed to get current price")

        # Test market status
        print("\n📊 Testing market status...")
        status = provider.get_market_status('EURUSD')
        print(f"   Binary: {'OPEN' if status['binary'] else 'CLOSED'}")
        print(f"   Digital: {'OPEN' if status['digital'] else 'CLOSED'}")
        print(f"✅ Market status retrieved")

        # Test available assets
        print("\n📊 Testing available assets...")
        assets = provider.get_available_assets()
        print(f"   Binary assets: {len(assets['binary'])}")
        print(f"   Digital assets: {len(assets['digital'])}")
        if assets['binary']:
            print(f"   Examples: {', '.join(assets['binary'][:5])}")
        print(f"✅ Available assets retrieved")

        # Get statistics
        print("\n📊 Provider Statistics:")
        stats = provider.get_statistics()
        print(f"   Total Requests: {stats['total_requests']}")
        print(f"   Cache Hits: {stats['cache_hits']}")
        print(f"   Cache Misses: {stats['cache_misses']}")
        print(f"   Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        print(f"   Failed Requests: {stats['failed_requests']}")
        print(f"   Data Quality Issues: {stats['data_quality_issues']}")

        # Cleanup
        conn_mgr.disconnect()
        print(f"\n✅ All market data provider tests passed")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_04_connection_resilience():
    """Test 4: Connection Resilience"""
    print_section("TEST 4: Connection Resilience")

    email = os.getenv('IQOPTION_EMAIL')
    password = os.getenv('IQOPTION_PASSWORD')

    if not email or not password:
        print("❌ Credentials not set in environment")
        return False

    try:
        conn_mgr = ConnectionManager(email, password, 'demo', max_retries=3)

        # Test initial connection
        print("\n📊 Testing initial connection...")
        success, _ = conn_mgr.connect()
        if not success:
            print("❌ Initial connection failed")
            return False
        print("✅ Initial connection successful")

        # Test ensure_connected
        print("\n📊 Testing ensure_connected...")
        if conn_mgr.ensure_connected():
            print("✅ Connection ensured")
        else:
            print("❌ Failed to ensure connection")
            return False

        # Test reconnection
        print("\n📊 Testing reconnection...")
        conn_mgr.disconnect()
        time.sleep(1)

        success, _ = conn_mgr.connect(force_reconnect=True)
        if success:
            print("✅ Reconnection successful")
            stats = conn_mgr.get_connection_stats()
            print(f"   Total Reconnections: {stats['total_reconnections']}")
        else:
            print("❌ Reconnection failed")
            return False

        # Cleanup
        conn_mgr.disconnect()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_05_data_quality_monitoring():
    """Test 5: Data Quality Monitoring"""
    print_section("TEST 5: Data Quality Monitoring")

    email = os.getenv('IQOPTION_EMAIL')
    password = os.getenv('IQOPTION_PASSWORD')

    if not email or not password:
        print("❌ Credentials not set in environment")
        return False

    try:
        conn_mgr = ConnectionManager(email, password, 'demo')
        conn_mgr.connect()

        provider = MarketDataProvider(conn_mgr, enable_caching=False)
        validator = DataValidator()

        # Test multiple pairs
        test_pairs = ['EURUSD', 'GBPUSD', 'USDJPY']

        print("\n📊 Testing data quality across multiple pairs...")

        for pair in test_pairs:
            print(f"\n   Testing {pair}...")

            candles = provider.get_candles(pair, timeframe='1m', count=100)

            if candles:
                quality = validator.check_data_quality(candles)
                print(f"   ✅ {pair}: Quality Score {quality['quality_score']}/100")
                if quality['issues']:
                    print(f"      Issues: {', '.join(quality['issues'])}")
            else:
                print(f"   ❌ {pair}: Failed to retrieve data")

        # Get final statistics
        print("\n📊 Final Statistics:")
        stats = provider.get_statistics()
        print(f"   Total Requests: {stats['total_requests']}")
        print(f"   Failed Requests: {stats['failed_requests']}")
        print(f"   Data Quality Issues: {stats['data_quality_issues']}")

        success_rate = (
            (stats['total_requests'] - stats['failed_requests']) /
            stats['total_requests'] * 100
        ) if stats['total_requests'] > 0 else 0

        print(f"   Success Rate: {success_rate:.1f}%")

        conn_mgr.disconnect()

        if success_rate >= 80:
            print(f"\n✅ Data quality monitoring passed")
            return True
        else:
            print(f"\n⚠️  Success rate below 80%")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all data ingestion tests"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "DATA INGESTION TEST SUITE" + " " * 28 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"\n🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {}

    # Run tests
    results['Connection Manager'] = test_01_connection_manager()
    time.sleep(2)

    results['Data Validator'] = test_02_data_validator()
    time.sleep(2)

    results['Market Data Provider'] = test_03_market_data_provider()
    time.sleep(2)

    results['Connection Resilience'] = test_04_connection_resilience()
    time.sleep(2)

    results['Data Quality Monitoring'] = test_05_data_quality_monitoring()

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\n✅ Passed: {passed}/{total} ({percentage:.1f}%)")
    print(f"❌ Failed: {total - passed}/{total}\n")

    print("Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
