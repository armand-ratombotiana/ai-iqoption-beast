"""Trading state model"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict


@dataclass
class TradingState:
    """Tracks trading statistics and state"""

    # Daily statistics
    daily_loss: float = 0.0
    daily_profit: float = 0.0
    trades_today: int = 0
    last_reset: date = field(default_factory=lambda: datetime.now().date())

    # Streak tracking
    consecutive_losses: int = 0
    consecutive_wins: int = 0

    # Martingale
    martingale_level: int = 0

    # Overall statistics
    total_trades: int = 0
    total_wins: int = 0
    total_losses: int = 0
    total_profit: float = 0.0

    def reset_daily(self):
        """Reset daily statistics"""
        today = datetime.now().date()
        if self.last_reset != today:
            self.daily_loss = 0.0
            self.daily_profit = 0.0
            self.trades_today = 0
            self.last_reset = today

    def record_win(self, profit: float):
        """Record a winning trade"""
        self.daily_profit += profit
        self.total_profit += profit
        self.trades_today += 1
        self.total_trades += 1
        self.total_wins += 1

        self.consecutive_wins += 1
        self.consecutive_losses = 0
        self.martingale_level = 0  # Reset Martingale on win

    def record_loss(self, loss: float):
        """Record a losing trade"""
        self.daily_loss += abs(loss)
        self.total_profit += loss  # loss is negative
        self.trades_today += 1
        self.total_trades += 1
        self.total_losses += 1

        self.consecutive_losses += 1
        self.consecutive_wins = 0
        self.martingale_level += 1

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.total_wins / self.total_trades) * 100

    @property
    def daily_net(self) -> float:
        """Calculate daily net profit/loss"""
        return self.daily_profit - self.daily_loss

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'daily_loss': self.daily_loss,
            'daily_profit': self.daily_profit,
            'daily_net': self.daily_net,
            'trades_today': self.trades_today,
            'last_reset': self.last_reset.isoformat(),
            'consecutive_losses': self.consecutive_losses,
            'consecutive_wins': self.consecutive_wins,
            'martingale_level': self.martingale_level,
            'total_trades': self.total_trades,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'total_profit': self.total_profit,
            'win_rate': round(self.win_rate, 2),
        }
