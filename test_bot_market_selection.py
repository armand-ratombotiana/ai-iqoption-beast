#!/usr/bin/env python3
"""
Quick test to verify bot can find available markets
"""

import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, '/app/app/KAEL/KAEL/src')

from iqoptionapi.stable_api import IQ_Option
import logging

# Simple logger
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

def get_best_asset(api, logger):
    """Test version of get_best_asset from bot"""
    try:
        open_markets = api.get_all_open_time()

        if not open_markets or 'binary' not in open_markets:
            logger.warning("⚠️  No binary markets data available")
            return None

        binary_markets = open_markets['binary']

        # Check preferred assets first (try both regular and -op suffix)
        preferred = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'EURJPY', 'GBPJPY']

        for asset in preferred:
            asset = asset.strip()

            # Try regular asset name
            if asset in binary_markets and binary_markets[asset].get('open', False):
                logger.info(f"📊 Selected preferred asset: {asset}")
                return asset

            # Try with -op suffix (IQ Option format)
            asset_op = f"{asset}-op"
            if asset_op in binary_markets and binary_markets[asset_op].get('open', False):
                logger.info(f"📊 Selected preferred asset (op): {asset_op}")
                return asset_op

            # Try with -OTC suffix
            asset_otc = f"{asset}-OTC"
            if asset_otc in binary_markets and binary_markets[asset_otc].get('open', False):
                logger.info(f"📊 Selected preferred asset (OTC): {asset_otc}")
                return asset_otc

        # If no preferred asset available, find any open market
        # Prioritize forex pairs over other assets
        open_assets = [(asset, info) for asset, info in binary_markets.items() if info.get('open', False)]

        if not open_assets:
            logger.warning("⚠️  No open markets found")
            return None

        # Sort: prefer forex (contains USD, EUR, GBP, JPY) over OTC
        def sort_key(item):
            asset, _ = item
            # Prefer non-OTC forex pairs
            is_otc = 'OTC' in asset
            is_forex = any(curr in asset for curr in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'NZD', 'CHF'])
            return (is_otc, not is_forex, asset)

        open_assets.sort(key=sort_key)
        selected_asset = open_assets[0][0]

        logger.info(f"📊 Selected available asset: {selected_asset}")
        logger.info(f"   Total {len(open_assets)} markets available")

        return selected_asset

    except Exception as e:
        logger.error(f"❌ Error finding asset: {e}")
        return None

def main():
    print("="*70)
    print("🧪 BOT MARKET SELECTION TEST")
    print("="*70)

    email = os.getenv('IQOPTION_EMAIL')
    password = os.getenv('IQOPTION_PASSWORD')

    if not email or not password:
        print("❌ No credentials found!")
        return 1

    print(f"\n📧 Connecting...")

    # Connect
    api = IQ_Option(email, password)
    check, reason = api.connect()

    if not check:
        print(f"❌ Connection failed: {reason}")
        return 1

    print("✅ Connected!")
    api.change_balance('PRACTICE')

    print("\n" + "="*70)
    print("🔍 TESTING MARKET SELECTION")
    print("="*70 + "\n")

    # Test market selection 5 times
    for i in range(5):
        print(f"\nAttempt {i+1}:")
        asset = get_best_asset(api, logger)
        if asset:
            print(f"✅ Found asset: {asset}")
        else:
            print(f"❌ No asset found")

    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)

    return 0

if __name__ == '__main__':
    sys.exit(main())
