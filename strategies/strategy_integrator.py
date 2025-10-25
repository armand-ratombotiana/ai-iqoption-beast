"""
Strategy Integrator

Integrates the advanced strategy engine with the parallel trading bot.
Provides a simple interface compatible with the existing bot architecture.
"""

import logging
from typing import Dict, List, Tuple, Optional
from .advanced_strategies import AdvancedStrategyEngine, StrategySignal
from .strategy_config import StrategyConfig, DEFAULT_REAL_MONEY_CONFIG


class StrategyIntegrator:
    """
    Wrapper class to integrate advanced strategies with existing trading bot
    """

    def __init__(self, config: Optional[StrategyConfig] = None):
        """
        Initialize strategy integrator

        Args:
            config: Strategy configuration (uses default if None)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or DEFAULT_REAL_MONEY_CONFIG
        self.engine = AdvancedStrategyEngine()

        self.logger.info("=" * 80)
        self.logger.info("🎯 ADVANCED STRATEGY ENGINE INITIALIZED")
        self.logger.info("=" * 80)
        self.logger.info(f"Min Confidence: {self.config.min_confidence}")
        self.logger.info(f"Min Confluence: {self.config.min_confluence} strategies")
        self.logger.info(f"Enabled Strategies: {len(self.config.enabled_strategies)}")
        self.logger.info(f"Max Trade Amount: ${self.config.max_trade_amount}")
        self.logger.info(f"Max Daily Loss: ${self.config.max_daily_loss}")
        self.logger.info("=" * 80)

    def analyze_instrument(self, candles: List[Dict]) -> Tuple[str, float, List[Dict]]:
        """
        Analyze instrument and return trading signal

        Args:
            candles: List of candle dictionaries

        Returns:
            Tuple of (direction, confidence, breakdown)
            - direction: 'CALL', 'PUT', or 'NEUTRAL'
            - confidence: 0.0 to 1.0
            - breakdown: List of strategy results for logging

        Compatible with existing bot's expected return format
        """
        try:
            # Run analysis
            signal = self.engine.analyze(candles)

            # Check if signal meets minimum requirements
            if signal.direction == 'NEUTRAL':
                return ('NEUTRAL', 0.0, [])

            if signal.confidence < self.config.min_confidence:
                self.logger.debug(
                    f"Signal rejected: confidence {signal.confidence:.2f} "
                    f"< minimum {self.config.min_confidence:.2f}"
                )
                return ('NEUTRAL', 0.0, [])

            # Format breakdown for logging
            breakdown = [{
                'strategy': signal.strategy_name,
                'vote': signal.direction,
                'score': signal.confidence,
                'reasons': signal.reasons,
                'indicators': signal.indicators
            }]

            self.logger.info(f"✅ Signal: {signal.direction} @ {signal.confidence:.2f}")
            for reason in signal.reasons[:3]:  # Log top 3 reasons
                self.logger.info(f"   • {reason}")

            return (signal.direction, signal.confidence, breakdown)

        except Exception as e:
            self.logger.error(f"Error in strategy analysis: {e}", exc_info=True)
            return ('NEUTRAL', 0.0, [])

    def get_trade_amount(self, balance: float, win_streak: int = 0,
                        loss_streak: int = 0) -> float:
        """
        Calculate trade amount based on balance and performance

        Args:
            balance: Current account balance
            win_streak: Current winning streak
            loss_streak: Current losing streak

        Returns:
            Trade amount in dollars
        """
        # Base amount from config
        base_amount = self.config.min_trade_amount

        # Adjust based on balance (Kelly Criterion inspired but conservative)
        # For $100 account, start with $1-2 per trade
        if balance >= 100:
            base_amount = min(
                self.config.max_trade_amount,
                max(self.config.min_trade_amount, balance * 0.02)
            )

        # Reduce on losing streak (risk management)
        if loss_streak >= 2:
            base_amount *= 0.75  # Reduce by 25%
            self.logger.warning(f"⚠️ Reducing trade size due to {loss_streak} loss streak")

        elif loss_streak >= 4:
            base_amount *= 0.50  # Reduce by 50%
            self.logger.warning(f"⚠️ Further reducing trade size: {loss_streak} losses")

        # Slightly increase on win streak (but capped)
        if win_streak >= 3:
            base_amount *= 1.1  # Increase by 10%
            base_amount = min(base_amount, self.config.max_trade_amount)

        # Ensure within bounds
        final_amount = max(
            self.config.min_trade_amount,
            min(self.config.max_trade_amount, base_amount)
        )

        return round(final_amount, 2)

    def should_stop_trading(self, daily_pnl: float, balance: float) -> Tuple[bool, str]:
        """
        Check if trading should stop based on risk limits

        Args:
            daily_pnl: Today's profit/loss
            balance: Current balance

        Returns:
            Tuple of (should_stop, reason)
        """
        # Stop on daily loss limit
        if daily_pnl <= -self.config.max_daily_loss:
            return (True, f"Daily loss limit reached: ${daily_pnl:.2f}")

        # Stop if balance drops too low
        min_balance_threshold = 50.0  # Don't trade below $50
        if balance < min_balance_threshold:
            return (True, f"Balance too low: ${balance:.2f} < ${min_balance_threshold}")

        # Stop if balance is less than minimum trade amount
        if balance < self.config.min_trade_amount:
            return (True, f"Insufficient balance for minimum trade: ${balance:.2f}")

        return (False, "")

    def format_signal_log(self, instrument: str, signal: Tuple[str, float, List[Dict]]) -> str:
        """
        Format signal information for logging

        Args:
            instrument: Instrument name
            signal: Signal tuple from analyze_instrument

        Returns:
            Formatted log string
        """
        direction, confidence, breakdown = signal

        if direction == 'NEUTRAL':
            return f"[{instrument}] No signal"

        log_lines = [
            f"",
            f"{'=' * 80}",
            f"🎯 TRADE SIGNAL: {instrument}",
            f"{'=' * 80}",
            f"Direction: {direction}",
            f"Confidence: {confidence:.2%}",
        ]

        if breakdown:
            log_lines.append(f"Strategy: {breakdown[0]['strategy']}")
            log_lines.append(f"Reasons:")
            for reason in breakdown[0].get('reasons', [])[:5]:
                log_lines.append(f"  • {reason}")

        log_lines.append(f"{'=' * 80}")

        return "\n".join(log_lines)


def create_integrator(risk_profile: str = 'moderate') -> StrategyIntegrator:
    """
    Factory function to create strategy integrator

    Args:
        risk_profile: 'conservative', 'moderate', or 'aggressive'

    Returns:
        StrategyIntegrator instance
    """
    from .strategy_config import get_config

    config = get_config(risk_profile)
    return StrategyIntegrator(config)
