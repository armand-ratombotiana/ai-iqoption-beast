#!/usr/bin/env python3
"""
Test script to check what markets are actually available
"""

import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, '/app/app/KAEL/KAEL/src')

from iqoptionapi.stable_api import IQ_Option
import json
import time

def main():
    print("="*70)
    print("🔍 MARKET AVAILABILITY CHECKER")
    print("="*70)

    email = os.getenv('IQOPTION_EMAIL')
    password = os.getenv('IQOPTION_PASSWORD')

    if not email or not password:
        print("❌ No credentials found!")
        return 1

    print(f"\n📧 Connecting with: {email}")

    # Connect
    api = IQ_Option(email, password)
    check, reason = api.connect()

    if not check:
        print(f"❌ Connection failed: {reason}")
        return 1

    print("✅ Connected!")

    # Switch to practice
    api.change_balance('PRACTICE')
    print("✅ Demo mode activated")

    balance = api.get_balance()
    print(f"💰 Balance: ${balance:.2f}")

    print("\n" + "="*70)
    print("📊 CHECKING MARKET AVAILABILITY")
    print("="*70)

    # Get all open time
    print("\n1. Getting all open time data...")
    open_markets = api.get_all_open_time()

    if not open_markets:
        print("❌ No market data received!")
        return 1

    print(f"✅ Received market data with keys: {list(open_markets.keys())}")

    # Check binary markets
    if 'binary' in open_markets:
        print("\n2. Binary markets found!")
        binary_markets = open_markets['binary']
        print(f"   Total binary markets: {len(binary_markets)}")

        # Check which are open
        open_count = 0
        closed_count = 0
        open_assets = []

        for asset, info in binary_markets.items():
            is_open = info.get('open', False)
            if is_open:
                open_count += 1
                open_assets.append(asset)
            else:
                closed_count += 1

        print(f"   Open: {open_count}")
        print(f"   Closed: {closed_count}")

        if open_assets:
            print(f"\n3. Open assets (showing first 10):")
            for asset in open_assets[:10]:
                info = binary_markets[asset]
                print(f"   - {asset}")
                print(f"     Status: {info}")

                # Try to get payout
                try:
                    payout = api.get_binary_payout(asset)
                    print(f"     Payout: {payout:.1%}" if payout else "     Payout: N/A")
                except Exception as e:
                    print(f"     Payout error: {e}")
        else:
            print("\n❌ No open binary markets found!")
            print("\n4. Sample of closed markets:")
            closed_assets = [a for a, i in binary_markets.items() if not i.get('open', False)]
            for asset in closed_assets[:5]:
                info = binary_markets[asset]
                print(f"   - {asset}: {info}")
    else:
        print("❌ No 'binary' key in market data!")
        print(f"Available keys: {list(open_markets.keys())}")

    # Check digital markets
    if 'digital' in open_markets:
        print("\n5. Digital markets found!")
        digital_markets = open_markets['digital']
        print(f"   Total digital markets: {len(digital_markets)}")

        open_digital = [a for a, i in digital_markets.items() if i.get('open', False)]
        print(f"   Open digital markets: {len(open_digital)}")

        if open_digital:
            print(f"   Sample open digital assets:")
            for asset in open_digital[:5]:
                print(f"   - {asset}")

    # Try checking specific preferred assets
    print("\n" + "="*70)
    print("6. CHECKING PREFERRED ASSETS")
    print("="*70)

    preferred = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'EURJPY', 'GBPJPY']

    for asset in preferred:
        print(f"\n{asset}:")

        if 'binary' in open_markets and asset in open_markets['binary']:
            info = open_markets['binary'][asset]
            is_open = info.get('open', False)
            print(f"  Binary: {'OPEN ✅' if is_open else 'CLOSED ❌'}")
            print(f"  Info: {info}")

            if is_open:
                try:
                    payout = api.get_binary_payout(asset)
                    print(f"  Payout: {payout:.1%}" if payout else "  Payout: N/A")
                except Exception as e:
                    print(f"  Payout error: {e}")
        else:
            print(f"  Binary: NOT FOUND")

        if 'digital' in open_markets and asset in open_markets['digital']:
            info = open_markets['digital'][asset]
            is_open = info.get('open', False)
            print(f"  Digital: {'OPEN ✅' if is_open else 'CLOSED ❌'}")
        else:
            print(f"  Digital: NOT FOUND")

    print("\n" + "="*70)
    print("✅ MARKET CHECK COMPLETE")
    print("="*70)

    return 0

if __name__ == '__main__':
    sys.exit(main())
