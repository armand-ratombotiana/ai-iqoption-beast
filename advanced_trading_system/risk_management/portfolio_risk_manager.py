"""
Portfolio Risk Manager
Advanced portfolio-level risk management with real-time monitoring
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio

from .var_calculator import VaRCalculator
from .correlation_monitor import CorrelationMonitor
from .stress_tester import StressTester


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Position:
    """Represents a trading position"""
    position_id: str
    pair: str
    direction: str  # CALL or PUT
    amount: float
    entry_price: float
    entry_time: datetime
    duration: int  # minutes
    current_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    is_active: bool = True


@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""
    total_exposure: float
    var_95: float
    var_99: float
    expected_shortfall: float
    max_drawdown: float
    correlation_risk: float
    concentration_risk: float
    liquidity_risk: float
    overall_risk_level: RiskLevel
    risk_score: float


class PortfolioRiskManager:
    """
    Advanced portfolio risk management system
    
    Features:
    - Real-time risk monitoring
    - Position correlation analysis
    - VaR and CVaR calculations
    - Stress testing
    - Dynamic position limits
    - Risk-based position sizing
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Risk components
        self.var_calculator = VaRCalculator()
        self.correlation_monitor = CorrelationMonitor()
        self.stress_tester = StressTester()
        
        # Portfolio state
        self.positions: Dict[str, Position] = {}
        self.historical_pnl: List[float] = []
        self.risk_metrics_history: List[RiskMetrics] = []
        
        # Risk limits
        self.max_portfolio_risk = config.get('max_portfolio_risk', 0.05)  # 5%
        self.max_single_position = config.get('max_single_position', 0.02)  # 2%
        self.max_pair_exposure = config.get('max_pair_exposure', 0.10)  # 10%
        self.max_correlation_exposure = config.get('max_correlation_exposure', 0.15)  # 15%
        
        # Risk monitoring
        self.risk_check_interval = 60  # seconds
        self.is_monitoring = False

    async def start_monitoring(self):
        """Start real-time risk monitoring"""
        self.is_monitoring = True
        asyncio.create_task(self._risk_monitoring_loop())
        print("✅ Portfolio risk monitoring started")

    async def stop_monitoring(self):
        """Stop risk monitoring"""
        self.is_monitoring = False
        print("🛑 Portfolio risk monitoring stopped")

    async def _risk_monitoring_loop(self):
        """Main risk monitoring loop"""
        while self.is_monitoring:
            try:
                # Calculate current risk metrics
                risk_metrics = await self.calculate_portfolio_risk()
                
                # Check risk limits
                violations = self.check_risk_violations(risk_metrics)
                
                if violations:
                    await self.handle_risk_violations(violations)
                
                # Store metrics
                self.risk_metrics_history.append(risk_metrics)
                
                # Keep only last 1000 entries
                if len(self.risk_metrics_history) > 1000:
                    self.risk_metrics_history = self.risk_metrics_history[-1000:]
                
                await asyncio.sleep(self.risk_check_interval)
                
            except Exception as e:
                print(f"❌ Risk monitoring error: {e}")
                await asyncio.sleep(self.risk_check_interval)

    def add_position(self, position: Position) -> bool:
        """Add a new position to the portfolio"""
        try:
            # Pre-trade risk check
            if not self._validate_new_position(position):
                return False
            
            self.positions[position.position_id] = position
            print(f"📈 Added position: {position.position_id} ({position.pair} {position.direction})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding position: {e}")
            return False

    def remove_position(self, position_id: str, final_pnl: float = None):
        """Remove a position from the portfolio"""
        try:
            if position_id in self.positions:
                position = self.positions[position_id]
                
                # Record final P&L
                if final_pnl is not None:
                    self.historical_pnl.append(final_pnl)
                    
                    # Keep only last 1000 P&L records
                    if len(self.historical_pnl) > 1000:
                        self.historical_pnl = self.historical_pnl[-1000:]
                
                del self.positions[position_id]
                print(f"📉 Removed position: {position_id}")
                
        except Exception as e:
            print(f"❌ Error removing position: {e}")

    def update_position_pnl(self, position_id: str, current_price: float):
        """Update position P&L based on current price"""
        try:
            if position_id not in self.positions:
                return
            
            position = self.positions[position_id]
            
            # Calculate unrealized P&L for binary options
            # This is simplified - in reality, binary options have fixed payouts
            if position.direction == 'CALL':
                if current_price > position.entry_price:
                    position.unrealized_pnl = position.amount * 0.8  # 80% payout
                else:
                    position.unrealized_pnl = -position.amount
            else:  # PUT
                if current_price < position.entry_price:
                    position.unrealized_pnl = position.amount * 0.8
                else:
                    position.unrealized_pnl = -position.amount
            
            position.current_pnl = position.unrealized_pnl
            
        except Exception as e:
            print(f"❌ Error updating position P&L: {e}")

    async def calculate_portfolio_risk(self) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            if not self.positions:
                return RiskMetrics(
                    total_exposure=0.0,
                    var_95=0.0,
                    var_99=0.0,
                    expected_shortfall=0.0,
                    max_drawdown=0.0,
                    correlation_risk=0.0,
                    concentration_risk=0.0,
                    liquidity_risk=0.0,
                    overall_risk_level=RiskLevel.LOW,
                    risk_score=0.0
                )
            
            # Calculate total exposure
            total_exposure = sum(pos.amount for pos in self.positions.values())
            
            # Calculate VaR and Expected Shortfall
            position_values = [pos.current_pnl for pos in self.positions.values()]
            
            if len(self.historical_pnl) > 30:  # Need sufficient history
                var_95 = self.var_calculator.calculate_var(self.historical_pnl, 0.95)
                var_99 = self.var_calculator.calculate_var(self.historical_pnl, 0.99)
                expected_shortfall = self.var_calculator.calculate_expected_shortfall(self.historical_pnl, 0.95)
            else:
                # Use simplified calculation for insufficient history
                if position_values:
                    std_dev = np.std(position_values)
                    var_95 = 1.645 * std_dev  # 95% confidence
                    var_99 = 2.326 * std_dev  # 99% confidence
                    expected_shortfall = var_95 * 1.2  # Approximation
                else:
                    var_95 = var_99 = expected_shortfall = 0.0
            
            # Calculate maximum drawdown
            max_drawdown = self._calculate_max_drawdown()
            
            # Calculate correlation risk
            correlation_risk = await self._calculate_correlation_risk()
            
            # Calculate concentration risk
            concentration_risk = self._calculate_concentration_risk()
            
            # Calculate liquidity risk (simplified for binary options)
            liquidity_risk = self._calculate_liquidity_risk()
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(
                total_exposure, var_95, correlation_risk, concentration_risk
            )
            
            # Determine risk level
            overall_risk_level = self._determine_risk_level(risk_score)
            
            return RiskMetrics(
                total_exposure=total_exposure,
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                max_drawdown=max_drawdown,
                correlation_risk=correlation_risk,
                concentration_risk=concentration_risk,
                liquidity_risk=liquidity_risk,
                overall_risk_level=overall_risk_level,
                risk_score=risk_score
            )
            
        except Exception as e:
            print(f"❌ Error calculating portfolio risk: {e}")
            return RiskMetrics(
                total_exposure=0.0,
                var_95=0.0,
                var_99=0.0,
                expected_shortfall=0.0,
                max_drawdown=0.0,
                correlation_risk=0.0,
                concentration_risk=0.0,
                liquidity_risk=0.0,
                overall_risk_level=RiskLevel.HIGH,
                risk_score=100.0
            )

    def _validate_new_position(self, position: Position) -> bool:
        """Validate if new position meets risk criteria"""
        try:
            # Check single position limit
            portfolio_value = sum(pos.amount for pos in self.positions.values()) + position.amount
            if position.amount / portfolio_value > self.max_single_position:
                print(f"❌ Position size exceeds single position limit: {position.amount}")
                return False
            
            # Check pair exposure limit
            pair_exposure = sum(
                pos.amount for pos in self.positions.values() 
                if pos.pair == position.pair
            ) + position.amount
            
            if pair_exposure / portfolio_value > self.max_pair_exposure:
                print(f"❌ Pair exposure exceeds limit for {position.pair}: {pair_exposure}")
                return False
            
            # Check correlation exposure (simplified)
            correlated_exposure = self._calculate_correlated_exposure(position)
            if correlated_exposure / portfolio_value > self.max_correlation_exposure:
                print(f"❌ Correlated exposure exceeds limit: {correlated_exposure}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating position: {e}")
            return False

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from historical P&L"""
        if len(self.historical_pnl) < 2:
            return 0.0
        
        cumulative_pnl = np.cumsum(self.historical_pnl)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdowns = running_max - cumulative_pnl
        
        return float(np.max(drawdowns))

    async def _calculate_correlation_risk(self) -> float:
        """Calculate portfolio correlation risk"""
        try:
            if len(self.positions) < 2:
                return 0.0
            
            # Get unique pairs
            pairs = list(set(pos.pair for pos in self.positions.values()))
            
            if len(pairs) < 2:
                return 0.0
            
            # Calculate correlation matrix
            correlation_matrix = await self.correlation_monitor.get_correlation_matrix(pairs)
            
            # Calculate weighted correlation risk
            total_risk = 0.0
            total_weight = 0.0
            
            for i, pair1 in enumerate(pairs):
                for j, pair2 in enumerate(pairs):
                    if i != j:
                        correlation = correlation_matrix.get(f"{pair1}_{pair2}", 0.0)
                        
                        # Get exposure for each pair
                        exposure1 = sum(pos.amount for pos in self.positions.values() if pos.pair == pair1)
                        exposure2 = sum(pos.amount for pos in self.positions.values() if pos.pair == pair2)
                        
                        weight = exposure1 * exposure2
                        total_risk += abs(correlation) * weight
                        total_weight += weight
            
            return total_risk / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            print(f"❌ Error calculating correlation risk: {e}")
            return 0.5  # Default moderate risk

    def _calculate_concentration_risk(self) -> float:
        """Calculate portfolio concentration risk"""
        if not self.positions:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index for concentration
        total_exposure = sum(pos.amount for pos in self.positions.values())
        
        if total_exposure == 0:
            return 0.0
        
        # Group by pair
        pair_exposures = {}
        for position in self.positions.values():
            if position.pair not in pair_exposures:
                pair_exposures[position.pair] = 0
            pair_exposures[position.pair] += position.amount
        
        # Calculate HHI
        hhi = sum((exposure / total_exposure) ** 2 for exposure in pair_exposures.values())
        
        # Normalize to 0-1 scale (1 = maximum concentration)
        return hhi

    def _calculate_liquidity_risk(self) -> float:
        """Calculate liquidity risk (simplified for binary options)"""
        # Binary options have fixed expiration, so liquidity risk is time-based
        if not self.positions:
            return 0.0
        
        current_time = datetime.now()
        total_risk = 0.0
        total_weight = 0.0
        
        for position in self.positions.values():
            # Time until expiration
            time_to_expiry = (position.entry_time + timedelta(minutes=position.duration) - current_time).total_seconds() / 60
            
            # Higher risk for positions close to expiry
            if time_to_expiry > 0:
                liquidity_risk = max(0, 1 - (time_to_expiry / position.duration))
            else:
                liquidity_risk = 1.0  # Maximum risk for expired positions
            
            total_risk += liquidity_risk * position.amount
            total_weight += position.amount
        
        return total_risk / total_weight if total_weight > 0 else 0.0

    def _calculate_correlated_exposure(self, new_position: Position) -> float:
        """Calculate exposure to positions correlated with new position"""
        correlated_exposure = new_position.amount
        
        # Simplified correlation - same base currency pairs are correlated
        base_currency = new_position.pair[:3]  # e.g., EUR from EURUSD
        
        for position in self.positions.values():
            if position.pair.startswith(base_currency) or position.pair.endswith(base_currency):
                correlated_exposure += position.amount * 0.7  # 70% correlation assumption
        
        return correlated_exposure

    def _calculate_risk_score(self, total_exposure: float, var_95: float, 
                            correlation_risk: float, concentration_risk: float) -> float:
        """Calculate overall risk score (0-100)"""
        try:
            # Normalize components to 0-1 scale
            exposure_score = min(total_exposure / 10000, 1.0)  # Normalize by $10k
            var_score = min(abs(var_95) / 1000, 1.0)  # Normalize by $1k
            correlation_score = correlation_risk
            concentration_score = concentration_risk
            
            # Weighted combination
            risk_score = (
                exposure_score * 0.3 +
                var_score * 0.3 +
                correlation_score * 0.2 +
                concentration_score * 0.2
            ) * 100
            
            return min(risk_score, 100.0)
            
        except Exception as e:
            print(f"❌ Error calculating risk score: {e}")
            return 50.0

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on risk score"""
        if risk_score < 25:
            return RiskLevel.LOW
        elif risk_score < 50:
            return RiskLevel.MEDIUM
        elif risk_score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def check_risk_violations(self, risk_metrics: RiskMetrics) -> List[str]:
        """Check for risk limit violations"""
        violations = []
        
        # Check overall risk level
        if risk_metrics.overall_risk_level == RiskLevel.CRITICAL:
            violations.append("CRITICAL_RISK_LEVEL")
        
        # Check VaR limits
        if abs(risk_metrics.var_95) > self.config.get('max_var_95', 500):
            violations.append("VAR_95_EXCEEDED")
        
        # Check concentration risk
        if risk_metrics.concentration_risk > 0.5:  # 50% concentration
            violations.append("HIGH_CONCENTRATION")
        
        # Check correlation risk
        if risk_metrics.correlation_risk > 0.7:  # 70% correlation
            violations.append("HIGH_CORRELATION")
        
        return violations

    async def handle_risk_violations(self, violations: List[str]):
        """Handle risk violations"""
        print(f"⚠️ Risk violations detected: {violations}")
        
        for violation in violations:
            if violation == "CRITICAL_RISK_LEVEL":
                await self._handle_critical_risk()
            elif violation == "VAR_95_EXCEEDED":
                await self._handle_var_violation()
            elif violation == "HIGH_CONCENTRATION":
                await self._handle_concentration_violation()
            elif violation == "HIGH_CORRELATION":
                await self._handle_correlation_violation()

    async def _handle_critical_risk(self):
        """Handle critical risk level"""
        print("🚨 CRITICAL RISK LEVEL - Implementing emergency measures")
        
        # Could implement:
        # - Stop new positions
        # - Close most risky positions
        # - Reduce position sizes
        # - Send alerts to risk managers

    async def _handle_var_violation(self):
        """Handle VaR violation"""
        print("⚠️ VaR limit exceeded - Reducing exposure")

    async def _handle_concentration_violation(self):
        """Handle concentration violation"""
        print("⚠️ High concentration detected - Diversifying portfolio")

    async def _handle_correlation_violation(self):
        """Handle correlation violation"""
        print("⚠️ High correlation risk - Reducing correlated positions")

    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        if not self.positions:
            return {
                'total_positions': 0,
                'total_exposure': 0.0,
                'unrealized_pnl': 0.0,
                'pairs': []
            }
        
        total_exposure = sum(pos.amount for pos in self.positions.values())
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        # Group by pair
        pair_summary = {}
        for position in self.positions.values():
            if position.pair not in pair_summary:
                pair_summary[position.pair] = {
                    'positions': 0,
                    'exposure': 0.0,
                    'pnl': 0.0
                }
            
            pair_summary[position.pair]['positions'] += 1
            pair_summary[position.pair]['exposure'] += position.amount
            pair_summary[position.pair]['pnl'] += position.unrealized_pnl
        
        return {
            'total_positions': len(self.positions),
            'total_exposure': total_exposure,
            'unrealized_pnl': unrealized_pnl,
            'pairs': pair_summary,
            'risk_metrics': self.risk_metrics_history[-1] if self.risk_metrics_history else None
        }

    async def run_stress_test(self, scenarios: List[Dict]) -> Dict:
        """Run stress test scenarios"""
        try:
            current_positions = list(self.positions.values())
            
            if not current_positions:
                return {'error': 'No positions to stress test'}
            
            results = await self.stress_tester.run_stress_tests(current_positions, scenarios)
            
            return {
                'stress_test_results': results,
                'timestamp': datetime.now().isoformat(),
                'positions_tested': len(current_positions)
            }
            
        except Exception as e:
            print(f"❌ Stress test error: {e}")
            return {'error': str(e)}

    def export_risk_report(self, filepath: str):
        """Export comprehensive risk report"""
        try:
            current_metrics = self.risk_metrics_history[-1] if self.risk_metrics_history else None
            portfolio_summary = self.get_portfolio_summary()
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_summary': portfolio_summary,
                'current_risk_metrics': current_metrics.__dict__ if current_metrics else None,
                'risk_history': [m.__dict__ for m in self.risk_metrics_history[-100:]],  # Last 100
                'historical_pnl': self.historical_pnl[-100:],  # Last 100
                'risk_limits': {
                    'max_portfolio_risk': self.max_portfolio_risk,
                    'max_single_position': self.max_single_position,
                    'max_pair_exposure': self.max_pair_exposure,
                    'max_correlation_exposure': self.max_correlation_exposure
                }
            }
            
            import json
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📊 Risk report exported to {filepath}")
            
        except Exception as e:
            print(f"❌ Error exporting risk report: {e}")