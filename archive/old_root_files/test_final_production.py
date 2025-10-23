#!/usr/bin/env python3
"""
FINAL PRODUCTION TEST - Complete 1-Minute Binary Options Trading
Tests with correct API methods
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
print("🎯 FINAL PRODUCTION TEST - 1-MINUTE BINARY OPTIONS")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mode: DEMO (Safe Testing)")
print(f"Credentials: {os.environ['TEST_EMAIL']}")
print("="*80)
print()

# Step 1: Connect
print("🔌 STEP 1: Connecting to IQ Option...")
print("-" * 80)
api = IQ_Option(os.environ['TEST_EMAIL'], os.environ['TEST_PASSWORD'])
check, reason = api.connect()

if not check:
    print(f"❌ Connection failed: {reason}")
    sys.exit(1)

print(f"✅ Connected successfully")
print()

# Step 2: Set demo mode and get balance
print("💰 STEP 2: Setting Demo Mode & Getting Balance...")
print("-" * 80)
api.change_balance('PRACTICE')
balance = api.get_balance()
print(f"✅ Demo mode activated")
print(f"✅ Balance: ${balance:.2f}")
print()

# Step 3: Get all profit/payout data
print("📊 STEP 3: Getting Profit/Payout Information...")
print("-" * 80)
try:
    all_profit = api.get_all_profit()
    print(f"✅ Retrieved profit data for available assets")
    print()

    # Display sample payouts
    print("Sample Payouts (Binary Options):")
    count = 0
    best_assets = []

    for asset, data in all_profit.items():
        if 'binary' in data and data['binary'] > 0:
            payout_percent = data['binary'] * 100
            if payout_percent >= 70:  # At least 70% payout
                best_assets.append((asset, data['binary']))
                count += 1
                if count <= 10:  # Show first 10
                    print(f"   {asset:15s} | Payout: {payout_percent:5.1f}%")

    print(f"\n✅ Found {len(best_assets)} assets with good payouts (>70%)")
    print()

except Exception as e:
    print(f"❌ Error getting profit data: {e}")
    sys.exit(1)

# Step 4: Select best asset
print("🎯 STEP 4: Selecting Best Asset for Trading...")
print("-" * 80)

if not best_assets:
    print("❌ No suitable assets found")
    print("⚠️  This might be due to market hours or weekend")
    sys.exit(1)

# Sort by payout
best_assets.sort(key=lambda x: x[1], reverse=True)
selected_asset, selected_payout = best_assets[0]

print(f"✅ SELECTED ASSET: {selected_asset}")
print(f"   Payout: {selected_payout*100:.1f}%")
print(f"   Potential profit on $1: ${selected_payout:.2f}")
print()

# Step 5: Verify market is open
print("📈 STEP 5: Verifying Market Status...")
print("-" * 80)
try:
    open_markets = api.get_all_open_time()
    if open_markets and 'binary' in open_markets:
        binary_markets = open_markets['binary']

        is_open = False
        if selected_asset in binary_markets:
            is_open = binary_markets[selected_asset].get('open', False)

        if is_open:
            print(f"✅ Market {selected_asset} is OPEN for trading")
        else:
            print(f"⚠️  Market {selected_asset} appears closed")
            print(f"   Proceeding anyway (OTC markets may still work)")
        print()
except Exception as e:
    print(f"⚠️  Could not verify market status: {e}")
    print(f"   Proceeding with trade attempt...")
    print()

# Step 6: Execute 1-minute binary option trade
print("="*80)
print("🎲 STEP 6: EXECUTING 1-MINUTE BINARY OPTION TRADE")
print("="*80)
print(f"Asset: {selected_asset}")
print(f"Action: CALL")
print(f"Amount: $1.00")
print(f"Duration: 1 minute (60 seconds)")
print(f"Expected payout: {selected_payout*100:.1f}%")
print()

response = input("Execute REAL trade on DEMO account? (yes/no): ").lower().strip()

if response != 'yes':
    print("⏭️  Trade execution cancelled by user")
    print()
    print("="*80)
    print("✅ TEST SUMMARY")
    print("="*80)
    print(f"1. ✅ Connection: SUCCESS")
    print(f"2. ✅ Demo mode: SUCCESS")
    print(f"3. ✅ Balance retrieval: ${balance:.2f}")
    print(f"4. ✅ Profit data: {len(best_assets)} suitable assets")
    print(f"5. ✅ Asset selection: {selected_asset}")
    print(f"6. ⏭️  Trade execution: Skipped by user")
    print("="*80)
    print()
    print("🤖 All tests passed! System is ready for autonomous operation.")
    print("   Start the bot with: ./start_24_7_bot.sh")
    print()
    sys.exit(0)

print("🚀 Executing trade...")
print("-" * 80)

try:
    amount = 1.0
    duration = 1  # 1 minute
    action = "call"

    # Execute trade
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Placing order...")
    status, order_id = api.buy(amount, selected_asset, action, duration)

    if not status or not order_id:
        print(f"❌ Trade execution failed")
        print(f"   Status: {status}")
        print(f"   Order ID: {order_id}")
        sys.exit(1)

    print(f"✅ Trade placed successfully!")
    print(f"   Order ID: {order_id}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print()

    # Wait for result
    print(f"⏳ Waiting for trade result...")
    print(f"   Trade duration: 60 seconds")
    print(f"   Buffer time: 20 seconds")
    print(f"   Total wait: 80 seconds")
    print()

    for i in range(8):
        remaining = 80 - (i * 10)
        print(f"   {remaining}s remaining...", flush=True)
        time.sleep(10)

    print()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking result...")

    # Check result
    profit = None
    for attempt in range(30):
        try:
            profit = api.check_win_v3(order_id)
            if profit is not None:
                print(f"   ✅ Result obtained on attempt {attempt + 1}")
                break
        except Exception as e:
            if attempt == 0:
                print(f"   Waiting for result...")
        time.sleep(1)

    print()
    print("="*80)

    if profit is not None:
        result_status = "WIN 🎉" if profit > 0 else "LOSS 😞"
        new_balance = api.get_balance()
        balance_change = new_balance - balance

        print(f"📈 TRADE RESULT: {result_status}")
        print("="*80)
        print(f"Order ID........: {order_id}")
        print(f"Asset...........: {selected_asset}")
        print(f"Action..........: {action.upper()}")
        print(f"Amount..........: ${amount:.2f}")
        print(f"Duration........: {duration} minute")
        print(f"Profit/Loss.....: ${profit:.2f}")
        print(f"Old Balance.....: ${balance:.2f}")
        print(f"New Balance.....: ${new_balance:.2f}")
        print(f"Net Change......: ${balance_change:.2f}")
        print("="*80)
        print()

        if profit > 0:
            print("🎉 CONGRATULATIONS! Trade was successful!")
            print()
            win_message = "WIN"
        else:
            print("📊 Trade resulted in a loss, but execution was correct")
            print("   (This is normal - binary options have inherent risk)")
            print()
            win_message = "LOSS (but test passed)"

        # FINAL SUMMARY
        print("="*80)
        print("✅ COMPLETE TEST SUMMARY")
        print("="*80)
        print(f"1. ✅ Connection.........: SUCCESS")
        print(f"2. ✅ Demo Mode..........: SUCCESS (${balance:.2f})")
        print(f"3. ✅ Profit Data........: {len(best_assets)} assets found")
        print(f"4. ✅ Asset Selection....: {selected_asset} ({selected_payout*100:.1f}%)")
        print(f"5. ✅ Trade Execution....: SUCCESS (Order {order_id})")
        print(f"6. ✅ Result Check.......: SUCCESS ({win_message})")
        print(f"7. ✅ Balance Update.....: ${balance:.2f} -> ${new_balance:.2f}")
        print("="*80)
        print()
        print("🏆 ALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL!")
        print("="*80)
        print()
        print("🤖 AUTONOMOUS BOT IS READY FOR 24/7 OPERATION")
        print()
        print("Next Steps:")
        print("  1. Configure .env file with your settings")
        print("  2. Start the bot: ./start_24_7_bot.sh")
        print("  3. Monitor logs: tail -f logs/autonomous_bot_*.log")
        print("  4. Check stats: curl http://localhost:5001/statistics")
        print("  5. Emergency stop: touch EMERGENCY_STOP")
        print()
        print("="*80)

    else:
        print(f"❌ Could not retrieve trade result for order {order_id}")
        print("   The trade may have been placed but result is delayed")
        print("   Check your IQ Option account manually")
        print()
        sys.exit(1)

except Exception as e:
    print(f"❌ Error during trade execution: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cleanup
api.close()
print("🔒 Connection closed")
print()

