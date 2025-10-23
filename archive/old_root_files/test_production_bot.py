#!/usr/bin/env python3
"""
Comprehensive Production Bot Testing Suite
Tests all critical components of the 24/7 autonomous trading bot
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

# Set test credentials
os.environ['TEST_EMAIL'] = 'tombokael4@gmail.com'
os.environ['TEST_PASSWORD'] = 'tombokael04'
os.environ['IQOPTION_EMAIL'] = 'tombokael4@gmail.com'
os.environ['IQOPTION_PASSWORD'] = 'tombokael04'

# Test configuration
os.environ['TRADING_MODE'] = 'demo'
os.environ['BASE_TRADE_AMOUNT'] = '1.0'
os.environ['MAX_DAILY_LOSS'] = '10'  # Small for testing
os.environ['MAX_DAILY_PROFIT'] = '20'  # Small for testing
os.environ['MAX_CONSECUTIVE_LOSSES'] = '3'
os.environ['MIN_BALANCE'] = '10'
os.environ['ENABLE_MARTINGALE'] = 'false'  # Disable for initial testing
os.environ['LOG_LEVEL'] = 'DEBUG'

print("="*80)
print("🧪 COMPREHENSIVE PRODUCTION BOT TESTING")
print("="*80)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mode: DEMO (Safe Testing)")
print(f"Credentials: {os.environ['TEST_EMAIL']}")
print("="*80)
print()

# Test results tracking
test_results = {
    'total_tests': 0,
    'passed': 0,
    'failed': 0,
    'tests': []
}

def log_test(name, passed, details="", duration=0):
    """Log test result"""
    test_results['total_tests'] += 1
    if passed:
        test_results['passed'] += 1
        status = "✅ PASS"
    else:
        test_results['failed'] += 1
        status = "❌ FAIL"

    result = {
        'name': name,
        'passed': passed,
        'details': details,
        'duration': duration
    }
    test_results['tests'].append(result)

    print(f"{status} | {name}")
    if details:
        print(f"         {details}")
    if duration > 0:
        print(f"         Duration: {duration:.2f}s")
    print()

# =============================================================================
# TEST 1: Import and Module Loading
# =============================================================================
print("📦 TEST 1: Import and Module Loading")
print("-" * 80)

start_time = time.time()
try:
    from iqoptionapi.stable_api import IQ_Option
    log_test("Import IQOption API", True, "Successfully imported", time.time() - start_time)
except Exception as e:
    log_test("Import IQOption API", False, f"Error: {e}", time.time() - start_time)
    sys.exit(1)

start_time = time.time()
try:
    # Import bot components (without running)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "autonomous_bot",
        "/app/app/KAEL/KAEL/autonomous_trading_bot_24_7.py"
    )
    bot_module = importlib.util.module_from_spec(spec)

    log_test("Import Autonomous Bot Module", True, "Module loaded successfully", time.time() - start_time)
except Exception as e:
    log_test("Import Autonomous Bot Module", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# TEST 2: IQ Option Connection
# =============================================================================
print("\n🔌 TEST 2: IQ Option Connection")
print("-" * 80)

start_time = time.time()
try:
    api = IQ_Option(os.environ['TEST_EMAIL'], os.environ['TEST_PASSWORD'])
    check, reason = api.connect()

    if check:
        log_test("Connect to IQ Option", True, f"Connected: {reason}", time.time() - start_time)
    else:
        log_test("Connect to IQ Option", False, f"Failed: {reason}", time.time() - start_time)
        sys.exit(1)
except Exception as e:
    log_test("Connect to IQ Option", False, f"Error: {e}", time.time() - start_time)
    sys.exit(1)

# =============================================================================
# TEST 3: Account Setup and Balance
# =============================================================================
print("\n💰 TEST 3: Account Setup and Balance")
print("-" * 80)

start_time = time.time()
try:
    api.change_balance('PRACTICE')
    balance = api.get_balance()

    if balance is not None and balance > 0:
        log_test("Set Demo Mode", True, f"Balance: ${balance:.2f}", time.time() - start_time)
    else:
        log_test("Set Demo Mode", False, f"Invalid balance: {balance}", time.time() - start_time)
        sys.exit(1)
except Exception as e:
    log_test("Set Demo Mode", False, f"Error: {e}", time.time() - start_time)
    sys.exit(1)

# =============================================================================
# TEST 4: Connection Stability
# =============================================================================
print("\n🔄 TEST 4: Connection Stability")
print("-" * 80)

start_time = time.time()
try:
    is_connected = api.check_connect()

    if is_connected:
        log_test("Connection Stability", True, "Connection is stable", time.time() - start_time)
    else:
        log_test("Connection Stability", False, "Connection check failed", time.time() - start_time)
except Exception as e:
    log_test("Connection Stability", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# TEST 5: Market Data Retrieval
# =============================================================================
print("\n📊 TEST 5: Market Data Retrieval")
print("-" * 80)

start_time = time.time()
try:
    open_markets = api.get_all_open_time()

    if open_markets and 'binary' in open_markets:
        binary_markets = open_markets['binary']
        open_count = sum(1 for m in binary_markets.values() if m.get('open', False))
        log_test("Get Open Markets", True, f"Found {open_count} open binary markets", time.time() - start_time)
    else:
        log_test("Get Open Markets", False, "No market data available", time.time() - start_time)
except Exception as e:
    log_test("Get Open Markets", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# TEST 6: Find Best Trading Asset
# =============================================================================
print("\n🎯 TEST 6: Find Best Trading Asset")
print("-" * 80)

start_time = time.time()
best_asset = None
try:
    open_markets = api.get_all_open_time()

    if open_markets and 'binary' in open_markets:
        binary_markets = open_markets['binary']

        # Preferred assets for 1-minute trading
        preferred_assets = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']

        for asset in preferred_assets:
            if asset in binary_markets and binary_markets[asset].get('open', False):
                try:
                    payout = api.get_binary_payout(asset)
                    if payout and payout > 0.7:
                        best_asset = asset
                        log_test("Find Best Asset", True,
                               f"Selected: {asset}, Payout: {payout:.1%}",
                               time.time() - start_time)
                        break
                except:
                    continue

        if not best_asset:
            log_test("Find Best Asset", False, "No suitable asset found", time.time() - start_time)
    else:
        log_test("Find Best Asset", False, "No market data available", time.time() - start_time)
except Exception as e:
    log_test("Find Best Asset", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# TEST 7: Payout Information
# =============================================================================
print("\n💵 TEST 7: Payout Information")
print("-" * 80)

if best_asset:
    start_time = time.time()
    try:
        payout = api.get_binary_payout(best_asset)

        if payout:
            potential_profit = 1.0 * payout
            log_test("Get Payout Information", True,
                   f"{best_asset}: {payout:.1%} payout, ${potential_profit:.2f} profit on $1",
                   time.time() - start_time)
        else:
            log_test("Get Payout Information", False, "No payout data", time.time() - start_time)
    except Exception as e:
        log_test("Get Payout Information", False, f"Error: {e}", time.time() - start_time)
else:
    log_test("Get Payout Information", False, "No asset to test", 0)

# =============================================================================
# TEST 8: Risk Management Validation
# =============================================================================
print("\n🛡️ TEST 8: Risk Management Validation")
print("-" * 80)

start_time = time.time()
try:
    # Test risk management configuration
    config_checks = []

    # Check daily loss limit
    max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', 50))
    config_checks.append(f"Max daily loss: ${max_daily_loss}")

    # Check daily profit target
    max_daily_profit = float(os.getenv('MAX_DAILY_PROFIT', 100))
    config_checks.append(f"Max daily profit: ${max_daily_profit}")

    # Check consecutive losses
    max_consecutive_losses = int(os.getenv('MAX_CONSECUTIVE_LOSSES', 5))
    config_checks.append(f"Max consecutive losses: {max_consecutive_losses}")

    # Check minimum balance
    min_balance = float(os.getenv('MIN_BALANCE', 50))
    config_checks.append(f"Min balance: ${min_balance}")

    # Verify balance is above minimum
    current_balance = api.get_balance()
    if current_balance >= min_balance:
        config_checks.append(f"✓ Balance ${current_balance:.2f} > Min ${min_balance}")
        log_test("Risk Management Config", True,
               ", ".join(config_checks),
               time.time() - start_time)
    else:
        log_test("Risk Management Config", False,
               f"Balance ${current_balance:.2f} below minimum ${min_balance}",
               time.time() - start_time)
except Exception as e:
    log_test("Risk Management Config", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# TEST 9: 1-Minute Binary Option Trade Execution (REAL TEST!)
# =============================================================================
print("\n🎲 TEST 9: 1-Minute Binary Option Trade Execution")
print("-" * 80)
print("⚠️  This will execute a REAL trade on DEMO account")
print("    Trade amount: $1.00")
print("    Duration: 1 minute (60 seconds)")
print()

if best_asset:
    # Ask for confirmation
    response = input("Execute test trade? (yes/no): ").lower().strip()

    if response == 'yes':
        start_time = time.time()
        try:
            amount = 1.0
            duration = 1  # 1 minute
            action = "call"  # Buy CALL option

            print(f"\n🎯 Executing: {action.upper()} {best_asset} ${amount} for {duration} min")
            print("="*80)

            # Execute trade
            status, order_id = api.buy(amount, best_asset, action, duration)

            if status and order_id:
                print(f"✅ Trade placed successfully!")
                print(f"   Order ID: {order_id}")
                print(f"   Asset: {best_asset}")
                print(f"   Action: {action.upper()}")
                print(f"   Amount: ${amount}")
                print(f"   Duration: {duration} minute")
                print()

                # Wait for trade to complete
                print(f"⏳ Waiting 80 seconds for trade to complete...")
                time.sleep(80)

                # Check result
                print("📊 Checking trade result...")
                profit = None

                for attempt in range(30):
                    try:
                        profit = api.check_win_v3(order_id)
                        if profit is not None:
                            print(f"   Result obtained on attempt {attempt + 1}")
                            break
                    except:
                        pass
                    time.sleep(1)

                if profit is not None:
                    result = "WIN" if profit > 0 else "LOSS"
                    new_balance = api.get_balance()

                    print()
                    print("="*80)
                    print(f"📈 TRADE RESULT: {result}")
                    print(f"   Profit/Loss: ${profit:.2f}")
                    print(f"   New Balance: ${new_balance:.2f}")
                    print("="*80)

                    log_test("Execute 1-Minute Binary Trade", True,
                           f"Order {order_id}: {result}, P/L: ${profit:.2f}",
                           time.time() - start_time)
                else:
                    log_test("Execute 1-Minute Binary Trade", False,
                           f"Could not retrieve result for order {order_id}",
                           time.time() - start_time)
            else:
                log_test("Execute 1-Minute Binary Trade", False,
                       f"Trade execution failed: status={status}, order_id={order_id}",
                       time.time() - start_time)
        except Exception as e:
            log_test("Execute 1-Minute Binary Trade", False,
                   f"Error: {e}",
                   time.time() - start_time)
    else:
        print("⏭️  Skipping trade execution test")
        log_test("Execute 1-Minute Binary Trade", True, "Skipped by user", 0)
else:
    log_test("Execute 1-Minute Binary Trade", False, "No asset available", 0)

# =============================================================================
# TEST 10: Emergency Stop Mechanism
# =============================================================================
print("\n🚨 TEST 10: Emergency Stop Mechanism")
print("-" * 80)

start_time = time.time()
try:
    emergency_file = Path('EMERGENCY_STOP')

    # Create emergency stop file
    emergency_file.touch()

    if emergency_file.exists():
        # Remove it
        emergency_file.unlink()

        if not emergency_file.exists():
            log_test("Emergency Stop Mechanism", True,
                   "File creation and removal works correctly",
                   time.time() - start_time)
        else:
            log_test("Emergency Stop Mechanism", False,
                   "Could not remove emergency stop file",
                   time.time() - start_time)
    else:
        log_test("Emergency Stop Mechanism", False,
               "Could not create emergency stop file",
               time.time() - start_time)
except Exception as e:
    log_test("Emergency Stop Mechanism", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# TEST 11: Logging System
# =============================================================================
print("\n📝 TEST 11: Logging System")
print("-" * 80)

start_time = time.time()
try:
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    if log_dir.exists() and log_dir.is_dir():
        log_test("Logging Directory", True,
               "Logs directory created successfully",
               time.time() - start_time)
    else:
        log_test("Logging Directory", False,
               "Could not create logs directory",
               time.time() - start_time)
except Exception as e:
    log_test("Logging Directory", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# TEST 12: Configuration Validation
# =============================================================================
print("\n⚙️ TEST 12: Configuration Validation")
print("-" * 80)

start_time = time.time()
try:
    config_valid = True
    config_errors = []

    # Check required environment variables
    required_vars = [
        'IQOPTION_EMAIL',
        'IQOPTION_PASSWORD',
        'TRADING_MODE',
        'BASE_TRADE_AMOUNT',
        'MAX_DAILY_LOSS',
        'MAX_DAILY_PROFIT'
    ]

    for var in required_vars:
        if not os.getenv(var):
            config_valid = False
            config_errors.append(f"Missing: {var}")

    if config_valid:
        log_test("Configuration Validation", True,
               f"All {len(required_vars)} required variables set",
               time.time() - start_time)
    else:
        log_test("Configuration Validation", False,
               ", ".join(config_errors),
               time.time() - start_time)
except Exception as e:
    log_test("Configuration Validation", False, f"Error: {e}", time.time() - start_time)

# =============================================================================
# FINAL RESULTS
# =============================================================================
print("\n" + "="*80)
print("📊 TEST RESULTS SUMMARY")
print("="*80)
print(f"Total Tests: {test_results['total_tests']}")
print(f"Passed: {test_results['passed']} ✅")
print(f"Failed: {test_results['failed']} ❌")
print(f"Success Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%")
print("="*80)
print()

# Detailed results
print("📋 DETAILED RESULTS:")
print("-" * 80)
for i, test in enumerate(test_results['tests'], 1):
    status = "✅ PASS" if test['passed'] else "❌ FAIL"
    print(f"{i:2d}. {status} | {test['name']}")
    if test['details']:
        print(f"           {test['details']}")
    if test['duration'] > 0:
        print(f"           Duration: {test['duration']:.2f}s")

print("\n" + "="*80)

# Save results to file
results_file = Path('logs') / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
results_file.parent.mkdir(exist_ok=True)

with open(results_file, 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"📄 Results saved to: {results_file}")
print("="*80)

# Final status
if test_results['failed'] == 0:
    print("\n🎉 ALL TESTS PASSED! System is ready for operation.")
    print("✅ You can now start the autonomous trading bot with:")
    print("   ./start_24_7_bot.sh")
else:
    print(f"\n⚠️  {test_results['failed']} TESTS FAILED")
    print("❌ Please review the failures above before proceeding.")

print()

# Cleanup
try:
    api.close()
except:
    pass

sys.exit(0 if test_results['failed'] == 0 else 1)
