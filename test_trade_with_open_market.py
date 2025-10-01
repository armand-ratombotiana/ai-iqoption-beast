"""
Test trade execution with an open market
"""
import sys
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

import requests
import time
from iqoptionapi.stable_api import IQ_Option

EMAIL = "tombokael4@gmail.com"
PASSWORD = "tombokael04"
API_URL = "http://localhost:5000"

def find_open_market():
    """Find an open binary options market"""
    print("Finding open market...")

    api = IQ_Option(EMAIL, PASSWORD)
    check, reason = api.connect()

    if not check:
        print(f"Connection failed: {reason}")
        return None

    api.change_balance('PRACTICE')
    open_times = api.get_all_open_time()

    if 'binary' in open_times:
        open_markets = [pair for pair, status in open_times['binary'].items()
                       if status.get('open', False)]

        # Prefer common forex pairs
        preferred = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
        for pair in preferred:
            if pair in open_markets:
                return pair

        # Return first available if no preferred pair is open
        if open_markets:
            return open_markets[0]

    return None

def test_trade_execution():
    """Test trade execution with an open market"""
    print("\n" + "="*70)
    print("TRADE EXECUTION TEST WITH OPEN MARKET")
    print("="*70 + "\n")

    # Find open market
    market = find_open_market()

    if not market:
        print("❌ No open markets found. Markets may be closed.")
        print("ℹ️  Binary options markets are typically closed on weekends")
        return False

    print(f"✓ Found open market: {market}")
    print(f"ℹ️  Executing CALL trade with 75% confidence...")
    print(f"⚠️  This will take 1-2 minutes to complete\n")

    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "action": "call",
        "pair": market,
        "confidence": 75,
        "accountType": "demo"
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/trade",
            json=payload,
            timeout=300
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            print(f"✓ Trade executed successfully in {elapsed:.1f}s\n")

            print("TRADE DETAILS:")
            print(f"  Order ID: {data.get('orderId')}")
            print(f"  Action: {data.get('action', '').upper()}")
            print(f"  Pair: {data.get('pair')}")
            print(f"  Amount: ${data.get('amount'):.2f}")
            print(f"  Duration: {data.get('duration')} minute(s)")
            print(f"  Confidence: {data.get('confidence')}%")

            result = data.get('result', '')
            profit = data.get('profit', 0)

            print("\nRESULTS:")
            if result == 'win':
                print(f"  ✓ WIN - Profit: ${profit:.2f}")
            else:
                print(f"  ✗ LOSS - Loss: ${abs(profit):.2f}")

            print("\nBALANCE:")
            print(f"  Old: ${data.get('oldBalance', 0):.2f}")
            print(f"  New: ${data.get('newBalance', 0):.2f}")
            print(f"  Change: ${data.get('balanceChange', 0):.2f}")

            state = data.get('tradingState', {})
            print("\nTRADING STATE:")
            print(f"  Daily P/L: +${state.get('dailyProfit', 0):.2f} / -${state.get('dailyLoss', 0):.2f}")
            print(f"  Martingale Level: {state.get('martingaleLevel', 0)}")
            print(f"  Consecutive Losses: {state.get('consecutiveLosses', 0)}")
            print(f"  Trades Today: {state.get('tradesToday', 0)}")

            print("\n" + "="*70)
            print("✓ TRADE TEST PASSED")
            print("="*70)
            return True
        else:
            print(f"❌ Trade failed with status code: {response.status_code}")
            error_data = response.json()
            print(f"Error: {error_data.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_trade_execution()
    sys.exit(0 if success else 1)
