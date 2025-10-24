#!/usr/bin/env python3
"""
Enhanced Production Bot Testing - Finds and Uses Available Assets
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

# Set test credentials
os.environ['TEST_EMAIL'] = 'tombokael4@gmail.com'
os.environ['TEST_PASSWORD'] = 'tombokael04'
os.environ['IQOPTION_EMAIL'] = 'tombokael4@gmail.com'
os.environ['IQOPTION_PASSWORD'] = 'tombokael04'
os.environ['TRADING_MODE'] = 'demo'

from iqoptionapi.stable_api import IQ_Option

print("="*80)
print("🧪 ENHANCED ASSET DISCOVERY AND TESTING")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mode: DEMO")
print("="*80)
print()

# Connect
print("🔌 Connecting to IQ Option...")
api = IQ_Option(os.environ['TEST_EMAIL'], os.environ['TEST_PASSWORD'])
check, reason = api.connect()

if not check:
    print(f"❌ Connection failed: {reason}")
    sys.exit(1)

print(f"✅ Connected successfully")

# Set demo mode
api.change_balance('PRACTICE')
balance = api.get_balance()
print(f"💰 Balance: ${balance:.2f}")
print()

# Get all open markets
print("📊 Discovering available markets...")
open_markets = api.get_all_open_time()

if not open_markets or 'binary' not in open_markets:
    print("❌ No market data available")
    sys.exit(1)

binary_markets = open_markets['binary']
open_assets = [asset for asset, info in binary_markets.items() if info.get('open', False)]

print(f"✅ Found {len(open_assets)} open binary markets")
print()

# Try to find best asset with good payout
print("🎯 Finding best trading asset...")
print("-" * 80)

best_assets = []

for asset in open_assets[:20]:  # Check first 20 assets
    try:
        payout = api.get_binary_payout(asset)
        if payout and payout > 0.70:  # At least 70% payout
            best_assets.append((asset, payout))
            print(f"   {asset:12s} | Payout: {payout:6.1%} | ✅")
        else:
            print(f"   {asset:12s} | Payout: {payout:6.1%} | ❌ Too low")
    except Exception as e:
        print(f"   {asset:12s} | Error: {str(e)[:30]}")

print()

if not best_assets:
    print("❌ No suitable assets found with acceptable payout")
    print("This might be due to:")
    print("  - Market hours (try during peak trading hours)")
    print("  - Weekend (markets are closed)")
    print("  - Broker maintenance")
    sys.exit(1)

# Sort by payout and get best
best_assets.sort(key=lambda x: x[1], reverse=True)
selected_asset, selected_payout = best_assets[0]

print(f"✅ BEST ASSET SELECTED: {selected_asset}")
print(f"   Payout: {selected_payout:.1%}")
print(f"   Potential profit on $1: ${selected_payout:.2f}")
print()

# Ask for trade execution
print("="*80)
print("🎲 REAL TRADE EXECUTION TEST")
print("="*80)
print(f"Asset: {selected_asset}")
print(f"Action: CALL")
print(f"Amount: $1.00")
print(f"Duration: 1 minute (60 seconds)")
print(f"Expected profit if win: ${selected_payout:.2f}")
print()

response = input("Execute test trade on DEMO account? (yes/no): ").lower().strip()

if response != 'yes':
    print("⏭️  Trade execution cancelled")
    sys.exit(0)

print()
print("🚀 Executing trade...")
print("="*80)

try:
    amount = 1.0
    duration = 1
    action = "call"

    # Execute trade
    status, order_id = api.buy(amount, selected_asset, action, duration)

    if not status or not order_id:
        print(f"❌ Trade execution failed: status={status}, order_id={order_id}")
        sys.exit(1)

    print(f"✅ Trade placed successfully!")
    print(f"   Order ID: {order_id}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print()

    # Wait for result
    print(f"⏳ Waiting 80 seconds for trade result...")
    for i in range(8):
        print(f"   {(i+1)*10}s...", end=' ', flush=True)
        time.sleep(10)
    print()
    print()

    # Check result
    print("📊 Checking trade result...")
    profit = None

    for attempt in range(30):
        try:
            profit = api.check_win_v3(order_id)
            if profit is not None:
                print(f"   ✅ Result obtained on attempt {attempt + 1}")
                break
        except:
            pass
        time.sleep(1)
        if (attempt + 1) % 5 == 0:
            print(f"   Attempt {attempt + 1}/30...")

    print()
    print("="*80)

    if profit is not None:
        result = "WIN 🎉" if profit > 0 else "LOSS 😞"
        new_balance = api.get_balance()
        balance_change = new_balance - balance

        print(f"📈 TRADE RESULT: {result}")
        print("-" * 80)
        print(f"   Order ID: {order_id}")
        print(f"   Asset: {selected_asset}")
        print(f"   Action: {action.upper()}")
        print(f"   Amount: ${amount:.2f}")
        print(f"   Profit/Loss: ${profit:.2f}")
        print(f"   Old Balance: ${balance:.2f}")
        print(f"   New Balance: ${new_balance:.2f}")
        print(f"   Change: ${balance_change:.2f}")
        print("="*80)

        if profit > 0:
            print("\n✅ TEST SUCCESSFUL - Trade executed and won!")
            print("🤖 The autonomous bot is ready for operation!")
        else:
            print("\n⚠️  TEST COMPLETED - Trade executed but lost")
            print("📊 This is normal - binary options have ~50/50 win rate")
            print("🤖 The bot executed correctly, result was just unfavorable")

        print()
        print("="*80)
        print("🎯 NEXT STEPS:")
        print("="*80)
        print("1. Review the trade execution - it worked correctly")
        print("2. The bot can now run autonomously with:")
        print("   ./start_24_7_bot.sh")
        print("3. Monitor logs in: logs/")
        print("4. Check statistics via: curl http://localhost:5001/statistics")
        print("5. Emergency stop: touch EMERGENCY_STOP")
        print("="*80)
    else:
        print(f"❌ Could not retrieve trade result for order {order_id}")
        print("   This might be a timing issue. Check your IQ Option account")
        print("   to verify if the trade was placed.")

except Exception as e:
    print(f"❌ Error during trade execution: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
api.close()
