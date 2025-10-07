"""
Free AI Model Implementation
Uses free/open-source AI models for trading signals
"""
import os
import json
import requests
from typing import Dict, Optional
from .base_model import BaseAIModel


class FreeAIModel(BaseAIModel):
    """Free AI model using Hugging Face Inference API or local models"""
    
    def __init__(self, model_type: str = "huggingface"):
        super().__init__(f"free-{model_type}")
        self.model_type = model_type
        
        # Hugging Face free inference API
        self.hf_api_url = "https://api-inference.huggingface.co/models/"
        self.hf_token = os.getenv('HUGGINGFACE_API_KEY', '')  # Optional, works without
        
    def predict(self, market_data: Dict) -> Dict:
        """Generate trading signal using free AI models"""
        try:
            # Use rule-based AI as fallback (always free)
            if not self.hf_token or self.model_type == "rule-based":
                return self._rule_based_prediction(market_data)
            
            # Try Hugging Face free inference
            return self._huggingface_prediction(market_data)
            
        except Exception as e:
            print(f"Free AI prediction error: {e}")
            # Always fallback to rule-based
            return self._rule_based_prediction(market_data)
    
    def _rule_based_prediction(self, market_data: Dict) -> Dict:
        """
        Advanced rule-based trading logic (completely free)
        Uses technical indicators to make decisions
        """
        rsi_14 = market_data.get('rsi_14', 50)
        rsi_7 = market_data.get('rsi_7', 50)
        trend = market_data.get('trend', 'sideways')
        bb_position = market_data.get('bb_position', 0.5)
        macd_histogram = market_data.get('macd_histogram', 0)
        volatility = market_data.get('volatility', 'medium')
        adx = market_data.get('adx', 25)
        
        # Initialize scoring
        call_score = 0
        put_score = 0
        confidence = 50
        reasoning = []
        
        # RSI Analysis (30 points)
        if rsi_14 < 30:
            call_score += 15
            reasoning.append("RSI(14) oversold (<30)")
            confidence += 10
        elif rsi_14 < 40:
            call_score += 8
            reasoning.append("RSI(14) low (<40)")
            confidence += 5
        elif rsi_14 > 70:
            put_score += 15
            reasoning.append("RSI(14) overbought (>70)")
            confidence += 10
        elif rsi_14 > 60:
            put_score += 8
            reasoning.append("RSI(14) high (>60)")
            confidence += 5
        
        # Short-term RSI
        if rsi_7 < 25:
            call_score += 10
            reasoning.append("RSI(7) very oversold")
        elif rsi_7 > 75:
            put_score += 10
            reasoning.append("RSI(7) very overbought")
        
        # Trend Analysis (25 points)
        if trend == 'uptrend':
            call_score += 12
            reasoning.append("Strong uptrend detected")
            confidence += 8
        elif trend == 'downtrend':
            put_score += 12
            reasoning.append("Strong downtrend detected")
            confidence += 8
        
        # Bollinger Bands (20 points)
        if bb_position < 0.2:
            call_score += 10
            reasoning.append("Price near lower BB")
            confidence += 5
        elif bb_position > 0.8:
            put_score += 10
            reasoning.append("Price near upper BB")
            confidence += 5
        
        # MACD (15 points)
        if macd_histogram > 0.0001:
            call_score += 8
            reasoning.append("MACD bullish")
        elif macd_histogram < -0.0001:
            put_score += 8
            reasoning.append("MACD bearish")
        
        # Trend Strength (ADX) (10 points)
        if adx > 25:
            if trend == 'uptrend':
                call_score += 5
                reasoning.append("Strong trend confirmed by ADX")
            elif trend == 'downtrend':
                put_score += 5
                reasoning.append("Strong trend confirmed by ADX")
            confidence += 5
        
        # Volatility adjustment
        if volatility == 'high':
            confidence -= 5
            reasoning.append("High volatility reduces confidence")
        elif volatility == 'low':
            confidence += 3
            reasoning.append("Low volatility increases confidence")
        
        # Determine signal
        if call_score > put_score:
            signal = 'CALL'
            confidence = min(95, confidence + (call_score - put_score))
        elif put_score > call_score:
            signal = 'PUT'
            confidence = min(95, confidence + (put_score - call_score))
        else:
            # Equal scores - use trend
            if trend == 'uptrend':
                signal = 'CALL'
            elif trend == 'downtrend':
                signal = 'PUT'
            else:
                signal = 'CALL'  # Default to CALL in sideways
            confidence = 55
        
        confidence = max(50, min(95, confidence))  # Clamp between 50-95
        
        return {
            'signal': signal,
            'confidence': int(confidence),
            'reasoning': f"Free AI Analysis: {'; '.join(reasoning[:3])} (Score: CALL={call_score}, PUT={put_score})",
            'model': self.model_name
        }
    
    def _huggingface_prediction(self, market_data: Dict) -> Dict:
        """Try to use Hugging Face free inference (optional)"""
        try:
            # Use a free text generation model
            model = "facebook/bart-large-mnli"  # Free classification model
            
            # Create prompt
            trend = market_data.get('trend', 'sideways')
            rsi = market_data.get('rsi_14', 50)
            
            # Simple classification approach
            text = f"Market trend is {trend} with RSI at {rsi}. Should I buy or sell?"
            
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            response = requests.post(
                f"{self.hf_api_url}{model}",
                headers=headers,
                json={"inputs": text, "parameters": {"candidate_labels": ["buy", "sell"]}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse result and convert to signal
                # This is a simplified example
                return self._rule_based_prediction(market_data)
            else:
                return self._rule_based_prediction(market_data)
                
        except Exception as e:
            print(f"Hugging Face error: {e}")
            return self._rule_based_prediction(market_data)
    
    def get_model_info(self) -> Dict:
        """Return model metadata"""
        return {
            'name': self.model_name,
            'provider': 'Free/Open-Source',
            'type': self.model_type,
            'cost': 'FREE',
            'accuracy': self.get_accuracy(),
            'total_predictions': self.total_predictions
        }
