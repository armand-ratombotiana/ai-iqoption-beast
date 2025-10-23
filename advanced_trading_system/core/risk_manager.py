"""Risk management logic"""

import sys
import os
from typing import Tuple, Dict

# Add src to path for imports
if __name__ == '__main__' or 'src' not in sys.path[0]:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from models.state import TradingState
except ImportError:
    from src.models.state import TradingState


class RiskManager:
    """Manages trading risk and enforces limits"""

    def __init__(self, config: Dict):
        self.config = config

    def check_risk_guards(self, state: TradingState, balance: float) -> Tuple[bool, str]:
        """
        Check all risk guards before allowing a trade

        Args:
            state: Current trading state
            balance: Current account balance

        Returns:
            Tuple of (trade_allowed, reason)
        """
        # Ensure daily stats are current
        state.reset_daily()

        # Balance check
        if balance < self.config['MIN_BALANCE']:
            return False, f'Balance ${balance:.2f} below minimum ${self.config["MIN_BALANCE"]}'

        # Daily loss limit
        if state.daily_loss >= self.config['MAX_DAILY_LOSS']:
            return False, (
                f'Daily loss limit reached: ${state.daily_loss:.2f} >= '
                f'${self.config["MAX_DAILY_LOSS"]}'
            )

        # Daily profit target
        if state.daily_profit >= self.config['MAX_DAILY_PROFIT']:
            return False, (
                f'Daily profit target reached: ${state.daily_profit:.2f} >= '
                f'${self.config["MAX_DAILY_PROFIT"]}'
            )

        # Consecutive losses
        if state.consecutive_losses >= self.config['MAX_CONSECUTIVE_LOSSES']:
            return False, (
                f'Consecutive losses limit reached: {state.consecutive_losses} >= '
                f'{self.config["MAX_CONSECUTIVE_LOSSES"]}'
            )

        # Martingale level limit
        if state.martingale_level >= self.config['MAX_MARTINGALE_LEVEL']:
            return False, (
                f'Martingale level limit reached: {state.martingale_level} >= '
                f'{self.config["MAX_MARTINGALE_LEVEL"]}'
            )

        return True, 'Risk checks passed'

    def should_stop_trading(self, state: TradingState) -> Tuple[bool, str]:
        """
        Check if trading should be halted

        Args:
            state: Current trading state

        Returns:
            Tuple of (should_stop, reason)
        """
        # Check if daily limits reached
        if state.daily_loss >= self.config['MAX_DAILY_LOSS']:
            return True, 'Daily loss limit reached'

        if state.daily_profit >= self.config['MAX_DAILY_PROFIT']:
            return True, 'Daily profit target reached'

        # Check consecutive losses
        if state.consecutive_losses >= self.config['MAX_CONSECUTIVE_LOSSES']:
            return True, 'Consecutive losses limit reached'

        return False, 'Continue trading'
