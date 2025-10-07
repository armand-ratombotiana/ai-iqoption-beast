"""
DeepSeek Model Integration
Uses DeepSeek API for trading signal generation
"""
import os
import json
import requests
from typing import Dict, Optional
from .base_model import BaseAIModel


class DeepSeekModel(BaseAIModel):
    """DeepSeek model for trading signals"""

    def __init__(self, model_name: str = "deepseek-chat", api_key: Optional[str] = None):
        super().__init__(f"deepseek-{model_name}")
        self.deepseek_model = model_name
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def predict(self, market_data: Dict) -> Dict:
        """Generate trading signal using DeepSeek API"""
        try:
            prompt = self._create_analysis_prompt(market_data)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.deepseek_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert binary options trading analyst with deep knowledge of technical analysis. Provide precise, data-driven trading signals."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 200,
                "response_format": {"type": "json_object"}
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            # Parse JSON response
            prediction = json.loads(content)

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
            print(f"DeepSeek prediction error: {e}")
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
            'provider': 'DeepSeek',
            'model': self.deepseek_model,
            'type': 'LLM',
            'accuracy': self.get_accuracy(),
            'total_predictions': self.total_predictions
        }
