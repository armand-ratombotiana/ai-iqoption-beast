"""Position sizing and Martingale logic"""

import sys
import os
from typing import Dict, Tuple

# Add src to path for imports
if __name__ == '__main__' or 'src' not in sys.path[0]:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))



class PositionSizer:
    """Calculates optimal position sizes"""

    def __init__(self, config: Dict):
        self.config = config

    def calculate_trade_amount(
        self,
        confidence: float,
        balance: float,
        martingale_level: int
    ) -> float:
        """
        Calculate trade amount based on confidence, balance, and Martingale level

        Args:
            confidence: AI confidence (0-100)
            balance: Current account balance
            martingale_level: Current Martingale level

        Returns:
            Calculated trade amount
        """
        base_amount = self.config['BASE_TRADE_AMOUNT']

        # Apply Martingale multiplier
        martingale_factor = self.config['MARTINGALE_MULTIPLIER'] ** martingale_level

        # Apply confidence scaling
        confidence_factor = confidence / 100.0

        # Calculate amount
        amount = base_amount * martingale_factor * confidence_factor

        # Cap at maximum multiplier
        max_amount = base_amount * self.config['MAX_TRADE_MULTIPLIER']
        amount = min(amount, max_amount)

        # Cap at 5% of balance for safety
        max_balance_percent = balance * 0.05
        amount = min(amount, max_balance_percent)

        return round(amount, 2)

    def calculate_expiration(self, confidence: float) -> int:
        """
        Calculate trade expiration based on confidence

        Higher confidence = shorter expiration (more certain)
        Lower confidence = longer expiration (more time to be right)

        Args:
            confidence: AI confidence (0-100)

        Returns:
            Expiration time in minutes
        """
        if confidence >= 90:
            return 1
        elif confidence >= 80:
            return 2
        elif confidence >= 70:
            return 3
        else:
            return 5

    def calculate_parameters(
        self,
        confidence: float,
        balance: float,
        martingale_level: int
    ) -> Tuple[float, int]:
        """
        Calculate both amount and expiration

        Args:
            confidence: AI confidence (0-100)
            balance: Current account balance
            martingale_level: Current Martingale level

        Returns:
            Tuple of (amount, expiration)
        """
        amount = self.calculate_trade_amount(confidence, balance, martingale_level)
        expiration = self.calculate_expiration(confidence)
        return amount, expiration
