"""API routes"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict

# Import IQOption API (will be in src/iqoptionapi after reorganization)
try:
    from src.iqoptionapi.stable_api import IQ_Option
except ImportError:
    try:
        from iqoptionapi.stable_api import IQ_Option
    except ImportError:
        IQ_Option = None  # Will fail at runtime if actually needed

# Handle both package and standalone imports
try:
    from ..models.signal import Signal
    from ..models.trade import Trade
    from ..core.signal_validator import SignalValidator
    from ..core.risk_manager import RiskManager
    from ..core.position_sizer import PositionSizer
    from ..core.trade_executor import TradeExecutor
    from ..core.state_manager import StateManager
except ImportError:
    from models.signal import Signal
    from models.trade import Trade
    from core.signal_validator import SignalValidator
    from core.risk_manager import RiskManager
    from core.position_sizer import PositionSizer
    from core.trade_executor import TradeExecutor
    from core.state_manager import StateManager

# Create blueprint
trading_bp = Blueprint('trading', __name__)

# Global state manager (singleton)
state_manager = StateManager()


def get_config() -> Dict:
    """Get configuration from app context"""
    return current_app.config['TRADING_CONFIG'].to_dict()


@trading_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


@trading_bp.route('/status', methods=['GET'])
def get_status():
    """Get current trading status and statistics"""
    config = get_config()
    state = state_manager.get_state()

    return jsonify({
        'status': 'active',
        'tradingState': state.to_dict(),
        'config': config,
        'timestamp': datetime.now().isoformat()
    })


@trading_bp.route('/reset', methods=['POST'])
def reset_state():
    """Manually reset trading state"""
    data = request.json or {}
    reset_type = data.get('type', 'daily')

    if reset_type == 'daily':
        state_manager.reset_daily_stats()
    elif reset_type == 'martingale':
        state_manager.reset_martingale()
    elif reset_type == 'full':
        state_manager.reset_all()
    else:
        return jsonify({
            'success': False,
            'error': f'Invalid reset type: {reset_type}'
        }), 400

    current_app.logger.info(f"State reset: {reset_type}")

    return jsonify({
        'success': True,
        'message': f'{reset_type} reset completed',
        'tradingState': state_manager.get_state().to_dict()
    })


@trading_bp.route('/trade', methods=['POST'])
def execute_trade():
    """
    Execute a trade with AI signal validation and risk management

    Expected JSON:
    {
        "email": "your@email.com",
        "password": "yourpassword",
        "action": "call" or "put",
        "pair": "EURUSD",
        "confidence": 75,
        "amount": 1 (optional),
        "duration": 1 (optional),
        "accountType": "demo" or "real"
    }
    """
    try:
        data = request.json

        # Validate required fields
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
        confidence = float(data.get('confidence', 60))
        account_type = data.get('accountType', 'demo')

        # Get configuration
        config = get_config()

        current_app.logger.info(f"Trade request: {action.upper()} {pair} @ {confidence}%")

        # Create and validate signal
        try:
            signal = Signal(
                action=action,
                pair=pair,
                confidence=confidence
            )
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

        # Validate signal
        validator = SignalValidator(config['MIN_CONFIDENCE_THRESHOLD'])
        is_valid, validation_msg = validator.validate(signal)

        if not is_valid:
            return jsonify({
                'success': False,
                'error': validation_msg,
                'tradingState': state_manager.get_state().to_dict()
            }), 400

        current_app.logger.info(f"Signal validated: {validation_msg}")

        # Connect to IQOption
        api = IQ_Option(email, password)
        check, reason = api.connect()

        if not check:
            return jsonify({
                'success': False,
                'error': f'Connection failed: {reason}'
            }), 400

        current_app.logger.info("Connected to IQOption")

        # Set account type
        if account_type == 'real':
            api.change_balance('REAL')
        else:
            api.change_balance('PRACTICE')

        # Verify connection
        if not api.check_connect():
            return jsonify({
                'success': False,
                'error': 'Connection check failed'
            }), 400

        # Get balance
        balance = api.get_balance()
        current_app.logger.info(f"Balance: ${balance:.2f}")

        # Get current state
        state = state_manager.get_state()

        # Check risk guards
        risk_manager = RiskManager(config)
        trade_allowed, risk_msg = risk_manager.check_risk_guards(state, balance)

        if not trade_allowed:
            return jsonify({
                'success': False,
                'error': f'Risk Guard: {risk_msg}',
                'tradingState': state.to_dict(),
                'balance': balance
            }), 403

        current_app.logger.info(f"Risk guard: {risk_msg}")

        # Calculate trade parameters
        position_sizer = PositionSizer(config)
        calculated_amount, calculated_duration = position_sizer.calculate_parameters(
            confidence,
            balance,
            state.martingale_level
        )

        # Use provided values or calculated ones
        amount = float(data.get('amount', calculated_amount))
        duration = int(data.get('duration', calculated_duration))

        current_app.logger.info(
            f"Trade sizing: ${amount} @ {duration}m "
            f"(Martingale: {state.martingale_level})"
        )

        # Create trade
        trade = Trade(
            pair=pair,
            action=action,
            amount=amount,
            duration=duration,
            confidence=confidence,
            account_type=account_type,
            martingale_level=state.martingale_level
        )

        # Execute trade
        executor = TradeExecutor(api)
        result = executor.execute(trade)

        if not result.success:
            return jsonify({
                'success': False,
                'error': result.error,
                'errorCode': result.error_code
            }), 400

        # Wait for result
        result = executor.wait_for_result(trade)

        if not result.success:
            return jsonify({
                'success': False,
                'error': result.error,
                'errorCode': result.error_code
            }), 500

        # Update state
        state_manager.update_after_trade(trade)

        # Get updated state
        updated_state = state_manager.get_state()

        current_app.logger.info(
            f"Daily P/L: +${updated_state.daily_profit:.2f} / "
            f"-${updated_state.daily_loss:.2f}"
        )

        # Return response
        return jsonify({
            'success': True,
            'trade': trade.to_dict(),
            'tradingState': updated_state.to_dict(),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"Trade execution error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@trading_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@trading_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
