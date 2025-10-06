"""
Ollama Local LLM Integration
Uses locally running Ollama models (100% FREE, no API costs)
Supports: Llama 3, Mistral, Phi-3, etc.
"""
import json
import requests
from typing import Dict, Optional
from .base_model import BaseAIModel


class OllamaModel(BaseAIModel):
    """Local Ollama model for trading signals (100% FREE)"""

    def __init__(self, model_name: str = "llama3:8b", ollama_url: str = "http://localhost:11434"):
        super().__init__(f"ollama-{model_name}")
        self.ollama_model = model_name
        self.ollama_url = ollama_url

    def predict(self, market_data: Dict) -> Dict:
        """Generate trading signal using local Ollama"""
        try:
            prompt = self._create_analysis_prompt(market_data)

            payload = {
                "model": self.ollama_model,
                "prompt": f"""You are an expert binary options trading analyst. {prompt}

Respond with ONLY valid JSON:
{{"signal": "CALL" or "PUT", "confidence": 0-100, "reasoning": "brief explanation"}}""",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200
                }
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content = result['response']

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
            print(f"Ollama prediction error: {e}")
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
            'provider': 'Ollama (Local)',
            'model': self.ollama_model,
            'type': 'LLM',
            'cost': '100% FREE (Local)',
            'accuracy': self.get_accuracy(),
            'total_predictions': self.total_predictions
        }

    @staticmethod
    def list_available_models(ollama_url: str = "http://localhost:11434") -> list:
        """List all available Ollama models"""
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            return [m['name'] for m in models]
        except Exception as e:
            print(f"Could not list Ollama models: {e}")
            return []
