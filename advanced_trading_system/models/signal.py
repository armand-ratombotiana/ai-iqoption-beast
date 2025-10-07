"""Signal model for AI trading signals"""

from dataclasses import dataclass
from typing import Literal
from datetime import datetime


@dataclass
class Signal:
    """Represents a trading signal from AI"""

    action: Literal['call', 'put']
    pair: str
    confidence: float
    timestamp: datetime = None
    source: str = 'ai'

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

        # Normalize action to lowercase
        self.action = self.action.lower()

        # Validate action
        if self.action not in ['call', 'put']:
            raise ValueError(f"Invalid action: {self.action}. Must be 'call' or 'put'")

        # Validate confidence
        if not 0 <= self.confidence <= 100:
            raise ValueError(f"Confidence must be between 0 and 100, got {self.confidence}")

    def is_valid(self, min_confidence: float = 60) -> bool:
        """Check if signal meets minimum requirements"""
        return self.confidence >= min_confidence

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'action': self.action,
            'pair': self.pair,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }
