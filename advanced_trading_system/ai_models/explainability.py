"""
Explainable AI (XAI) Framework
Provides transparency and interpretability for AI trading decisions
"""
from typing import Dict, List, Tuple
import numpy as np


class ExplainabilityEngine:
    """
    Provides explainability for AI trading decisions through:
    - Feature importance analysis (SHAP-like)
    - Decision boundary visualization
    - Counterfactual explanations
    - Confidence calibration
    """

    def __init__(self):
        self.feature_contributions = {}
        self.decision_history = []

    def explain_decision(
        self,
        signal: str,
        confidence: float,
        market_data: Dict,
        feature_importance: Dict = None
    ) -> Dict:
        """
        Generate comprehensive explanation for a trading decision

        Returns:
        {
            'signal': str,
            'confidence': float,
            'explanation': str,
            'top_factors': List[Dict],
            'counterfactuals': List[str],
            'risk_factors': List[str],
            'confidence_calibration': Dict
        }
        """
        # Analyze feature importance
        if feature_importance:
            top_factors = self._get_top_factors(feature_importance)
        else:
            top_factors = self._infer_factors_from_data(market_data, signal)

        # Generate natural language explanation
        explanation = self._generate_explanation(
            signal, confidence, top_factors, market_data
        )

        # Generate counterfactual explanations
        counterfactuals = self._generate_counterfactuals(
            signal, market_data, top_factors
        )

        # Identify risk factors
        risk_factors = self._identify_risk_factors(market_data, confidence)

        # Confidence calibration
        calibration = self._calibrate_confidence(confidence, market_data)

        return {
            'signal': signal,
            'confidence': confidence,
            'explanation': explanation,
            'top_factors': top_factors,
            'counterfactuals': counterfactuals,
            'risk_factors': risk_factors,
            'confidence_calibration': calibration,
            'decision_certainty': self._calculate_certainty(confidence, market_data)
        }

    def _get_top_factors(self, feature_importance: Dict) -> List[Dict]:
        """Extract and explain top contributing features"""
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        top_factors = []
        for feature, importance in sorted_features[:5]:
            direction = 'bullish' if importance > 0 else 'bearish'
            strength = abs(importance)

            factor = {
                'feature': feature,
                'importance': round(importance, 2),
                'direction': direction,
                'strength': 'strong' if strength > 10 else 'moderate' if strength > 5 else 'weak',
                'description': self._describe_feature(feature, importance)
            }
            top_factors.append(factor)

        return top_factors

    def _infer_factors_from_data(self, market_data: Dict, signal: str) -> List[Dict]:
        """Infer important factors when feature importance is not available"""
        factors = []

        # RSI
        rsi_14 = market_data.get('rsi_14', 50)
        if rsi_14 < 30:
            factors.append({
                'feature': 'rsi_14',
                'value': rsi_14,
                'importance': 15,
                'direction': 'bullish',
                'strength': 'strong',
                'description': f'RSI at {rsi_14:.1f} indicates oversold conditions'
            })
        elif rsi_14 > 70:
            factors.append({
                'feature': 'rsi_14',
                'value': rsi_14,
                'importance': -15,
                'direction': 'bearish',
                'strength': 'strong',
                'description': f'RSI at {rsi_14:.1f} indicates overbought conditions'
            })

        # MACD
        macd_hist = market_data.get('macd', {}).get('histogram', 0)
        if abs(macd_hist) > 0.0001:
            direction = 'bullish' if macd_hist > 0 else 'bearish'
            factors.append({
                'feature': 'macd_histogram',
                'value': macd_hist,
                'importance': macd_hist * 1000,
                'direction': direction,
                'strength': 'moderate',
                'description': f'MACD histogram {direction} at {macd_hist:.6f}'
            })

        # Trend
        trend = market_data.get('trend', 'neutral')
        if trend != 'neutral':
            direction = 'bullish' if trend == 'uptrend' else 'bearish'
            factors.append({
                'feature': 'trend',
                'value': trend,
                'importance': 10 if trend == 'uptrend' else -10,
                'direction': direction,
                'strength': 'moderate',
                'description': f'Market in {trend}, favoring {direction} trades'
            })

        return factors[:5]

    def _describe_feature(self, feature: str, importance: float) -> str:
        """Generate human-readable description for a feature"""
        descriptions = {
            'rsi_14': 'Relative Strength Index (14 period)',
            'macd_histogram': 'MACD Histogram (momentum indicator)',
            'bb_position': 'Position within Bollinger Bands',
            'stochastic_k': 'Stochastic Oscillator',
            'adx': 'Average Directional Index (trend strength)',
            'trend_encoded': 'Market trend direction',
            'support_resistance_position': 'Price position relative to support/resistance'
        }

        base_desc = descriptions.get(feature, feature.replace('_', ' ').title())
        direction = 'supports CALL' if importance > 0 else 'supports PUT'

        return f"{base_desc} {direction}"

    def _generate_explanation(
        self,
        signal: str,
        confidence: float,
        factors: List[Dict],
        market_data: Dict
    ) -> str:
        """Generate natural language explanation"""
        parts = []

        # Opening
        parts.append(f"AI recommends {signal} with {confidence:.0f}% confidence.")

        # Top factors
        if factors:
            top_factor = factors[0]
            parts.append(f"Primary reason: {top_factor['description']}.")

            if len(factors) > 1:
                second_factor = factors[1]
                parts.append(f"Additionally, {second_factor['description']}.")

        # Market context
        trend = market_data.get('trend', 'neutral')
        volatility = market_data.get('volatility', 'medium')
        parts.append(
            f"Market is in {trend} with {volatility} volatility."
        )

        # Risk assessment
        if confidence < 65:
            parts.append("⚠️ Confidence is below optimal threshold. Consider reducing position size.")
        elif volatility == 'high':
            parts.append("⚠️ High volatility detected. Exercise caution.")

        return " ".join(parts)

    def _generate_counterfactuals(
        self,
        signal: str,
        market_data: Dict,
        factors: List[Dict]
    ) -> List[str]:
        """
        Generate counterfactual explanations:
        "If X were different, the decision would change to Y"
        """
        counterfactuals = []

        # RSI counterfactual
        rsi_14 = market_data.get('rsi_14', 50)
        if signal == 'CALL' and rsi_14 < 50:
            opposite_threshold = 70
            counterfactuals.append(
                f"If RSI were above {opposite_threshold} (currently {rsi_14:.1f}), "
                f"the signal would likely flip to PUT"
            )
        elif signal == 'PUT' and rsi_14 > 50:
            opposite_threshold = 30
            counterfactuals.append(
                f"If RSI were below {opposite_threshold} (currently {rsi_14:.1f}), "
                f"the signal would likely flip to CALL"
            )

        # Trend counterfactual
        trend = market_data.get('trend', 'neutral')
        if signal == 'CALL' and trend != 'downtrend':
            counterfactuals.append(
                "If market trend reversed to downtrend, confidence would drop significantly"
            )
        elif signal == 'PUT' and trend != 'uptrend':
            counterfactuals.append(
                "If market trend reversed to uptrend, confidence would drop significantly"
            )

        # MACD counterfactual
        macd_hist = market_data.get('macd', {}).get('histogram', 0)
        if macd_hist > 0 and signal == 'CALL':
            counterfactuals.append(
                "If MACD histogram turned negative, signal confidence would decrease"
            )
        elif macd_hist < 0 and signal == 'PUT':
            counterfactuals.append(
                "If MACD histogram turned positive, signal confidence would decrease"
            )

        return counterfactuals[:3]

    def _identify_risk_factors(self, market_data: Dict, confidence: float) -> List[str]:
        """Identify factors that increase risk"""
        risks = []

        # Volatility risk
        volatility = market_data.get('volatility', 'medium')
        if volatility == 'high':
            risks.append("⚠️ High market volatility increases unpredictability")

        # Confidence risk
        if confidence < 65:
            risks.append(f"⚠️ Low confidence ({confidence:.0f}%) suggests uncertain conditions")

        # Conflicting indicators
        rsi_14 = market_data.get('rsi_14', 50)
        trend = market_data.get('trend', 'neutral')
        if (rsi_14 > 70 and trend == 'uptrend') or (rsi_14 < 30 and trend == 'downtrend'):
            risks.append("⚠️ Potential trend exhaustion: RSI extreme while trend continues")

        # Range trading risk
        if trend == 'sideways':
            risks.append("⚠️ Sideways market: Breakout direction uncertain")

        # ADX risk
        adx = market_data.get('adx', 0)
        if adx < 20:
            risks.append(f"⚠️ Weak trend (ADX {adx:.0f}): Higher reversal risk")

        return risks

    def _calibrate_confidence(self, confidence: float, market_data: Dict) -> Dict:
        """
        Provide confidence calibration information

        Shows how reliable the confidence score is
        """
        # Factors that affect calibration
        volatility = market_data.get('volatility', 'medium')
        trend = market_data.get('trend', 'neutral')
        adx = market_data.get('adx', 0)

        # Base calibration
        calibrated_confidence = confidence

        # Adjust for market conditions
        adjustments = []

        if volatility == 'high':
            calibrated_confidence *= 0.85
            adjustments.append("High volatility: -15% confidence")
        elif volatility == 'low':
            calibrated_confidence *= 1.05
            adjustments.append("Low volatility: +5% confidence")

        if trend == 'sideways':
            calibrated_confidence *= 0.90
            adjustments.append("Sideways market: -10% confidence")

        if adx < 20:
            calibrated_confidence *= 0.92
            adjustments.append("Weak trend (low ADX): -8% confidence")

        calibrated_confidence = max(30, min(95, calibrated_confidence))

        return {
            'original_confidence': confidence,
            'calibrated_confidence': round(calibrated_confidence, 1),
            'reliability': 'high' if abs(confidence - calibrated_confidence) < 10 else 'moderate',
            'adjustments': adjustments
        }

    def _calculate_certainty(self, confidence: float, market_data: Dict) -> str:
        """Calculate decision certainty level"""
        # Combine confidence with market clarity
        volatility = market_data.get('volatility', 'medium')
        adx = market_data.get('adx', 0)

        certainty_score = confidence

        # Penalize for unclear market
        if volatility == 'high':
            certainty_score -= 15
        if adx < 20:
            certainty_score -= 10

        if certainty_score > 75:
            return 'VERY HIGH'
        elif certainty_score > 60:
            return 'HIGH'
        elif certainty_score > 45:
            return 'MODERATE'
        else:
            return 'LOW'

    def visualize_decision_boundary(
        self,
        signal: str,
        market_data: Dict,
        feature_importance: Dict
    ) -> Dict:
        """
        Provide decision boundary information
        (What changes would flip the decision?)
        """
        rsi_14 = market_data.get('rsi_14', 50)
        macd_hist = market_data.get('macd', {}).get('histogram', 0)

        boundaries = []

        if signal == 'CALL':
            # What would cause PUT?
            rsi_boundary = 70
            rsi_distance = rsi_boundary - rsi_14
            boundaries.append({
                'feature': 'RSI',
                'current': rsi_14,
                'boundary': rsi_boundary,
                'distance': round(rsi_distance, 1),
                'description': f'RSI needs to increase {rsi_distance:.1f} points to flip signal'
            })

        else:  # PUT
            # What would cause CALL?
            rsi_boundary = 30
            rsi_distance = rsi_14 - rsi_boundary
            boundaries.append({
                'feature': 'RSI',
                'current': rsi_14,
                'boundary': rsi_boundary,
                'distance': round(rsi_distance, 1),
                'description': f'RSI needs to decrease {rsi_distance:.1f} points to flip signal'
            })

        return {
            'signal': signal,
            'boundaries': boundaries,
            'sensitivity': 'high' if len(boundaries) > 0 and boundaries[0]['distance'] < 10 else 'moderate'
        }

    def generate_report(self, decision_explanation: Dict) -> str:
        """Generate formatted XAI report"""
        report = []

        report.append("\n" + "=" * 70)
        report.append("🔍 EXPLAINABLE AI (XAI) DECISION REPORT")
        report.append("=" * 70)

        # Decision
        report.append(f"\n📊 DECISION: {decision_explanation['signal']}")
        report.append(f"   Confidence: {decision_explanation['confidence']:.1f}%")
        report.append(f"   Certainty: {decision_explanation['decision_certainty']}")

        # Explanation
        report.append(f"\n💡 EXPLANATION:")
        report.append(f"   {decision_explanation['explanation']}")

        # Top factors
        report.append(f"\n🎯 TOP FACTORS:")
        for factor in decision_explanation['top_factors']:
            report.append(
                f"   • {factor['feature']}: {factor['importance']:+.1f} "
                f"({factor['strength']} {factor['direction']})"
            )
            report.append(f"     {factor['description']}")

        # Risk factors
        if decision_explanation['risk_factors']:
            report.append(f"\n⚠️  RISK FACTORS:")
            for risk in decision_explanation['risk_factors']:
                report.append(f"   {risk}")

        # Counterfactuals
        if decision_explanation['counterfactuals']:
            report.append(f"\n🔄 WHAT-IF SCENARIOS:")
            for cf in decision_explanation['counterfactuals']:
                report.append(f"   • {cf}")

        # Confidence calibration
        calib = decision_explanation['confidence_calibration']
        report.append(f"\n📏 CONFIDENCE CALIBRATION:")
        report.append(f"   Original: {calib['original_confidence']:.1f}%")
        report.append(f"   Calibrated: {calib['calibrated_confidence']:.1f}%")
        report.append(f"   Reliability: {calib['reliability'].upper()}")
        if calib['adjustments']:
            report.append(f"   Adjustments:")
            for adj in calib['adjustments']:
                report.append(f"   • {adj}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)
