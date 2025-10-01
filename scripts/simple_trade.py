"""
Simple trade execution script for testing
Usage: python3 simple_trade.py

Improvements based on BOT_KAEL.py:
- Reconnection decorator for reliability
- Connection validation
- Better error handling
- Market validation
- Payout checking
- Improved result checking loop
"""
from iqoptionapi.stable_api import IQ_Option
import time
import functools

def reconnect_on_failure(func):
    """Decorator to handle automatic reconnection on failure"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):  # 3 attempts
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"⚠️  Error: {e}, reconnection attempt ({attempt + 1}/3)...")
                time.sleep(2)
        raise Exception("Failed after multiple reconnection attempts")
    return wrapper

def execute_simple_trade(email, password, action, pair, amount, duration, account_type="demo"):
    """
    Execute a simple trade

    Args:
        email: IQ Option email
        password: IQ Option password
        action: 'call' or 'put'
        pair: Trading pair (e.g., 'EURUSD')
        amount: Trade amount
        duration: Duration in minutes
        account_type: 'demo' or 'real'
    """
    print(f"Connecting to IQ Option...")
    api = IQ_Option(email, password)
    check, reason = api.connect()

    if not check:
        print(f"❌ Connection failed: {reason}")
        return None

    print(f"✅ Connected successfully!")

    # Set account type
    if account_type == 'real':
        api.change_balance('REAL')
        print("Using REAL account")
    else:
        api.change_balance('PRACTICE')
        print("Using DEMO account")

    # Verify connection is stable
    if not api.check_connect():
        print(f"❌ Connection check failed")
        return None

    # Get current balance
    balance = api.get_balance()
    print(f"Current balance: ${balance}")

    # Validate market is open
    print(f"\n🔍 Validating market status...")
    open_times = api.get_all_open_time()
    market_open = False

    if 'binary' in open_times:
        if pair in open_times['binary']:
            market_open = open_times['binary'][pair].get('open', False)

    if not market_open:
        print(f"❌ Market {pair} is not open!")
        print(f"   Try checking available markets with check_markets.py")
        return None

    print(f"✅ Market {pair} is open")

    # Get payout information
    try:
        payout = api.get_binary_payout(pair)
        if payout:
            potential_profit = amount * payout
            print(f"💰 Payout: {payout:.2%} | Potential profit: ${potential_profit:.2f}")
    except:
        print(f"⚠️  Could not fetch payout information")

    # Execute trade
    print(f"\n📊 Executing {action.upper()} trade on {pair}")
    print(f"   Amount: ${amount}")
    print(f"   Duration: {duration} minute(s)")

    try:
        status, order_id = api.buy(amount, pair, action, duration)

        if not status or order_id is None:
            print(f"❌ Trade execution failed!")
            print(f"   Status: {status}, Order ID: {order_id}")
            return None

        print(f"✅ Trade placed successfully!")
        print(f"   Order ID: {order_id}")
    except Exception as e:
        print(f"❌ Trade execution error: {e}")
        return None

    # Wait for trade to complete
    wait_time = duration * 60 + 5
    print(f"\n⏳ Waiting {wait_time} seconds for trade to complete...")

    for i in range(wait_time, 0, -1):
        print(f"   Time remaining: {i}s", end='\r')
        time.sleep(1)

    # Check result with retry loop (like BOT_KAEL.py)
    print("\n\n📊 Checking result...")
    profit = None
    max_attempts = 20

    for attempt in range(max_attempts):
        try:
            profit = api.check_win_v3(order_id)
            if profit is not None:
                break
        except Exception as e:
            print(f"⚠️  Result check error: {e}", end='\r')

        time.sleep(0.5)

    if profit is None:
        print("❌ Result not available after multiple attempts")
        return None

    # Display result with detailed info
    if profit > 0:
        print(f"✅ WIN! Profit: ${profit:.2f}")
        payout_percent = (profit / amount) * 100
        print(f"   Payout received: {payout_percent:.1f}%")
    else:
        print(f"❌ LOSS! Loss: ${abs(profit):.2f}")

    # Get new balance
    new_balance = api.get_balance()
    balance_change = new_balance - balance

    print(f"\n💵 Balance Summary:")
    print(f"   Old balance: ${balance:.2f}")
    print(f"   New balance: ${new_balance:.2f}")

    if balance_change > 0:
        print(f"   Change: +${balance_change:.2f} ✅")
    else:
        print(f"   Change: ${balance_change:.2f} ❌")

    return {
        'success': True,
        'orderId': order_id,
        'action': action,
        'pair': pair,
        'amount': amount,
        'duration': duration,
        'profit': profit,
        'result': 'win' if profit > 0 else 'loss',
        'oldBalance': balance,
        'newBalance': new_balance,
        'balanceChange': balance_change,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

if __name__ == '__main__':
    # Test configuration
    EMAIL = "tombokael4@gmail.com"
    PASSWORD = "tombokael04"
    ACTION = "call"  # or "put"
    PAIR = "AUDCHF-OTC"  # Using OTC pair that's currently open
    AMOUNT = 1
    DURATION = 1  # minutes
    ACCOUNT_TYPE = "demo"

    print("=" * 60)
    print("SIMPLE TRADE EXECUTION TEST")
    print("=" * 60)

    result = execute_simple_trade(
        email=EMAIL,
        password=PASSWORD,
        action=ACTION,
        pair=PAIR,
        amount=AMOUNT,
        duration=DURATION,
        account_type=ACCOUNT_TYPE
    )

    if result:
        print("\n" + "=" * 60)
        print("TRADE COMPLETED SUCCESSFULLY")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("TRADE FAILED")
        print("=" * 60)
