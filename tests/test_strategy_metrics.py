import pytest
from datetime import datetime
import numpy as np
from models.strategy_metrics import StrategyMetrics, TradeResult

def test_strategy_metrics_initialization():
    """Test StrategyMetrics initialization"""
    metrics = StrategyMetrics("test_strategy")
    assert metrics.strategy_name == "test_strategy"
    assert metrics.total_trades == 0
    assert metrics.wins == 0
    assert metrics.losses == 0
    assert metrics.win_rate == 0.0

def test_strategy_metrics_update():
    """Test updating metrics with trade results"""
    metrics = StrategyMetrics("test_strategy")
    
    # Test winning trade
    win_trade = TradeResult(
        strategy_name="test_strategy",
        instrument="EURUSD",
        direction="CALL",
        amount=1.0,
        entry_time=datetime.now(),
        exit_time=datetime.now(),
        profit=10.0,
        won=True,
        payout_ratio=0.8,
        confidence=0.75
    )
    metrics.update(win_trade)
    
    assert metrics.total_trades == 1
    assert metrics.wins == 1
    assert metrics.losses == 0
    assert metrics.win_rate == 1.0
    assert metrics.total_pnl == 10.0
    
    # Test losing trade
    loss_trade = TradeResult(
        strategy_name="test_strategy",
        instrument="EURUSD",
        direction="PUT",
        amount=1.0,
        entry_time=datetime.now(),
        exit_time=datetime.now(),
        profit=-1.0,
        won=False,
        payout_ratio=0.8,
        confidence=0.75
    )
    metrics.update(loss_trade)
    
    assert metrics.total_trades == 2
    assert metrics.wins == 1
    assert metrics.losses == 1
    assert metrics.win_rate == 0.5
    assert metrics.total_pnl == 9.0

def test_consecutive_trades():
    """Test consecutive wins/losses tracking"""
    metrics = StrategyMetrics("test_strategy")
    
    # Three consecutive wins
    for _ in range(3):
        win_trade = TradeResult(
            strategy_name="test_strategy",
            instrument="EURUSD",
            direction="CALL",
            amount=1.0,
            entry_time=datetime.now(),
            profit=1.0,
            won=True,
            payout_ratio=0.8,
            confidence=0.75
        )
        metrics.update(win_trade)
    
    assert metrics.max_consecutive_wins == 3
    assert metrics.current_streak == 3
    
    # Two consecutive losses
    for _ in range(2):
        loss_trade = TradeResult(
            strategy_name="test_strategy",
            instrument="EURUSD",
            direction="PUT",
            amount=1.0,
            entry_time=datetime.now(),
            profit=-1.0,
            won=False,
            payout_ratio=0.8,
            confidence=0.75
        )
        metrics.update(loss_trade)
    
    assert metrics.max_consecutive_losses == 2
    assert metrics.current_streak == -2

def test_risk_metrics():
    """Test risk metric calculations"""
    metrics = StrategyMetrics("test_strategy")
    
    # Add mixed profit/loss trades
    trades = [
        (1.0, True),   # Win
        (-1.0, False), # Loss
        (2.0, True),   # Win
        (1.5, True),   # Win
        (-1.0, False)  # Loss
    ]
    
    for profit, won in trades:
        trade = TradeResult(
            strategy_name="test_strategy",
            instrument="EURUSD",
            direction="CALL",
            amount=1.0,
            entry_time=datetime.now(),
            profit=profit,
            won=won,
            payout_ratio=0.8,
            confidence=0.75
        )
        metrics.update(trade)
    
    # Verify risk metrics
    assert metrics.win_rate == 0.6  # 3 wins out of 5
    assert metrics.total_pnl == 2.5  # Sum of all profits
    assert metrics.avg_win > 0
    assert metrics.avg_loss < 0
    assert metrics.risk_reward_ratio > 0
    assert metrics.max_drawdown >= 0
    assert metrics.sharpe_ratio != 0
    assert metrics.sortino_ratio != 0

def test_kelly_criterion():
    """Test Kelly Criterion calculation"""
    metrics = StrategyMetrics("test_strategy")
    
    # Add trades with consistent payout
    for _ in range(10):
        trade = TradeResult(
            strategy_name="test_strategy",
            instrument="EURUSD",
            direction="CALL",
            amount=1.0,
            entry_time=datetime.now(),
            profit=0.8,
            won=True,
            payout_ratio=0.8,
            confidence=0.75
        )
        metrics.update(trade)
    
    assert 0 <= metrics.kelly_fraction <= 0.25  # Should be capped at 25%

def test_recalibration():
    """Test strategy recalibration"""
    metrics = StrategyMetrics("test_strategy")
    
    # Add enough trades to trigger recalibration
    for i in range(25):
        won = i % 2 == 0  # Alternate wins/losses
        trade = TradeResult(
            strategy_name="test_strategy",
            instrument="EURUSD",
            direction="CALL",
            amount=1.0,
            entry_time=datetime.now(),
            profit=1.0 if won else -1.0,
            won=won,
            payout_ratio=0.8,
            confidence=0.75
        )
        metrics.update(trade)
    
    # Test recalibration
    assert metrics.should_recalibrate(min_trades=20, min_hours=0)
    
    original_multiplier = metrics.confidence_multiplier
    metrics.recalibrate()
    
    # Verify multiplier changed
    assert metrics.confidence_multiplier != original_multiplier

if __name__ == '__main__':
    pytest.main([__file__])