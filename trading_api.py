"""
Simple Flask API to execute trades from n8n

Improvements based on BOT_KAEL.py:
- Better connection validation
- Market status checking
- Payout information
- Improved result checking with retry loop
- Detailed error messages
"""
from flask import Flask, request, jsonify
from iqoptionapi.stable_api import IQ_Option
import time
import functools

app = Flask(__name__)

def reconnect_on_failure(func):
    """Decorator to handle automatic reconnection on failure"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}, reconnection attempt ({attempt + 1}/3)...")
                time.sleep(2)
        raise Exception("Failed after multiple reconnection attempts")
    return wrapper

@app.route('/trade', methods=['POST'])
def execute_trade():
    """
    Execute a trade based on n8n input
    Expected JSON payload:
    {
        "email": "your@email.com",
        "password": "yourpassword",
        "action": "call" or "put",
        "pair": "EURUSD",
        "amount": 1,
        "duration": 1,
        "accountType": "demo" or "real"
    }
    """
    try:
        data = request.json

        # Validate required parameters
        required = ['email', 'password', 'action', 'pair', 'amount']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Extract parameters
        email = data.get('email')
        password = data.get('password')
        action = data.get('action')  # 'call' or 'put'
        pair = data.get('pair')
        amount = float(data.get('amount', 1))
        duration = int(data.get('duration', 1))
        account_type = data.get('accountType', 'demo')

        print(f"[TRADE REQUEST] {action.upper()} {pair} ${amount} for {duration}min")

        # Connect to IQ Option
        api = IQ_Option(email, password)
        check, reason = api.connect()

        if not check:
            return jsonify({
                'success': False,
                'error': f'Connection failed: {reason}'
            }), 400

        print(f"[CONNECTED] Successfully connected to IQ Option")

        # Set account type
        if account_type == 'real':
            api.change_balance('REAL')
        else:
            api.change_balance('PRACTICE')

        # Verify connection is stable
        if not api.check_connect():
            return jsonify({
                'success': False,
                'error': 'Connection check failed'
            }), 400

        # Get initial balance
        balance = api.get_balance()
        print(f"[BALANCE] Current balance: ${balance}")

        # Validate market is open
        open_times = api.get_all_open_time()
        market_open = False

        if 'binary' in open_times:
            if pair in open_times['binary']:
                market_open = open_times['binary'][pair].get('open', False)

        if not market_open:
            return jsonify({
                'success': False,
                'error': f'Market {pair} is not open'
            }), 400

        print(f"[MARKET] {pair} is open")

        # Get payout information
        payout = None
        try:
            payout = api.get_binary_payout(pair)
            if payout:
                potential_profit = amount * payout
                print(f"[PAYOUT] {payout:.2%} | Potential profit: ${potential_profit:.2f}")
        except:
            pass

        # Execute trade
        print(f"[EXECUTING] {action.upper()} trade...")
        status, order_id = api.buy(amount, pair, action, duration)

        if not status or order_id is None:
            return jsonify({
                'success': False,
                'error': 'Trade execution failed',
                'details': f'Status: {status}, Order ID: {order_id}'
            }), 400

        print(f"[PLACED] Trade placed successfully, Order ID: {order_id}")

        # Wait for result
        wait_time = duration * 60 + 5
        print(f"[WAITING] Waiting {wait_time}s for trade to complete...")
        time.sleep(wait_time)

        # Check result with retry loop (like BOT_KAEL.py)
        print(f"[CHECKING] Checking result...")
        profit = None
        max_attempts = 20

        for attempt in range(max_attempts):
            try:
                profit = api.check_win_v3(order_id)
                if profit is not None:
                    break
            except Exception as e:
                print(f"[RETRY] Result check error: {e}")

            time.sleep(0.5)

        if profit is None:
            return jsonify({
                'success': False,
                'error': 'Result not available after multiple attempts'
            }), 500

        # Get new balance
        new_balance = api.get_balance()
        balance_change = new_balance - balance

        result = 'win' if profit > 0 else 'loss'
        print(f"[RESULT] {result.upper()} - Profit: ${profit:.2f}, Balance: ${balance:.2f} -> ${new_balance:.2f}")

        return jsonify({
            'success': True,
            'orderId': order_id,
            'action': action,
            'pair': pair,
            'amount': amount,
            'duration': duration,
            'profit': profit,
            'result': result,
            'payout': payout,
            'oldBalance': balance,
            'newBalance': new_balance,
            'balanceChange': balance_change,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
