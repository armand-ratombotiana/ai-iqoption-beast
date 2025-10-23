"""
Production-Ready Flask API for IQOption AI Binary Trading Bot

Enhanced Features:
- AI Signal Validation with confidence thresholds
- Advanced Risk Management (daily loss/profit limits, consecutive losses, balance checks)
- Dynamic Trade Sizing with Martingale strategy
- Market status checking and payout information
- Comprehensive error handling and retry mechanisms
- Session persistence and state tracking
- Detailed logging and monitoring
"""
import sys
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

from flask import Flask, request, jsonify
from iqoptionapi.stable_api import IQ_Option
import time
import functools
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

# Global state tracking for risk management
trading_state = {
    'daily_loss': 0.0,
    'daily_profit': 0.0,
    'consecutive_losses': 0,
    'consecutive_wins': 0,
    'martingale_level': 0,
    'last_reset': datetime.now().date(),
    'trades_today': 0,
    'total_trades': 0
}

# Configuration from environment variables
CONFIG = {
    'MAX_DAILY_LOSS': float(os.getenv('MAX_DAILY_LOSS', 50)),
    'MAX_DAILY_PROFIT': float(os.getenv('MAX_DAILY_PROFIT', 100)),
    'MAX_CONSECUTIVE_LOSSES': int(os.getenv('MAX_CONSECUTIVE_LOSSES', 3)),
    'MIN_BALANCE': float(os.getenv('MIN_BALANCE', 50)),
    'MARTINGALE_MULTIPLIER': float(os.getenv('MARTINGALE_MULTIPLIER', 1.5)),
    'MAX_MARTINGALE_LEVEL': int(os.getenv('MAX_MARTINGALE_LEVEL', 4)),
    'MIN_CONFIDENCE_THRESHOLD': int(os.getenv('MIN_CONFIDENCE_THRESHOLD', 60)),
    'BASE_TRADE_AMOUNT': float(os.getenv('BASE_TRADE_AMOUNT', 1)),
    'MAX_TRADE_MULTIPLIER': float(os.getenv('MAX_TRADE_MULTIPLIER', 5))
}

def reset_daily_stats():
    """Reset daily statistics if new day"""
    global trading_state
    today = datetime.now().date()
    if trading_state['last_reset'] != today:
        trading_state['daily_loss'] = 0.0
        trading_state['daily_profit'] = 0.0
        trading_state['trades_today'] = 0
        trading_state['last_reset'] = today
        print(f"[RESET] Daily statistics reset for {today}")

def validate_signal(signal, confidence):
    """
    Validate AI signal meets requirements
    Returns: (is_valid, reason)
    """
    signal_upper = signal.upper() if signal else None

    if signal_upper not in ['CALL', 'PUT']:
        return False, f'Invalid signal: {signal}. Must be CALL or PUT'

    if confidence < CONFIG['MIN_CONFIDENCE_THRESHOLD']:
        return False, f'Confidence {confidence}% below threshold {CONFIG["MIN_CONFIDENCE_THRESHOLD"]}%'

    return True, 'Signal validated'

def check_risk_guard(balance):
    """
    Comprehensive risk management checks
    Returns: (trade_allowed, reason)
    """
    reset_daily_stats()

    # Balance check
    if balance < CONFIG['MIN_BALANCE']:
        return False, f'Balance ${balance:.2f} below minimum ${CONFIG["MIN_BALANCE"]}'

    # Daily loss limit
    if trading_state['daily_loss'] >= CONFIG['MAX_DAILY_LOSS']:
        return False, f'Daily loss limit reached: ${trading_state["daily_loss"]:.2f} >= ${CONFIG["MAX_DAILY_LOSS"]}'

    # Daily profit target
    if trading_state['daily_profit'] >= CONFIG['MAX_DAILY_PROFIT']:
        return False, f'Daily profit target reached: ${trading_state["daily_profit"]:.2f} >= ${CONFIG["MAX_DAILY_PROFIT"]}'

    # Consecutive losses
    if trading_state['consecutive_losses'] >= CONFIG['MAX_CONSECUTIVE_LOSSES']:
        return False, f'Consecutive losses limit reached: {trading_state["consecutive_losses"]} >= {CONFIG["MAX_CONSECUTIVE_LOSSES"]}'

    # Martingale level limit
    if trading_state['martingale_level'] >= CONFIG['MAX_MARTINGALE_LEVEL']:
        return False, f'Martingale level limit reached: {trading_state["martingale_level"]} >= {CONFIG["MAX_MARTINGALE_LEVEL"]}'

    return True, 'Risk checks passed'

def calculate_trade_amount(confidence, balance):
    """
    Calculate dynamic trade amount based on:
    - Base amount
    - Confidence level
    - Martingale level
    - Account balance
    """
    base_amount = CONFIG['BASE_TRADE_AMOUNT']

    # Martingale multiplier
    martingale_factor = CONFIG['MARTINGALE_MULTIPLIER'] ** trading_state['martingale_level']

    # Confidence scaling (60-100% confidence scales from 0.6x to 1.0x)
    confidence_factor = (confidence / 100.0)

    # Calculate amount
    amount = base_amount * martingale_factor * confidence_factor

    # Cap at maximum multiplier
    max_amount = base_amount * CONFIG['MAX_TRADE_MULTIPLIER']
    amount = min(amount, max_amount)

    # Ensure we don't exceed 5% of balance
    max_balance_percent = balance * 0.05
    amount = min(amount, max_balance_percent)

    return round(amount, 2)

def calculate_expiration(confidence):
    """
    Calculate trade expiration based on confidence
    Higher confidence = shorter expiration (more certain)
    Lower confidence = longer expiration (more time to be right)
    """
    # Scale from 60-100% confidence to 1-5 minutes
    # 100% confidence = 1 minute
    # 60% confidence = 5 minutes
    if confidence >= 90:
        return 1
    elif confidence >= 80:
        return 2
    elif confidence >= 70:
        return 3
    else:
        return 5

def update_trade_result(profit):
    """Update trading state based on trade result"""
    global trading_state

    if profit > 0:
        trading_state['daily_profit'] += profit
        trading_state['consecutive_wins'] += 1
        trading_state['consecutive_losses'] = 0
        trading_state['martingale_level'] = 0  # Reset Martingale on win
        print(f"[WIN] Consecutive wins: {trading_state['consecutive_wins']}, Martingale reset")
    else:
        loss = abs(profit)
        trading_state['daily_loss'] += loss
        trading_state['consecutive_losses'] += 1
        trading_state['consecutive_wins'] = 0
        trading_state['martingale_level'] = min(
            trading_state['martingale_level'] + 1,
            CONFIG['MAX_MARTINGALE_LEVEL']
        )
        print(f"[LOSS] Consecutive losses: {trading_state['consecutive_losses']}, Martingale level: {trading_state['martingale_level']}")

    trading_state['trades_today'] += 1
    trading_state['total_trades'] += 1

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
    Execute a trade with full AI signal validation and risk management

    Expected JSON payload:
    {
        "email": "your@email.com",
        "password": "yourpassword",
        "action": "call" or "put",
        "pair": "EURUSD",
        "amount": 1,  # Optional - will be calculated if not provided
        "duration": 1,  # Optional - will be calculated based on confidence
        "confidence": 75,  # Required for AI-driven trading
        "accountType": "demo" or "real"
    }
    """
    try:
        data = request.json

        # Validate required parameters
        required = ['email', 'password', 'action', 'pair']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Extract parameters
        email = data.get('email')
        password = data.get('password')
        action = data.get('action').lower()
        pair = data.get('pair')
        confidence = int(data.get('confidence', CONFIG['MIN_CONFIDENCE_THRESHOLD']))
        account_type = data.get('accountType', 'demo')

        print(f"\n{'='*60}")
        print(f"[TRADE REQUEST] {action.upper()} {pair} | Confidence: {confidence}%")
        print(f"{'='*60}")

        # Validate signal
        is_valid, validation_msg = validate_signal(action, confidence)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': validation_msg,
                'tradingState': trading_state.copy()
            }), 400

        print(f"[VALIDATION] {validation_msg}")

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
        print(f"[BALANCE] Current balance: ${balance:.2f}")

        # Risk Guard Check
        trade_allowed, risk_msg = check_risk_guard(balance)
        if not trade_allowed:
            return jsonify({
                'success': False,
                'error': f'Risk Guard: {risk_msg}',
                'tradingState': trading_state.copy(),
                'balance': balance
            }), 403

        print(f"[RISK GUARD] {risk_msg}")

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

        # Calculate dynamic trade parameters
        calculated_amount = calculate_trade_amount(confidence, balance)
        amount = data.get('amount', calculated_amount)

        calculated_duration = calculate_expiration(confidence)
        duration = int(data.get('duration', calculated_duration))

        print(f"[TRADE SIZING] Amount: ${amount} (Martingale Level: {trading_state['martingale_level']})")
        print(f"[EXPIRATION] Duration: {duration} minute(s)")

        # Get payout information
        payout = None
        potential_profit = 0
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

        # Check result with retry loop
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

        # Update trading state
        update_trade_result(profit)

        # Get new balance
        new_balance = api.get_balance()
        balance_change = new_balance - balance

        result = 'win' if profit > 0 else 'loss'
        print(f"[RESULT] {result.upper()} - Profit: ${profit:.2f}, Balance: ${balance:.2f} -> ${new_balance:.2f}")
        print(f"[STATS] Daily P/L: +${trading_state['daily_profit']:.2f} / -${trading_state['daily_loss']:.2f}")
        print(f"{'='*60}\n")

        return jsonify({
            'success': True,
            'orderId': order_id,
            'action': action,
            'pair': pair,
            'amount': amount,
            'duration': duration,
            'confidence': confidence,
            'profit': profit,
            'result': result,
            'payout': payout,
            'potentialProfit': potential_profit,
            'oldBalance': balance,
            'newBalance': new_balance,
            'balanceChange': balance_change,
            'tradingState': {
                'dailyProfit': trading_state['daily_profit'],
                'dailyLoss': trading_state['daily_loss'],
                'consecutiveLosses': trading_state['consecutive_losses'],
                'consecutiveWins': trading_state['consecutive_wins'],
                'martingaleLevel': trading_state['martingale_level'],
                'tradesToday': trading_state['trades_today'],
                'totalTrades': trading_state['total_trades']
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current trading status and statistics"""
    reset_daily_stats()
    return jsonify({
        'status': 'active',
        'tradingState': trading_state.copy(),
        'config': CONFIG,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/reset', methods=['POST'])
def reset_state():
    """Manually reset trading state (use with caution)"""
    global trading_state
    reset_type = request.json.get('type', 'daily')

    if reset_type == 'daily':
        trading_state['daily_loss'] = 0.0
        trading_state['daily_profit'] = 0.0
        trading_state['trades_today'] = 0
    elif reset_type == 'martingale':
        trading_state['martingale_level'] = 0
        trading_state['consecutive_losses'] = 0
    elif reset_type == 'full':
        trading_state = {
            'daily_loss': 0.0,
            'daily_profit': 0.0,
            'consecutive_losses': 0,
            'consecutive_wins': 0,
            'martingale_level': 0,
            'last_reset': datetime.now().date(),
            'trades_today': 0,
            'total_trades': 0
        }

    print(f"[RESET] State reset: {reset_type}")
    return jsonify({
        'success': True,
        'message': f'{reset_type} reset completed',
        'tradingState': trading_state.copy()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print("IQOption AI Binary Trading Bot API")
    print(f"{'='*60}")
    print(f"Configuration:")
    for key, value in CONFIG.items():
        print(f"  {key}: {value}")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
