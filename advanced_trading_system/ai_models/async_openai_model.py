"""
Async OpenAI Model
High-performance async implementation with connection pooling
"""
import os
import json
import aiohttp
from typing import Dict, Optional

from .async_base_model import AsyncBaseAIModel


class AsyncOpenAIModel(AsyncBaseAIModel):
    """Async OpenAI GPT model for trading signals"""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        super().__init__(f"async-openai-{model_name}")
        self.gpt_model = model_name
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    async def predict_async(self, market_data: Dict) -> Dict:
        """Generate trading signal using OpenAI API (async)"""
        if not self.session:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        prompt = self._create_analysis_prompt(market_data)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.gpt_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert binary options trading analyst. Provide concise, data-driven trading signals based on technical analysis. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 300,
            "response_format": {"type": "json_object"}
        }

        async with self.session.post(self.api_url, headers=headers, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"OpenAI API error {response.status}: {error_text}")
            
            result = await response.json()
            content = result['choices'][0]['message']['content']

            # Parse JSON response
            try:
                prediction = json.loads(content)
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON response: {content}")

            # Validate and normalize
            signal = prediction.get('signal', 'CALL').upper()
            if signal not in ['CALL', 'PUT']:
                signal = 'CALL'

            confidence = int(prediction.get('confidence', 50))
            confidence = max(0, min(100, confidence))

            # Extract feature importance if available
            feature_importance = prediction.get('feature_importance', {})

            return {
                'signal': signal,
                'confidence': confidence,
                'reasoning': prediction.get('reasoning', 'No reasoning provided'),
                'feature_importance': feature_importance
            }

    def get_model_info(self) -> Dict:
        """Return model metadata"""
        base_info = super().get_model_info()
        base_info.update({
            'provider': 'OpenAI',
            'model': self.gpt_model,
            'type': 'LLM-Async'
        })
        return base_info


class AsyncOpenAIModelWithRetry(AsyncOpenAIModel):
    """OpenAI model with automatic retry logic"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None, 
                 max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(model_name, api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    async def predict_async(self, market_data: Dict) -> Dict:
        """Predict with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await super().predict_async(market_data)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    import asyncio
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    
        # If all retries failed
        raise last_exception