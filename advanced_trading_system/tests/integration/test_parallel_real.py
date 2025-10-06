#!/usr/bin/env python3
"""
Test Parallel Trading Engine with Real Credentials
"""

from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

EMAIL = "tombokael4@gmail.com"
PASSWORD = "tombokael04"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def analyze_asset(api, asset):
    """Analyze a single asset"""
    try:
        # Get candles
        api.start_candles_stream(asset, 60, 50)
        time.sleep(1)
        candles = api.get_realtime_candles(asset, 60)
        api.stop_candles_stream(asset, 60)

        if candles and len(candles) > 0:
            candle_list = list(candles.values())
            latest = candle_list[-1] if candle_list else None

            if latest:
                return {
                    'asset': asset,
                    'status': 'success',
                    'close': latest.get('close'),
                    'open': latest.get('open'),
                    'candles_count': len(candles)
                }

        return {'asset': asset, 'status': 'no_data'}
    except Exception as e:
        return {'asset': asset, 'status': 'error', 'error': str(e)}

def test_parallel_analysis():
    """Test parallel analysis of multiple assets"""
    print_section("PARALLEL TRADING ENGINE TEST")

    try:
        # Connect
        print("🔌 Connecting to IQ Option...")
        api = IQ_Option(EMAIL, PASSWORD)
        check, reason = api.connect()

        if not check:
            print(f"❌ Connection failed: {reason}")
            return

        print(f"✅ Connected successfully")

        # Change to practice
        api.change_balance("PRACTICE")
        time.sleep(1)

        balance = api.get_balance()
        print(f"💰 Balance: ${balance}")

        # Test assets
        test_assets = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
        print(f"\n📊 Analyzing {len(test_assets)} assets in parallel...")

        # Sequential analysis (baseline)
        print("\n1️⃣ Sequential Analysis:")
        start_seq = time.time()
        seq_results = []
        for asset in test_assets:
            result = analyze_asset(api, asset)
            seq_results.append(result)
            print(f"   {asset}: {result['status']}")
        seq_time = time.time() - start_seq
        print(f"   ⏱️  Sequential time: {seq_time:.2f}s")

        # Parallel analysis
        print("\n2️⃣ Parallel Analysis (3 workers):")
        start_par = time.time()
        par_results = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(analyze_asset, api, asset): asset
                      for asset in test_assets}

            for future in as_completed(futures):
                asset = futures[future]
                result = future.result()
                par_results.append(result)
                print(f"   {asset}: {result['status']}")

        par_time = time.time() - start_par
        print(f"   ⏱️  Parallel time: {par_time:.2f}s")

        # Speed improvement
        if seq_time > 0:
            improvement = ((seq_time - par_time) / seq_time) * 100
            print(f"\n🚀 Speed improvement: {improvement:.1f}% faster")

        # Results summary
        print(f"\n📈 Analysis Results:")
        successful = sum(1 for r in par_results if r['status'] == 'success')
        print(f"   ✅ Successful: {successful}/{len(test_assets)}")
        print(f"   ❌ Failed: {len(test_assets) - successful}/{len(test_assets)}")

        # Show asset data
        print(f"\n📊 Asset Data:")
        for result in par_results:
            if result['status'] == 'success':
                print(f"   {result['asset']}: Close={result.get('close', 'N/A')}, "
                      f"Open={result.get('open', 'N/A')}, "
                      f"Candles={result.get('candles_count', 0)}")

        api.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parallel_risk_management():
    """Test parallel risk management"""
    print_section("PARALLEL RISK MANAGEMENT")

    try:
        balance = 10000
        max_concurrent = 5
        risk_per_trade = 0.02
        total_risk_budget = 0.10

        print(f"💰 Balance: ${balance}")
        print(f"🎯 Max concurrent trades: {max_concurrent}")
        print(f"📊 Risk per trade: {risk_per_trade * 100}%")
        print(f"⚠️  Total risk budget: {total_risk_budget * 100}%")

        # Calculate position sizes
        position_size = balance * risk_per_trade
        max_total_risk = balance * total_risk_budget
        max_possible_trades = int(max_total_risk / position_size)

        print(f"\n📐 Calculations:")
        print(f"   Position size per trade: ${position_size:.2f}")
        print(f"   Max total risk: ${max_total_risk:.2f}")
        print(f"   Max possible trades: {min(max_possible_trades, max_concurrent)}")

        # Simulate parallel positions
        print(f"\n💼 Simulated Portfolio:")
        active_trades = min(3, max_concurrent)
        for i in range(active_trades):
            print(f"   Trade {i+1}: ${position_size:.2f} at risk")

        total_at_risk = active_trades * position_size
        risk_percentage = (total_at_risk / balance) * 100

        print(f"\n📊 Portfolio Risk:")
        print(f"   Total at risk: ${total_at_risk:.2f}")
        print(f"   Risk percentage: {risk_percentage:.1f}%")
        print(f"   Within budget: {'✅ YES' if risk_percentage <= total_risk_budget * 100 else '❌ NO'}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all parallel engine tests"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*15 + "PARALLEL TRADING ENGINE TESTING" + " "*22 + "║")
    print("╚" + "═"*68 + "╝")
    print(f"\n📧 Account: {EMAIL}")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {}

    # Test 1: Parallel Analysis
    results['Parallel Analysis'] = test_parallel_analysis()
    time.sleep(2)

    # Test 2: Risk Management
    results['Risk Management'] = test_parallel_risk_management()

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}\n")

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
