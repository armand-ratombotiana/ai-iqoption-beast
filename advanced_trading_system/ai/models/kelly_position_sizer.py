"""
Advanced Position Sizing with Kelly Criterion and AI
Mathematically optimal position sizing with risk management
"""
import numpy as np
from typing import Dict, Tuple, Optional


class KellyPositionSizer:
    """
    Advanced position sizing using:
    - Kelly Criterion for optimal bet sizing
    - Fractional Kelly for risk reduction
    - AI confidence-based adjustments
    - Regime-aware position scaling
    - Monte Carlo drawdown simulation
    """

    def __init__(self, config: Dict):
        self.config = config
        self.kelly_fraction = 0.25  # Use 25% of full Kelly (safer)
        self.max_position_pct = 0.05  # Max 5% of balance per trade
        self.win_rate_estimate = 0.55  # Initial estimate
        self.avg_win_loss_ratio = 1.8  # Payout ratio for binary options

    def calculate_position(
        self,
        confidence: float,
        balance: float,
        ai_consensus: Dict,
        regime_info: Dict = None,
        historical_performance: Dict = None
    ) -> Dict:
        """
        Calculate optimal position size

        Returns:
        {
            'amount': float,
            'kelly_percentage': float,
            'risk_percentage': float,
            'reasoning': str,
            'expected_value': float,
            'max_drawdown_risk': float
        }
        """
        # Step 1: Calculate base Kelly Criterion size
        kelly_size = self._kelly_criterion(
            confidence, historical_performance
        )

        # Step 2: Apply fractional Kelly for safety
        fractional_kelly = kelly_size * self.kelly_fraction

        # Step 3: Adjust for market regime
        if regime_info:
            regime_adjusted = self._regime_adjustment(
                fractional_kelly, regime_info
            )
        else:
            regime_adjusted = fractional_kelly

        # Step 4: Adjust for AI consensus quality
        if ai_consensus:
            consensus_adjusted = self._consensus_adjustment(
                regime_adjusted, ai_consensus
            )
        else:
            consensus_adjusted = regime_adjusted

        # Step 5: Calculate dollar amount
        position_amount = balance * consensus_adjusted

        # Step 6: Apply hard limits
        min_amount = self.config.get('MIN_AMOUNT', 1.0)
        max_amount = min(
            balance * self.max_position_pct,
            self.config.get('MAX_AMOUNT', 20.0)
        )

        position_amount = max(min_amount, min(position_amount, max_amount))

        # Step 7: Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(
            position_amount, balance, confidence
        )

        # Step 8: Build reasoning
        reasoning = self._build_reasoning(
            kelly_size, fractional_kelly, regime_adjusted,
            consensus_adjusted, position_amount, balance
        )

        return {
            'amount': round(position_amount, 2),
            'kelly_percentage': round(kelly_size * 100, 2),
            'fractional_kelly_percentage': round(fractional_kelly * 100, 2),
            'final_percentage': round(consensus_adjusted * 100, 2),
            'risk_percentage': round((position_amount / balance) * 100, 2),
            'reasoning': reasoning,
            'expected_value': risk_metrics['expected_value'],
            'max_drawdown_risk': risk_metrics['max_drawdown_risk'],
            'sharpe_estimate': risk_metrics['sharpe_estimate']
        }

    def _kelly_criterion(
        self,
        confidence: float,
        historical_performance: Dict = None
    ) -> float:
        """
        Calculate Kelly Criterion percentage

        Kelly% = (bp - q) / b
        where:
        - b = odds received on the bet (payout ratio)
        - p = probability of winning (win rate)
        - q = probability of losing (1 - p)

        For binary options with 80% payout:
        - Win: +80% of stake
        - Loss: -100% of stake
        - b = 0.8
        """
        # Use historical win rate if available
        if historical_performance:
            win_rate = historical_performance.get('win_rate', 0.55)
        else:
            # Use confidence as proxy for win probability
            # But be conservative: 80% confidence → 60% win rate
            win_rate = 0.4 + (confidence / 100 * 0.3)

        loss_rate = 1 - win_rate
        payout_ratio = self.avg_win_loss_ratio

        # Kelly formula
        kelly_pct = (payout_ratio * win_rate - loss_rate) / payout_ratio

        # Clamp to reasonable range
        kelly_pct = max(0.01, min(kelly_pct, 0.3))  # 1% to 30%

        return kelly_pct

    def _regime_adjustment(self, kelly_size: float, regime_info: Dict) -> float:
        """
        Adjust position size based on market regime
        """
        regime = regime_info.get('regime', 'sideways')
        risk_level = regime_info.get('risk_level', 'MEDIUM')
        confidence = regime_info.get('confidence', 50)

        adjustment_factor = 1.0

        # Regime-based adjustment
        if regime == 'bull' or regime == 'bear':
            if confidence > 70:
                adjustment_factor *= 1.1  # Increase in strong trends
            else:
                adjustment_factor *= 0.95
        elif regime == 'high_volatility':
            adjustment_factor *= 0.6  # Significantly reduce in volatile markets
        elif regime == 'low_volatility':
            adjustment_factor *= 1.05  # Slightly increase in calm markets
        else:  # sideways
            adjustment_factor *= 0.85  # Reduce in ranging markets

        # Risk level adjustment
        risk_adjustments = {
            'LOW': 1.1,
            'MEDIUM': 1.0,
            'HIGH': 0.7
        }
        adjustment_factor *= risk_adjustments.get(risk_level, 1.0)

        return kelly_size * adjustment_factor

    def _consensus_adjustment(self, kelly_size: float, consensus: Dict) -> float:
        """
        Adjust based on AI consensus quality
        """
        agreement = consensus.get('agreement', 50) / 100
        uncertainty = consensus.get('uncertainty', 30) / 100
        consensus_reached = consensus.get('consensus_reached', False)

        adjustment_factor = 1.0

        # Agreement bonus/penalty
        if agreement > 0.8:
            adjustment_factor *= 1.15  # Strong agreement
        elif agreement < 0.6:
            adjustment_factor *= 0.8  # Weak agreement

        # Uncertainty penalty
        adjustment_factor *= (1 - uncertainty * 0.3)

        # Consensus threshold
        if not consensus_reached:
            adjustment_factor *= 0.7  # Significantly reduce if no consensus

        return kelly_size * adjustment_factor

    def _calculate_risk_metrics(
        self,
        position_amount: float,
        balance: float,
        confidence: float
    ) -> Dict:
        """
        Calculate risk metrics for the position

        Returns:
        - Expected Value (EV)
        - Max Drawdown Risk
        - Estimated Sharpe Ratio
        """
        # Probability estimates
        win_prob = 0.4 + (confidence / 100 * 0.3)  # Conservative
        loss_prob = 1 - win_prob

        # Expected value
        win_payout = position_amount * self.avg_win_loss_ratio
        loss_amount = position_amount
        expected_value = (win_prob * win_payout) - (loss_prob * loss_amount)

        # Max drawdown risk (Monte Carlo simulation - simplified)
        # Simulate 10 consecutive losses (worst case)
        max_consecutive_losses = 10
        total_loss = 0
        current_balance = balance

        for i in range(max_consecutive_losses):
            loss = min(position_amount, current_balance)
            total_loss += loss
            current_balance -= loss
            if current_balance < position_amount:
                break

        max_drawdown_risk = (total_loss / balance) * 100

        # Estimated Sharpe Ratio
        # Sharpe = (Expected Return - Risk Free Rate) / Std Dev
        expected_return = expected_value / position_amount
        std_dev = np.sqrt(win_prob * (1 - win_prob))  # Simplified
        sharpe_estimate = expected_return / std_dev if std_dev > 0 else 0

        return {
            'expected_value': round(expected_value, 2),
            'max_drawdown_risk': round(max_drawdown_risk, 2),
            'sharpe_estimate': round(sharpe_estimate, 2)
        }

    def _build_reasoning(
        self,
        kelly: float,
        fractional: float,
        regime_adj: float,
        consensus_adj: float,
        final_amount: float,
        balance: float
    ) -> str:
        """Build human-readable reasoning for position size"""
        parts = []

        parts.append(f"Kelly: {kelly*100:.1f}%")
        parts.append(f"Fractional Kelly (25%): {fractional*100:.1f}%")

        if regime_adj != fractional:
            change = ((regime_adj - fractional) / fractional) * 100
            parts.append(f"Regime Adj: {change:+.0f}%")

        if consensus_adj != regime_adj:
            change = ((consensus_adj - regime_adj) / regime_adj) * 100
            parts.append(f"Consensus Adj: {change:+.0f}%")

        final_pct = (final_amount / balance) * 100
        parts.append(f"Final: ${final_amount:.2f} ({final_pct:.1f}% of balance)")

        return " → ".join(parts)

    def update_performance(self, win_rate: float, avg_payout: float):
        """
        Update position sizer with actual performance data

        This enables the Kelly Criterion to adapt to real results
        """
        # Exponential moving average
        alpha = 0.1  # Learning rate
        self.win_rate_estimate = (
            alpha * win_rate + (1 - alpha) * self.win_rate_estimate
        )
        self.avg_win_loss_ratio = (
            alpha * avg_payout + (1 - alpha) * self.avg_win_loss_ratio
        )

        print(f"📊 Kelly updated: Win Rate={self.win_rate_estimate:.2%}, "
              f"Payout Ratio={self.avg_win_loss_ratio:.2f}")

    def simulate_drawdown(
        self,
        starting_balance: float,
        position_size: float,
        num_trades: int = 1000,
        win_rate: float = 0.55
    ) -> Dict:
        """
        Monte Carlo simulation for drawdown analysis

        Returns:
        {
            'max_drawdown': float,
            'avg_drawdown': float,
            'win_rate_realized': float,
            'final_balance': float,
            'sharpe_ratio': float
        }
        """
        balance = starting_balance
        max_balance = starting_balance
        max_drawdown = 0
        drawdowns = []
        returns = []

        for i in range(num_trades):
            # Simulate win/loss
            win = np.random.random() < win_rate

            if win:
                profit = position_size * self.avg_win_loss_ratio
                balance += profit
                returns.append(profit / balance)
            else:
                loss = min(position_size, balance)
                balance -= loss
                returns.append(-loss / balance)

            # Track drawdown
            if balance > max_balance:
                max_balance = balance

            current_drawdown = (max_balance - balance) / max_balance * 100
            drawdowns.append(current_drawdown)

            if current_drawdown > max_drawdown:
                max_drawdown = current_drawdown

            # Stop if bankrupt
            if balance <= 0:
                break

        # Calculate Sharpe ratio
        if returns:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe = 0

        return {
            'max_drawdown': round(max_drawdown, 2),
            'avg_drawdown': round(np.mean(drawdowns), 2),
            'final_balance': round(balance, 2),
            'profit_loss': round(balance - starting_balance, 2),
            'sharpe_ratio': round(sharpe, 2),
            'total_trades': num_trades
        }
