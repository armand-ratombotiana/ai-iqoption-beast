"""
Google Gemini Model Integration
Uses free Gemini API for trading signal generation
"""
import os
import json
import requests
from typing import Dict, Optional
from .base_model import BaseAIModel


class GeminiModel(BaseAIModel):
    """Google Gemini model for trading signals (FREE)"""

    def __init__(self, model_name: str = "gemini-pro", api_key: Optional[str] = None):
        super().__init__(f"gemini-{model_name}")
        self.gemini_model = model_name
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

    def predict(self, market_data: Dict) -> Dict:
        """Generate trading signal using Gemini API"""
        try:
            prompt = self._create_analysis_prompt(market_data)

            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"""You are an expert binary options trading analyst. {prompt}

Respond with ONLY valid JSON in this format:
{{
    "signal": "CALL" or "PUT",
    "confidence": <number 0-100>,
    "reasoning": "<brief explanation>"
}}"""
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 200
                }
            }

            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']

            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                prediction = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")

            # Validate and normalize
            signal = prediction.get('signal', 'CALL').upper()
            if signal not in ['CALL', 'PUT']:
                signal = 'CALL'

            confidence = int(prediction.get('confidence', 50))
            confidence = max(0, min(100, confidence))

            return {
                'signal': signal,
                'confidence': confidence,
                'reasoning': prediction.get('reasoning', 'No reasoning provided'),
                'model': self.model_name
            }

        except Exception as e:
            print(f"Gemini prediction error: {e}")
            return {
                'signal': 'CALL',
                'confidence': 50,
                'reasoning': f'Error: {str(e)}',
                'model': self.model_name
            }

    def get_model_info(self) -> Dict:
        """Return model metadata"""
        return {
            'name': self.model_name,
            'provider': 'Google',
            'model': self.gemini_model,
            'type': 'LLM',
            'cost': 'FREE',
            'accuracy': self.get_accuracy(),
            'total_predictions': self.total_predictions
        }
