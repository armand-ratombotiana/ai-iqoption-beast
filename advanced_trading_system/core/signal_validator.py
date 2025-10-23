"""Signal validation logic"""

import sys
import os
from typing import Tuple

# Add src to path for imports
if __name__ == '__main__' or 'src' not in sys.path[0]:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from models.signal import Signal
except ImportError:
    from src.models.signal import Signal


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
