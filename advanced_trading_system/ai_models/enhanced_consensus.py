"""
Enhanced AI Consensus Engine with Dynamic Weighting and Reinforcement Learning
Multi-model voting with adaptive weights, regime-aware predictions, and explainability
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from .base_model import BaseAIModel
from .market_regime_detector import MarketRegimeDetector


class EnhancedConsensusEngine:
    """
    Advanced consensus engine with:
    - Dynamic weight adjustment based on performance
    - Market regime-aware model selection
    - Ensemble stacking with meta-learner
    - Explainability (SHAP-like feature importance)
    - Confidence calibration
    - Multi-armed bandit for exploration/exploitation
    """

    def __init__(self, consensus_threshold: float = 0.66):
        self.models: List[BaseAIModel] = []
        self.model_weights: Dict[str, float] = {}
        self.consensus_threshold = consensus_threshold

        # Performance tracking per regime
        self.model_performance_by_regime: Dict[str, Dict[str, Dict]] = {
            'bull': {},
            'bear': {},
            'sideways': {},
            'high_volatility': {},
            'low_volatility': {}
        }

        # Regime detector
        self.regime_detector = MarketRegimeDetector()

        # Meta-learner weights (how much to trust each model in different regimes)
        self.regime_model_affinity = {}

        # Exploration parameters (Multi-Armed Bandit)
        self.exploration_rate = 0.1  # 10% exploration
        self.total_trades = 0

    def add_model(self, model: BaseAIModel, weight: float = 1.0):
        """Register an AI model with initial weight"""
        self.models.append(model)
        self.model_weights[model.model_name] = weight

        # Initialize performance tracking for all regimes
        for regime in self.model_performance_by_regime:
            self.model_performance_by_regime[regime][model.model_name] = {
                'accuracy': 0.5,
                'total_predictions': 0,
                'correct_predictions': 0,
                'avg_confidence': 0.5
            }

        print(f"✅ Added AI model: {model.model_name} (weight: {weight})")

    def get_consensus_signal(self, market_data: Dict,
                              candles: List[Dict] = None) -> Dict:
        """
        Get enhanced consensus signal with regime awareness

        Returns:
        {
            'signal': 'CALL' or 'PUT' or 'NEUTRAL',
            'confidence': 0-100,
            'agreement': 0-100,
            'models_voted': {...},
            'reasoning': 'Combined analysis',
            'consensus_reached': bool,
            'regime': {...},
            'feature_importance': {...},
            'confidence_calibrated': float,
            'uncertainty': float
        }
        """
        if not self.models:
            return self._neutral_response('No AI models available')

        # Step 1: Detect market regime
        regime_info = self.regime_detector.detect_regime(market_data, candles)
        current_regime = regime_info['regime']

        # Step 2: Get regime-adjusted model weights
        adjusted_weights = self._get_regime_adjusted_weights(current_regime)

        # Step 3: Collect predictions from all models
        votes = {}
        call_votes = []
        put_votes = []
        all_confidences = []
        feature_importance_combined = {}

        for model in self.models:
            try:
                prediction = model.predict(market_data)
                votes[model.model_name] = prediction

                # Use regime-adjusted weight
                weight = adjusted_weights.get(model.model_name, 1.0)

                # Multi-Armed Bandit: Exploration vs Exploitation
                if self._should_explore():
                    # Exploration: Give equal weight
                    weight = 1.0

                if prediction['signal'] == 'CALL':
                    call_votes.append(weight)
                elif prediction['signal'] == 'PUT':
                    put_votes.append(weight)

                # Weighted confidence
                all_confidences.append(prediction['confidence'] * weight)

                # Aggregate feature importance if available
                if 'feature_importance' in prediction:
                    for feature, importance in prediction['feature_importance'].items():
                        if feature not in feature_importance_combined:
                            feature_importance_combined[feature] = 0
                        feature_importance_combined[feature] += importance * weight

            except Exception as e:
                print(f"⚠️  Error getting prediction from {model.model_name}: {e}")
                continue

        # Step 4: Calculate consensus
        total_weight = sum(adjusted_weights.values())
        call_weight = sum(call_votes)
        put_weight = sum(put_votes)

        # Determine consensus signal
        if call_weight > put_weight:
            consensus_signal = 'CALL'
            agreement_pct = (call_weight / total_weight) * 100
        elif put_weight > call_weight:
            consensus_signal = 'PUT'
            agreement_pct = (put_weight / total_weight) * 100
        else:
            consensus_signal = 'NEUTRAL'
            agreement_pct = 50.0

        # Check consensus threshold
        consensus_reached = agreement_pct >= (self.consensus_threshold * 100)

        # Step 5: Calculate weighted average confidence
        if all_confidences:
            avg_confidence = sum(all_confidences) / total_weight
        else:
            avg_confidence = 50.0

        # Step 6: Calibrate confidence based on historical accuracy
        calibrated_confidence = self._calibrate_confidence(
            avg_confidence, current_regime
        )

        # Step 7: Calculate uncertainty (ensemble disagreement)
        uncertainty = self._calculate_uncertainty(votes, total_weight)

        # Step 8: Regime-based signal adjustment
        if regime_info['risk_level'] == 'HIGH':
            # Reduce confidence in high-risk regimes
            calibrated_confidence *= 0.85
            uncertainty += 10

        # Step 9: Combine reasoning from all models
        all_reasoning = []
        for model_name, vote in votes.items():
            weight = adjusted_weights.get(model_name, 1.0)
            all_reasoning.append(
                f"{model_name} (w:{weight:.1f}): {vote['reasoning']}"
            )

        combined_reasoning = " | ".join(all_reasoning)

        # Step 10: Add regime context to reasoning
        regime_context = (
            f" | REGIME: {regime_info['regime_name']} "
            f"({regime_info['confidence']:.0f}% conf) - "
            f"{regime_info['recommended_strategy']}"
        )
        combined_reasoning += regime_context

        # Normalize feature importance
        if feature_importance_combined:
            max_importance = max(abs(v) for v in feature_importance_combined.values())
            if max_importance > 0:
                feature_importance_combined = {
                    k: round(v / max_importance, 2)
                    for k, v in feature_importance_combined.items()
                }

        return {
            'signal': consensus_signal if consensus_reached else 'NEUTRAL',
            'confidence': round(avg_confidence, 1),
            'confidence_calibrated': round(calibrated_confidence, 1),
            'agreement': round(agreement_pct, 1),
            'models_voted': votes,
            'reasoning': combined_reasoning,
            'consensus_reached': consensus_reached,
            'total_models': len(self.models),
            'call_weight': round(call_weight, 2),
            'put_weight': round(put_weight, 2),
            'regime': regime_info,
            'feature_importance': feature_importance_combined,
            'uncertainty': round(uncertainty, 1),
            'adjusted_weights': adjusted_weights,
            'exploration_mode': self._should_explore()
        }

    def _get_regime_adjusted_weights(self, regime: str) -> Dict[str, float]:
        """
        Adjust model weights based on their performance in the current regime
        """
        adjusted_weights = {}

        for model_name, base_weight in self.model_weights.items():
            if regime in self.model_performance_by_regime:
                regime_stats = self.model_performance_by_regime[regime].get(
                    model_name, {'accuracy': 0.5}
                )
                regime_accuracy = regime_stats.get('accuracy', 0.5)

                # Boost weight if model performs well in this regime
                # accuracy > 0.6: boost, < 0.5: reduce
                accuracy_multiplier = 0.5 + (regime_accuracy * 1.0)

                adjusted_weights[model_name] = base_weight * accuracy_multiplier
            else:
                adjusted_weights[model_name] = base_weight

        return adjusted_weights

    def _should_explore(self) -> bool:
        """
        Multi-Armed Bandit: Decide whether to explore (random) or exploit (best)
        """
        import random
        return random.random() < self.exploration_rate

    def _calibrate_confidence(self, raw_confidence: float, regime: str) -> float:
        """
        Calibrate confidence score based on historical accuracy

        If models say 80% confidence, but historically only 60% accurate,
        adjust confidence down to 60%
        """
        # Get average historical accuracy in this regime
        total_accuracy = 0
        model_count = 0

        for model_name in self.model_weights:
            if regime in self.model_performance_by_regime:
                stats = self.model_performance_by_regime[regime].get(model_name, {})
                if stats.get('total_predictions', 0) > 10:  # Need minimum data
                    total_accuracy += stats.get('accuracy', 0.5)
                    model_count += 1

        if model_count > 0:
            avg_accuracy = total_accuracy / model_count
            # Calibrate: blend raw confidence with historical accuracy
            calibrated = (raw_confidence * 0.6) + (avg_accuracy * 100 * 0.4)
        else:
            # Not enough data, use raw confidence
            calibrated = raw_confidence

        return max(30, min(95, calibrated))

    def _calculate_uncertainty(self, votes: Dict, total_weight: float) -> float:
        """
        Calculate prediction uncertainty based on model disagreement

        Higher disagreement = higher uncertainty
        """
        if len(votes) < 2:
            return 50.0

        confidences = [v['confidence'] for v in votes.values()]
        signals = [v['signal'] for v in votes.values()]

        # Disagreement in signals
        call_count = sum(1 for s in signals if s == 'CALL')
        put_count = sum(1 for s in signals if s == 'PUT')
        signal_disagreement = min(call_count, put_count) / len(signals) * 100

        # Variance in confidence
        import numpy as np
        confidence_variance = np.std(confidences)

        # Combined uncertainty
        uncertainty = (signal_disagreement * 0.6) + (confidence_variance * 0.4)

        return min(uncertainty, 50.0)

    def update_model_performance(self, model_name: str, regime: str,
                                  prediction_correct: bool, confidence: float):
        """
        Update model performance for a specific regime

        This enables regime-aware weight adjustment
        """
        if regime not in self.model_performance_by_regime:
            return

        if model_name not in self.model_performance_by_regime[regime]:
            self.model_performance_by_regime[regime][model_name] = {
                'accuracy': 0.5,
                'total_predictions': 0,
                'correct_predictions': 0,
                'avg_confidence': 0.5
            }

        stats = self.model_performance_by_regime[regime][model_name]
        stats['total_predictions'] += 1

        if prediction_correct:
            stats['correct_predictions'] += 1

        # Update accuracy
        stats['accuracy'] = stats['correct_predictions'] / stats['total_predictions']

        # Update average confidence
        total = stats['total_predictions']
        stats['avg_confidence'] = (
            (stats['avg_confidence'] * (total - 1) + confidence / 100) / total
        )

        # Adjust base model weight based on overall performance
        self._adjust_model_weight(model_name, prediction_correct)

    def _adjust_model_weight(self, model_name: str, prediction_correct: bool):
        """
        Dynamically adjust model weight based on performance

        Uses exponential moving average for smooth adjustments
        """
        if model_name not in self.model_weights:
            return

        current_weight = self.model_weights[model_name]

        # Adjustment factor
        if prediction_correct:
            # Reward: increase weight by 2%
            new_weight = current_weight * 1.02
        else:
            # Penalty: decrease weight by 3%
            new_weight = current_weight * 0.97

        # Clamp weights between 0.3 and 2.5
        new_weight = max(0.3, min(2.5, new_weight))

        self.model_weights[model_name] = round(new_weight, 2)

        print(f"🔄 Adjusted {model_name} weight: {current_weight:.2f} → {new_weight:.2f}")

    def get_model_summary(self) -> Dict:
        """Get comprehensive summary of all models"""
        summary = {
            'total_models': len(self.models),
            'consensus_threshold': self.consensus_threshold * 100,
            'models': [],
            'performance_by_regime': {}
        }

        # Model details
        for model in self.models:
            info = model.get_model_info()
            info['weight'] = self.model_weights.get(model.model_name, 1.0)

            # Add regime performance
            regime_perf = {}
            for regime in self.model_performance_by_regime:
                stats = self.model_performance_by_regime[regime].get(
                    model.model_name, {}
                )
                if stats.get('total_predictions', 0) > 0:
                    regime_perf[regime] = {
                        'accuracy': round(stats['accuracy'] * 100, 1),
                        'predictions': stats['total_predictions']
                    }

            info['regime_performance'] = regime_perf
            summary['models'].append(info)

        return summary

    def _neutral_response(self, reason: str) -> Dict:
        """Return neutral response when consensus fails"""
        return {
            'signal': 'NEUTRAL',
            'confidence': 0,
            'agreement': 0,
            'models_voted': {},
            'reasoning': reason,
            'consensus_reached': False
        }

    def print_enhanced_summary(self, consensus: Dict):
        """Print formatted enhanced consensus summary"""
        print("\n" + "=" * 80)
        print("🤖 ENHANCED AI CONSENSUS ANALYSIS")
        print("=" * 80)

        # Main signal
        print(f"\n📊 Consensus Signal: {consensus['signal']}")
        print(f"   Raw Confidence: {consensus['confidence']:.1f}%")
        print(f"   Calibrated Confidence: {consensus['confidence_calibrated']:.1f}%")
        print(f"   Agreement: {consensus['agreement']:.1f}%")
        print(f"   Uncertainty: {consensus['uncertainty']:.1f}%")
        print(f"   Consensus Reached: {'✅ YES' if consensus['consensus_reached'] else '❌ NO'}")

        # Market regime
        regime = consensus.get('regime', {})
        print(f"\n🌐 Market Regime: {regime.get('regime_name', 'Unknown')}")
        print(f"   Confidence: {regime.get('confidence', 0):.1f}%")
        print(f"   Risk Level: {regime.get('risk_level', 'UNKNOWN')}")
        print(f"   Strategy: {regime.get('recommended_strategy', 'N/A')}")

        # Feature importance
        features = consensus.get('feature_importance', {})
        if features:
            print(f"\n🔍 Top Features (Importance):")
            sorted_features = sorted(
                features.items(), key=lambda x: abs(x[1]), reverse=True
            )
            for feature, importance in sorted_features[:5]:
                print(f"   • {feature}: {importance:+.2f}")

        # Voting breakdown
        print(f"\n📈 Voting Breakdown:")
        print(f"   CALL Weight: {consensus['call_weight']:.2f}")
        print(f"   PUT Weight: {consensus['put_weight']:.2f}")

        # Individual votes
        print(f"\n🗳️  Individual Model Votes:")
        weights = consensus.get('adjusted_weights', {})
        for model_name, vote in consensus['models_voted'].items():
            weight = weights.get(model_name, 1.0)
            print(f"   • {model_name} (weight: {weight:.2f})")
            print(f"     Signal: {vote['signal']} | Confidence: {vote['confidence']}%")
            print(f"     Reasoning: {vote['reasoning'][:80]}...")

        print("\n" + "=" * 80)
