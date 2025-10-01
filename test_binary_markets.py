"""
Binary Options Market Analysis and Testing
Focus on identifying and testing open binary markets
"""
import sys
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime

EMAIL = "tombokael4@gmail.com"
PASSWORD = "tombokael04"

print("\n" + "="*80)
print("BINARY OPTIONS MARKET ANALYSIS")
print("="*80 + "\n")

# Connect to IQ Option
print("Connecting to IQ Option...")
api = IQ_Option(EMAIL, PASSWORD)
check, reason = api.connect()

if not check:
    print(f"❌ Connection failed: {reason}")
    sys.exit(1)

print("✓ Connected successfully\n")

# Set to practice account
api.change_balance('PRACTICE')
balance = api.get_balance()
print(f"Practice Balance: ${balance:.2f}\n")

# Get all open times
print("Fetching market data...")
open_times = api.get_all_open_time()

# Analyze binary markets
print("\n" + "="*80)
print("BINARY OPTIONS MARKETS ANALYSIS")
print("="*80 + "\n")

binary_markets = {}
if 'binary' in open_times:
    for pair, status in open_times['binary'].items():
        if status.get('open', False):
            binary_markets[pair] = status

print(f"Total Binary Markets Open: {len(binary_markets)}\n")

# Categorize markets
forex_pairs = []
commodities = []
crypto = []
stocks = []
indices = []
otc_markets = []

for pair in binary_markets.keys():
    pair_upper = pair.upper()

    # Categorize
    if '-OTC' in pair_upper:
        otc_markets.append(pair)
    elif any(curr in pair_upper for curr in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']):
        if not any(x in pair_upper for x in ['BTC', 'ETH', 'LTC', 'XRP']):
            forex_pairs.append(pair)
    elif any(crypto in pair_upper for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'DOG', 'ADA', 'SOL']):
        crypto.append(pair)
    elif any(idx in pair_upper for idx in ['SPX', 'DOW', 'NASDAQ', 'FTSE', 'DAX', 'CAC', 'NIKKEI']):
        indices.append(pair)
    elif any(comm in pair_upper for comm in ['OIL', 'GOLD', 'SILVER', 'GAS', 'BRENT', 'WTI']):
        commodities.append(pair)
    else:
        stocks.append(pair)

# Display categorized markets
print("┌─────────────────────────────────────────────────────────────────────────────┐")
print("│ MARKET CATEGORY           COUNT    SAMPLE PAIRS                            │")
print("├─────────────────────────────────────────────────────────────────────────────┤")
print(f"│ Forex (Non-OTC)           {len(forex_pairs):3d}      {', '.join(forex_pairs[:3]):<40} │" if forex_pairs else "│ Forex (Non-OTC)             0      None available                               │")
print(f"│ OTC Markets               {len(otc_markets):3d}      {', '.join(otc_markets[:3]):<40} │")
print(f"│ Cryptocurrencies          {len(crypto):3d}      {', '.join(crypto[:3]):<40} │" if crypto else "│ Cryptocurrencies            0      None available                               │")
print(f"│ Commodities               {len(commodities):3d}      {', '.join(commodities[:3]):<40} │" if commodities else "│ Commodities                 0      None available                               │")
print(f"│ Stocks                    {len(stocks):3d}      {', '.join(stocks[:3]):<40} │" if stocks else "│ Stocks                      0      None available                               │")
print(f"│ Indices                   {len(indices):3d}      {', '.join(indices[:3]):<40} │" if indices else "│ Indices                     0      None available                               │")
print("└─────────────────────────────────────────────────────────────────────────────┘")

# Select best markets for testing
print("\n" + "="*80)
print("RECOMMENDED MARKETS FOR BINARY OPTIONS TRADING")
print("="*80 + "\n")

recommended = []

# Prefer non-OTC forex pairs (most reliable)
if forex_pairs:
    print("✓ Non-OTC Forex Pairs (Best for binary options):")
    for pair in forex_pairs[:5]:
        print(f"  • {pair}")
        recommended.append(pair)
else:
    print("⚠️  No non-OTC forex pairs currently open")

# Fallback to OTC if no regular forex
if not forex_pairs and otc_markets:
    print("\n✓ OTC Markets (Available):")
    # Prefer common OTC forex pairs
    preferred_otc = [p for p in otc_markets if any(x in p.upper() for x in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'])]

    if preferred_otc:
        for pair in preferred_otc[:5]:
            print(f"  • {pair}")
            recommended.append(pair)
    else:
        # Use any OTC
        for pair in otc_markets[:5]:
            print(f"  • {pair}")
            recommended.append(pair)

if not recommended:
    print("\n❌ No suitable binary options markets found!")
    print("ℹ️  Binary options markets are typically closed on weekends")
    sys.exit(1)

# Test payout for recommended markets
print("\n" + "="*80)
print("PAYOUT ANALYSIS FOR RECOMMENDED MARKETS")
print("="*80 + "\n")

print("┌─────────────────────────────────────────────────────────────────────────────┐")
print("│ PAIR                          PAYOUT %     STATUS                           │")
print("├─────────────────────────────────────────────────────────────────────────────┤")

best_market = None
best_payout = 0

for pair in recommended[:10]:
    try:
        payout = api.get_binary_payout(pair)
        if payout:
            payout_pct = payout * 100
            status = "✓ Good" if payout >= 0.7 else "⚠ Low"
            print(f"│ {pair:<30} {payout_pct:6.1f}%      {status:<33} │")

            if payout > best_payout:
                best_payout = payout
                best_market = pair
        else:
            print(f"│ {pair:<30} N/A         ⚠ No payout info                     │")
    except Exception as e:
        print(f"│ {pair:<30} ERROR       ❌ {str(e)[:30]:<30} │")

print("└─────────────────────────────────────────────────────────────────────────────┘")

if best_market:
    print(f"\n🎯 BEST MARKET IDENTIFIED: {best_market}")
    print(f"   Payout: {best_payout*100:.1f}%")
    print(f"   Expected profit on $1 trade: ${best_payout:.2f}")

# Get candles for best market to verify data availability
if best_market:
    print(f"\n📊 Testing data availability for {best_market}...")
    try:
        candles = api.get_candles(best_market, 60, 10, time.time())
        if candles:
            print(f"✓ Successfully retrieved {len(candles)} candles")
            print(f"  Latest price: {candles[-1]['close']}")
            print(f"  Timeframe: 1 minute")
        else:
            print("⚠️  No candle data available")
    except Exception as e:
        print(f"⚠️  Error getting candles: {str(e)}")

# Export recommended markets for testing
print("\n" + "="*80)
print("MARKETS SELECTED FOR TRADE TESTING")
print("="*80 + "\n")

test_markets = recommended[:2] if len(recommended) >= 2 else recommended

for i, market in enumerate(test_markets, 1):
    print(f"{i}. {market}")
    try:
        payout = api.get_binary_payout(market)
        if payout:
            print(f"   Payout: {payout*100:.1f}%")
    except:
        pass

# Save to file for next test
with open('/tmp/test_markets.txt', 'w') as f:
    for market in test_markets:
        f.write(f"{market}\n")

print("\n✓ Market analysis complete!")
print(f"✓ Selected {len(test_markets)} markets for testing")
print("✓ Markets saved to /tmp/test_markets.txt")

print("\n" + "="*80)
