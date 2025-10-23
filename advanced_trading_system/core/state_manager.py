"""Trading state management"""

from ..models.state import TradingState
from ..models.trade import Trade


class StateManager:
    """Manages trading state and statistics"""

    def __init__(self):
        self.state = TradingState()

    def get_state(self) -> TradingState:
        """Get current trading state"""
        self.state.reset_daily()
        return self.state

    def update_after_trade(self, trade: Trade):
        """
        Update state after a trade completes

        Args:
            trade: Completed trade
        """
        if not trade.is_complete:
            return

        if trade.is_win:
            self.state.record_win(trade.profit)
        else:
            self.state.record_loss(trade.profit)

    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.state.reset_daily()

    def reset_martingale(self):
        """Reset Martingale level"""
        self.state.martingale_level = 0
        self.state.consecutive_losses = 0

    def reset_all(self):
        """Full reset of all statistics"""
        self.state = TradingState()
