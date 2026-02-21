from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from collections import deque
import statistics
import numpy as np

@dataclass
class TradeResult:
    """Single trade result"""
    strategy_name: str
    instrument: str
    direction: str
    amount: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    profit: Optional[float] = None
    won: Optional[bool] = None
    payout_ratio: float = 0.0
    confidence: float = 0.0
    execution_ms: Optional[int] = None

@dataclass
class StrategyMetrics:
    """Enhanced performance metrics for a single strategy"""
    strategy_name: str
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    avg_confidence: float = 0.0
    avg_payout: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    kelly_fraction: float = 0.0
    max_consecutive_losses: int = 0
    max_consecutive_wins: int = 0
    current_streak: int = 0  # Positive = wins, Negative = losses
    max_drawdown: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    risk_reward_ratio: float = 0.0
    expectancy: float = 0.0

    # Trade history
    profit_history: deque = field(default_factory=lambda: deque(maxlen=100))
    confidence_history: deque = field(default_factory=lambda: deque(maxlen=100))
    payout_history: deque = field(default_factory=lambda: deque(maxlen=100))
    drawdown_history: deque = field(default_factory=lambda: deque(maxlen=100))

    # Strategy calibration
    confidence_multiplier: float = 1.0
    volatility_factor: float = 1.0
    last_calibration: datetime = field(default_factory=datetime.now)
    
    def update(self, result: TradeResult):
        """Update metrics with new trade result"""
        self.total_trades += 1
        
        if result.won:
            self.wins += 1
            self.current_streak = max(0, self.current_streak) + 1
            self.max_consecutive_wins = max(self.max_consecutive_wins, self.current_streak)
        else:
            self.losses += 1
            self.current_streak = min(0, self.current_streak) - 1
            self.max_consecutive_losses = max(self.max_consecutive_losses, abs(self.current_streak))
            
        self.win_rate = self.wins / self.total_trades if self.total_trades > 0 else 0.0
        self.total_pnl += result.profit if result.profit is not None else 0

        # Update histories
        self.profit_history.append(result.profit if result.profit is not None else 0)
        self.confidence_history.append(result.confidence)
        self.payout_history.append(result.payout_ratio)
        
        # Calculate drawdown
        if self.profit_history:
            cumulative = np.cumsum(self.profit_history)
            peak = np.maximum.accumulate(cumulative)
            drawdown = (peak - cumulative) / peak
            current_dd = float(drawdown[-1]) if len(drawdown) > 0 else 0.0
            self.drawdown_history.append(current_dd)
            self.max_drawdown = float(max(self.drawdown_history))

        # Update averages
        if self.profit_history:
            wins = [p for p in self.profit_history if p > 0]
            losses = [p for p in self.profit_history if p < 0]
            
            self.avg_win = statistics.mean(wins) if wins else 0
            self.avg_loss = abs(statistics.mean(losses)) if losses else 0
            
            total_wins = sum(wins)
            total_losses = sum(abs(x) for x in losses)
            self.profit_factor = total_wins / total_losses if total_losses else float('inf')
            
            if self.avg_loss > 0:
                self.risk_reward_ratio = self.avg_win / self.avg_loss
            
            self.expectancy = (self.win_rate * self.avg_win) - ((1 - self.win_rate) * self.avg_loss)

        if self.confidence_history:
            self.avg_confidence = statistics.mean(self.confidence_history)
        if self.payout_history:
            self.avg_payout = statistics.mean(self.payout_history)

        # Calculate risk metrics
        if len(self.profit_history) >= 2:
            returns = np.array(self.profit_history)
            
            # Sharpe Ratio
            mean_return = np.mean(returns)
            std_return = np.std(returns, ddof=1)
            risk_free_rate = 0.0
            self.sharpe_ratio = (mean_return - risk_free_rate) / std_return if std_return > 0 else 0.0
            
            # Sortino Ratio (only considers negative returns)
            negative_returns = returns[returns < 0]
            downside_std = np.std(negative_returns, ddof=1) if len(negative_returns) > 0 else 1
            self.sortino_ratio = (mean_return - risk_free_rate) / downside_std if downside_std > 0 else 0.0

        # Calculate Kelly fraction
        if self.avg_payout > 0:
            self.kelly_fraction = self._calculate_kelly_fraction()

    def _calculate_kelly_fraction(self) -> float:
        """Calculate optimal Kelly Criterion bet size"""
        if self.avg_payout <= 0 or self.win_rate <= 0:
            return 0.0
            
        q = 1 - self.win_rate
        kelly = (self.win_rate * self.avg_payout - q) / self.avg_payout
        
        # Cap Kelly at 25% for safety
        return max(0.0, min(kelly, 0.25))

    def should_recalibrate(self, min_trades: int = 20, min_hours: float = 1.0) -> bool:
        """Check if strategy needs recalibration"""
        time_since = datetime.now() - self.last_calibration
        hours_since = time_since.total_seconds() / 3600
        return (self.total_trades >= min_trades and hours_since >= min_hours) or self.total_trades >= 50

    def recalibrate(self):
        """Adjust strategy parameters based on performance"""
        if self.total_trades < 10:
            return

        # Adjust confidence threshold based on win rate
        if self.win_rate < 0.55:
            self.confidence_multiplier = min(1.2, self.confidence_multiplier * 1.05)
        elif self.win_rate > 0.70:
            self.confidence_multiplier = max(0.9, self.confidence_multiplier * 0.98)

        # Adjust for volatility
        if self.profit_history:
            returns = np.array(self.profit_history)
            volatility = np.std(returns)
            target_vol = 0.02  # Target 2% volatility
            self.volatility_factor = min(1.5, max(0.5, target_vol / volatility if volatility > 0 else 1.0))

        self.last_calibration = datetime.now()

    def get_stats(self) -> Dict:
        """Get comprehensive strategy statistics"""
        return {
            'strategy_name': self.strategy_name,
            'performance': {
                'total_trades': self.total_trades,
                'wins': self.wins,
                'losses': self.losses,
                'win_rate': round(self.win_rate * 100, 2),
                'total_pnl': round(self.total_pnl, 2),
                'profit_factor': round(self.profit_factor, 3),
                'expectancy': round(self.expectancy, 3)
            },
            'risk_metrics': {
                'sharpe_ratio': round(self.sharpe_ratio, 3),
                'sortino_ratio': round(self.sortino_ratio, 3),
                'max_drawdown': round(self.max_drawdown * 100, 2),
                'kelly_fraction': round(self.kelly_fraction, 4)
            },
            'trade_metrics': {
                'avg_win': round(self.avg_win, 2),
                'avg_loss': round(self.avg_loss, 2),
                'risk_reward_ratio': round(self.risk_reward_ratio, 2),
                'avg_confidence': round(self.avg_confidence * 100, 2),
                'avg_payout': round(self.avg_payout, 4)
            },
            'streaks': {
                'max_consecutive_wins': self.max_consecutive_wins,
                'max_consecutive_losses': self.max_consecutive_losses,
                'current_streak': self.current_streak
            },
            'calibration': {
                'confidence_multiplier': round(self.confidence_multiplier, 3),
                'volatility_factor': round(self.volatility_factor, 3)
            }
        }