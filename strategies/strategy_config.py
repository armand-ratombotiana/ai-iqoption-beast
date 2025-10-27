"""
Strategy Configuration for Real Money Trading

This module defines configuration for different trading strategies
optimized for $100 real money trading with strict risk management.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class StrategyConfig:
    """Configuration for strategy engine"""

    # Strategy selection
    enabled_strategies: List[str] = None  # None = all strategies
    min_confidence: float = 0.75  # Minimum confidence to trade (0.0-1.0)
    min_confluence: int = 2  # Minimum number of strategies that must agree

    # Candle requirements
    min_candles_required: int = 50  # Minimum candles for analysis
    candle_size: int = 60  # Candle size in seconds

    # Risk management
    max_trade_amount: float = 2.0  # Maximum per trade ($2 for $100 account)
    min_trade_amount: float = 1.0  # Minimum per trade
    max_daily_loss: float = 10.0  # Max daily loss before stopping
    max_concurrent_trades: int = 2  # Max simultaneous trades

    # Performance filters
    min_payout_ratio: float = 0.75  # Minimum 75% payout
    min_expiration_seconds: int = 40  # Minimum expiration time
    max_expiration_seconds: int = 55  # Maximum expiration time

    def __post_init__(self):
        if self.enabled_strategies is None:
            self.enabled_strategies = [
                'enhanced_candle_count',
                'rsi_divergence',
                'macd_momentum',
                'bollinger_rsi_combo',
                'stochastic',
                'trend_alignment',
                'support_resistance'
            ]


# Preset configurations for different risk profiles
CONSERVATIVE_CONFIG = StrategyConfig(
    min_confidence=0.85,
    min_confluence=3,
    max_trade_amount=1.5,
    max_daily_loss=5.0,
    max_concurrent_trades=1
)

MODERATE_CONFIG = StrategyConfig(
    min_confidence=0.78,  # Increased from 0.75 for better quality signals
    min_confluence=2,
    max_trade_amount=2.0,
    max_daily_loss=8.0,  # Reduced from 10.0 to be more protective of $100 account
    max_concurrent_trades=2
)

AGGRESSIVE_CONFIG = StrategyConfig(
    min_confidence=0.70,
    min_confluence=2,
    max_trade_amount=3.0,
    max_daily_loss=15.0,
    max_concurrent_trades=3
)

# Default configuration for $100 real money trading
DEFAULT_REAL_MONEY_CONFIG = MODERATE_CONFIG


def get_config(profile: str = 'moderate') -> StrategyConfig:
    """
    Get strategy configuration by profile name

    Args:
        profile: One of 'conservative', 'moderate', 'aggressive'

    Returns:
        StrategyConfig instance
    """
    profiles = {
        'conservative': CONSERVATIVE_CONFIG,
        'moderate': MODERATE_CONFIG,
        'aggressive': AGGRESSIVE_CONFIG
    }

    return profiles.get(profile.lower(), MODERATE_CONFIG)
