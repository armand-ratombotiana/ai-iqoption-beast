"""Signal validation logic"""

from typing import Tuple
from ..models.signal import Signal


class SignalValidator:
    """Validates trading signals"""

    def __init__(self, min_confidence: float = 60):
        self.min_confidence = min_confidence

    def validate(self, signal: Signal) -> Tuple[bool, str]:
        """
        Validate a trading signal

        Args:
            signal: Signal to validate

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check action
        if signal.action not in ['call', 'put']:
            return False, f'Invalid action: {signal.action}. Must be call or put'

        # Check confidence
        if signal.confidence < self.min_confidence:
            return False, f'Confidence {signal.confidence}% below threshold {self.min_confidence}%'

        return True, 'Signal validated'

    def set_min_confidence(self, min_confidence: float):
        """Update minimum confidence threshold"""
        self.min_confidence = min_confidence
