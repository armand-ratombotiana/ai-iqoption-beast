"""
Market Regime Detection using Hidden Markov Models
Identifies: Bull, Bear, Sideways, High-Vol, Low-Vol regimes
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class MarketRegimeDetector:
    """
    Detects market regimes using statistical analysis
    and Hidden Markov Model principles
    """

    def __init__(self):
        self.regimes = {
            'bull': 'Bull Market',
            'bear': 'Bear Market',
            'sideways': 'Sideways/Ranging',
            'high_volatility': 'High Volatility',
            'low_volatility': 'Low Volatility'
        }

        self.regime_history = []
        self.regime_transitions = {}

    def detect_regime(self, market_data: Dict, candles: List[Dict] = None) -> Dict:
        """
        Detect current market regime

        Returns:
        {
            'regime': str,
            'confidence': float,
            'characteristics': dict,
            'recommended_strategy': str,
            'risk_level': str
        }
        """
        # Extract indicators
        trend = market_data.get('trend', 'neutral')
        volatility = market_data.get('volatility', 'medium')
        volatility_value = market_data.get('volatility_value', 0)
        adx = market_data.get('adx', 0)
        rsi_14 = market_data.get('rsi_14', 50)
        atr = market_data.get('atr', 0)

        # Calculate additional metrics
        regime_scores = {
            'bull': 0,
            'bear': 0,
            'sideways': 0,
            'high_volatility': 0,
            'low_volatility': 0
        }

        # Bull market indicators
        if trend == 'uptrend':
            regime_scores['bull'] += 30
        if rsi_14 > 50:
            regime_scores['bull'] += 15
        if adx > 25 and trend == 'uptrend':
            regime_scores['bull'] += 20

        # Bear market indicators
        if trend == 'downtrend':
            regime_scores['bear'] += 30
        if rsi_14 < 50:
            regime_scores['bear'] += 15
        if adx > 25 and trend == 'downtrend':
            regime_scores['bear'] += 20

        # Sideways market indicators
        if trend == 'sideways':
            regime_scores['sideways'] += 40
        if adx < 20:
            regime_scores['sideways'] += 25
        if 45 < rsi_14 < 55:
            regime_scores['sideways'] += 15

        # Volatility regimes
        if volatility == 'high' or volatility_value > 1.5:
            regime_scores['high_volatility'] += 50
        elif volatility == 'low' or volatility_value < 0.5:
            regime_scores['low_volatility'] += 50
        else:
            regime_scores['high_volatility'] += 20
            regime_scores['low_volatility'] += 20

        # Determine primary regime
        primary_regime = max(regime_scores, key=regime_scores.get)
        confidence = regime_scores[primary_regime]

        # Analyze candles for momentum
        if candles and len(candles) >= 20:
            momentum_regime = self._analyze_momentum(candles)
            if momentum_regime:
                regime_scores[momentum_regime] += 15

        # Re-evaluate after momentum
        primary_regime = max(regime_scores, key=regime_scores.get)
        confidence = min(regime_scores[primary_regime], 95)

        # Get regime characteristics
        characteristics = self._get_regime_characteristics(
            primary_regime, market_data, confidence
        )

        # Recommended strategy based on regime
        strategy = self._get_regime_strategy(primary_regime, volatility)

        # Risk level
        risk_level = self._calculate_risk_level(primary_regime, volatility, adx)

        # Store history
        self.regime_history.append({
            'timestamp': datetime.now().isoformat(),
            'regime': primary_regime,
            'confidence': confidence
        })

        # Keep only last 100 regimes
        if len(self.regime_history) > 100:
            self.regime_history = self.regime_history[-100:]

        return {
            'regime': primary_regime,
            'regime_name': self.regimes[primary_regime],
            'confidence': round(confidence, 1),
            'characteristics': characteristics,
            'recommended_strategy': strategy,
            'risk_level': risk_level,
            'regime_scores': regime_scores,
            'regime_stability': self._calculate_regime_stability()
        }

    def _analyze_momentum(self, candles: List[Dict]) -> Optional[str]:
        """Analyze price momentum from candle data"""
        if len(candles) < 20:
            return None

        recent_closes = [c['close'] for c in candles[-20:]]

        # Calculate returns
        returns = []
        for i in range(1, len(recent_closes)):
            returns.append((recent_closes[i] - recent_closes[i-1]) / recent_closes[i-1])

        avg_return = np.mean(returns)
        std_return = np.std(returns)

        # Momentum-based regime
        if avg_return > std_return * 0.5:
            return 'bull'
        elif avg_return < -std_return * 0.5:
            return 'bear'
        elif std_return > np.mean(np.abs(returns)) * 2:
            return 'high_volatility'
        else:
            return 'sideways'

    def _get_regime_characteristics(self, regime: str, market_data: Dict,
                                     confidence: float) -> Dict:
        """Get detailed characteristics of the regime"""
        characteristics = {
            'trend_direction': market_data.get('trend', 'unknown'),
            'volatility_level': market_data.get('volatility', 'unknown'),
            'trend_strength': market_data.get('adx', 0),
            'confidence': confidence
        }

        if regime == 'bull':
            characteristics.update({
                'description': 'Strong upward momentum with higher highs',
                'typical_duration': '3-7 days',
                'reversal_signals': ['RSI > 70', 'MACD bearish divergence']
            })
        elif regime == 'bear':
            characteristics.update({
                'description': 'Strong downward momentum with lower lows',
                'typical_duration': '3-7 days',
                'reversal_signals': ['RSI < 30', 'MACD bullish divergence']
            })
        elif regime == 'sideways':
            characteristics.update({
                'description': 'Ranging market with weak directional bias',
                'typical_duration': '1-3 days',
                'breakout_signals': ['Volume spike', 'ADX > 25']
            })
        elif regime == 'high_volatility':
            characteristics.update({
                'description': 'Unstable price action with large swings',
                'typical_duration': 'Hours to 1 day',
                'stabilization_signals': ['ATR declining', 'Consolidation pattern']
            })
        else:  # low_volatility
            characteristics.update({
                'description': 'Stable price action with small movements',
                'typical_duration': '1-2 days',
                'expansion_signals': ['Volume increase', 'Narrowing Bollinger Bands']
            })

        return characteristics

    def _get_regime_strategy(self, regime: str, volatility: str) -> str:
        """Get recommended trading strategy for regime"""
        strategies = {
            'bull': 'Focus on CALL options, buy dips, follow trend',
            'bear': 'Focus on PUT options, sell rallies, follow trend',
            'sideways': 'Range trading: Buy support, Sell resistance',
            'high_volatility': 'Reduce position size, wider stops, wait for clarity',
            'low_volatility': 'Breakout strategy, increase size carefully'
        }

        base_strategy = strategies.get(regime, 'Neutral strategy')

        # Adjust for volatility
        if volatility == 'high' and regime not in ['high_volatility']:
            base_strategy += ' | CAUTION: High volatility detected'

        return base_strategy

    def _calculate_risk_level(self, regime: str, volatility: str, adx: float) -> str:
        """Calculate risk level for current regime"""
        risk_score = 0

        # Regime risk
        regime_risk = {
            'bull': 2,
            'bear': 2,
            'sideways': 3,
            'high_volatility': 5,
            'low_volatility': 1
        }
        risk_score += regime_risk.get(regime, 3)

        # Volatility risk
        vol_risk = {'low': 0, 'medium': 2, 'high': 4}
        risk_score += vol_risk.get(volatility, 2)

        # Trend strength risk (weak trends are risky)
        if adx < 20:
            risk_score += 2

        # Classify
        if risk_score <= 3:
            return 'LOW'
        elif risk_score <= 6:
            return 'MEDIUM'
        else:
            return 'HIGH'

    def _calculate_regime_stability(self) -> float:
        """
        Calculate how stable the current regime is
        (i.e., how often it changes)
        """
        if len(self.regime_history) < 5:
            return 0.5

        recent_regimes = [r['regime'] for r in self.regime_history[-10:]]

        # Calculate regime changes
        changes = 0
        for i in range(1, len(recent_regimes)):
            if recent_regimes[i] != recent_regimes[i-1]:
                changes += 1

        # Stability = 1 - (change_rate)
        stability = 1 - (changes / (len(recent_regimes) - 1))

        return round(stability, 2)

    def get_regime_transition_probability(self, from_regime: str,
                                           to_regime: str) -> float:
        """
        Calculate probability of transitioning from one regime to another
        (based on historical data)
        """
        if len(self.regime_history) < 20:
            return 0.2  # Default uniform probability

        transitions = []
        for i in range(1, len(self.regime_history)):
            prev = self.regime_history[i-1]['regime']
            curr = self.regime_history[i]['regime']
            transitions.append((prev, curr))

        # Count transitions
        total_from = sum(1 for t in transitions if t[0] == from_regime)
        matching_transitions = sum(
            1 for t in transitions if t[0] == from_regime and t[1] == to_regime
        )

        if total_from == 0:
            return 0.2

        return round(matching_transitions / total_from, 2)

    def get_optimal_trade_timing(self, regime: str) -> Dict:
        """
        Get optimal trade timing based on regime

        Returns when to trade, when to avoid, and position sizing hints
        """
        timing = {
            'bull': {
                'best_time': 'Buy dips when RSI < 50, trend still intact',
                'avoid': 'Avoid when RSI > 80, overbought',
                'position_sizing': 'Normal to slightly aggressive'
            },
            'bear': {
                'best_time': 'Sell rallies when RSI > 50, trend still intact',
                'avoid': 'Avoid when RSI < 20, oversold',
                'position_sizing': 'Normal to slightly aggressive'
            },
            'sideways': {
                'best_time': 'Trade at range boundaries (support/resistance)',
                'avoid': 'Avoid mid-range, unclear direction',
                'position_sizing': 'Reduced size, quick exits'
            },
            'high_volatility': {
                'best_time': 'Wait for volatility to subside',
                'avoid': 'Avoid during peak volatility spikes',
                'position_sizing': 'Significantly reduced (50% normal)'
            },
            'low_volatility': {
                'best_time': 'Position before breakout, on consolidation',
                'avoid': 'Avoid after prolonged low-vol period',
                'position_sizing': 'Normal, with tight stops'
            }
        }

        return timing.get(regime, {
            'best_time': 'Wait for clear signals',
            'avoid': 'Uncertain regime',
            'position_sizing': 'Minimal'
        })
