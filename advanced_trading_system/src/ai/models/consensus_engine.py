"""
AI Consensus Engine
Aggregates signals from multiple AI models and determines consensus
"""
import json
from typing import Dict, List, Optional
from .base_model import BaseAIModel


class AIConsensusEngine:
    """
    Aggregates predictions from multiple AI models
    and determines consensus-based trading decisions
    """

    def __init__(self, consensus_threshold: float = 0.66):
        self.models: List[BaseAIModel] = []
        self.model_weights: Dict[str, float] = {}
        self.consensus_threshold = consensus_threshold  # 66% agreement required

    def add_model(self, model: BaseAIModel, weight: float = 1.0):
        """Register an AI model with optional weight"""
        self.models.append(model)
        self.model_weights[model.model_name] = weight
        print(f"✅ Added AI model: {model.model_name} (weight: {weight})")

    def get_consensus_signal(self, market_data: Dict) -> Dict:
        """
        Get consensus signal from all models

        Returns:
        {
            'signal': 'CALL' or 'PUT' or 'NEUTRAL',
            'confidence': 0-100 (weighted average),
            'agreement': 0-100 (% of models agreeing),
            'models_voted': {...},
            'reasoning': 'Combined analysis',
            'consensus_reached': bool
        }
        """
        if not self.models:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'agreement': 0,
                'models_voted': {},
                'reasoning': 'No AI models available',
                'consensus_reached': False
            }

        # Collect predictions from all models
        votes = {}
        call_votes = []
        put_votes = []
        all_confidences = []

        for model in self.models:
            try:
                prediction = model.predict(market_data)
                votes[model.model_name] = prediction

                weight = self.model_weights.get(model.model_name, 1.0)

                if prediction['signal'] == 'CALL':
                    call_votes.append(weight)
                elif prediction['signal'] == 'PUT':
                    put_votes.append(weight)

                # Weighted confidence
                all_confidences.append(prediction['confidence'] * weight)

            except Exception as e:
                print(f"⚠️  Error getting prediction from {model.model_name}: {e}")
                continue

        # Calculate consensus
        total_weight = sum(self.model_weights.values())
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

        # Check if consensus threshold is met
        consensus_reached = agreement_pct >= (self.consensus_threshold * 100)

        # Calculate weighted average confidence
        if all_confidences:
            avg_confidence = sum(all_confidences) / total_weight
        else:
            avg_confidence = 50.0

        # Combine reasoning from all models
        all_reasoning = []
        for model_name, vote in votes.items():
            all_reasoning.append(f"{model_name}: {vote['reasoning']}")

        combined_reasoning = " | ".join(all_reasoning)

        return {
            'signal': consensus_signal if consensus_reached else 'NEUTRAL',
            'confidence': round(avg_confidence, 1),
            'agreement': round(agreement_pct, 1),
            'models_voted': votes,
            'reasoning': combined_reasoning,
            'consensus_reached': consensus_reached,
            'total_models': len(self.models),
            'call_weight': round(call_weight, 2),
            'put_weight': round(put_weight, 2)
        }

    def update_model_weights(self, model_name: str, performance_multiplier: float):
        """
        Dynamically adjust model weights based on performance
        performance_multiplier: > 1.0 for better performance, < 1.0 for worse
        """
        if model_name in self.model_weights:
            current_weight = self.model_weights[model_name]
            new_weight = current_weight * performance_multiplier

            # Clamp weights between 0.5 and 2.0
            new_weight = max(0.5, min(2.0, new_weight))

            self.model_weights[model_name] = new_weight
            print(f"🔄 Updated {model_name} weight: {current_weight:.2f} → {new_weight:.2f}")

    def get_model_summary(self) -> Dict:
        """Get summary of all models and their weights"""
        summary = {
            'total_models': len(self.models),
            'consensus_threshold': self.consensus_threshold * 100,
            'models': []
        }

        for model in self.models:
            info = model.get_model_info()
            info['weight'] = self.model_weights.get(model.model_name, 1.0)
            summary['models'].append(info)

        return summary

    def print_consensus_summary(self, consensus: Dict):
        """Print formatted consensus summary"""
        print("\n" + "=" * 70)
        print("🤖 AI CONSENSUS ANALYSIS")
        print("=" * 70)

        print(f"\n📊 Consensus Signal: {consensus['signal']}")
        print(f"   Confidence: {consensus['confidence']:.1f}%")
        print(f"   Agreement: {consensus['agreement']:.1f}%")
        print(f"   Consensus Reached: {'✅ YES' if consensus['consensus_reached'] else '❌ NO'}")

        print(f"\n📈 Voting Breakdown:")
        print(f"   CALL Weight: {consensus['call_weight']:.2f}")
        print(f"   PUT Weight: {consensus['put_weight']:.2f}")

        print(f"\n🗳️  Individual Model Votes:")
        for model_name, vote in consensus['models_voted'].items():
            weight = self.model_weights.get(model_name, 1.0)
            print(f"   • {model_name} (weight: {weight:.1f})")
            print(f"     Signal: {vote['signal']} | Confidence: {vote['confidence']}%")
            print(f"     Reasoning: {vote['reasoning']}")

        print("\n" + "=" * 70)
