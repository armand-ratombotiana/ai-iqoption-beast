"""Trade model for tracking trades"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class TradeStatus(Enum):
    """Trade status enumeration"""
    PENDING = "pending"
    EXECUTED = "executed"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"


@dataclass
class Trade:
    """Represents a single trade"""

    pair: str
    action: Literal['call', 'put']
    amount: float
    duration: int
    confidence: float
    account_type: Literal['demo', 'real'] = 'demo'

    # Execution details
    order_id: Optional[int] = None
    status: TradeStatus = TradeStatus.PENDING
    executed_at: Optional[datetime] = None

    # Results
    profit: Optional[float] = None
    payout: Optional[float] = None
    old_balance: Optional[float] = None
    new_balance: Optional[float] = None

    # Risk management
    martingale_level: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def execute(self, order_id: int, old_balance: float, payout: float):
        """Mark trade as executed"""
        self.order_id = order_id
        self.status = TradeStatus.EXECUTED
        self.executed_at = datetime.now()
        self.old_balance = old_balance
        self.payout = payout

    def complete(self, profit: float, new_balance: float):
        """Mark trade as completed with result"""
        self.profit = profit
        self.new_balance = new_balance
        self.status = TradeStatus.WON if profit > 0 else TradeStatus.LOST

    def cancel(self, reason: str = None):
        """Cancel trade"""
        self.status = TradeStatus.CANCELLED

    @property
    def is_win(self) -> bool:
        """Check if trade was won"""
        return self.status == TradeStatus.WON

    @property
    def is_loss(self) -> bool:
        """Check if trade was lost"""
        return self.status == TradeStatus.LOST

    @property
    def is_complete(self) -> bool:
        """Check if trade is complete"""
        return self.status in [TradeStatus.WON, TradeStatus.LOST]

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'pair': self.pair,
            'action': self.action,
            'amount': self.amount,
            'duration': self.duration,
            'confidence': self.confidence,
            'account_type': self.account_type,
            'order_id': self.order_id,
            'status': self.status.value,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'profit': self.profit,
            'payout': self.payout,
            'old_balance': self.old_balance,
            'new_balance': self.new_balance,
            'martingale_level': self.martingale_level,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class TradeResult:
    """Result of a trade operation"""

    success: bool
    trade: Optional[Trade] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary"""
        result = {
            'success': self.success,
        }

        if self.trade:
            result['trade'] = self.trade.to_dict()

        if self.error:
            result['error'] = self.error

        if self.error_code:
            result['error_code'] = self.error_code

        return result
