"""
Anthropic Claude Model Integration
Uses Claude API for trading signal generation
"""
import os
import json
import requests
from typing import Dict, Optional
from .base_model import BaseAIModel


class ClaudeModel(BaseAIModel):
    """Anthropic Claude model for trading signals"""

    def __init__(self, model_name: str = "claude-3-5-haiku-20241022", api_key: Optional[str] = None):
        super().__init__(f"claude-{model_name}")
        self.claude_model = model_name
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.api_url = "https://api.anthropic.com/v1/messages"

    def predict(self, market_data: Dict) -> Dict:
        """Generate trading signal using Claude API"""
        try:
            prompt = self._create_analysis_prompt(market_data)

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.claude_model,
                "max_tokens": 300,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": f"""You are an expert binary options trading analyst. {prompt}

IMPORTANT: Respond ONLY with valid JSON, no other text. Format:
{{
    "signal": "CALL" or "PUT",
    "confidence": <number 0-100>,
    "reasoning": "<brief explanation>"
}}"""
                    }
                ]
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            content = result['content'][0]['text']

            # Extract JSON from response (Claude may add extra text)
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
            print(f"Claude prediction error: {e}")
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
            'provider': 'Anthropic',
            'model': self.claude_model,
            'type': 'LLM',
            'accuracy': self.get_accuracy(),
            'total_predictions': self.total_predictions
        }
