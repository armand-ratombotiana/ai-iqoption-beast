"""
OpenClaw Model Integration
Open-source LLM integration for trading signal generation

Supports multiple open-source models:
- Ollama (local models)
- HuggingFace Inference API
- LM Studio
- LocalAI
- OpenRouter (aggregator for open models)
"""

import os
import json
import requests
from typing import Dict, Optional, Literal
from .base_model import BaseAIModel


class OpenClawModel(BaseAIModel):
    """
    OpenClaw - Open-source LLM model for trading signals
    
    Supports multiple backends:
    - ollama: Local Ollama server
    - huggingface: HuggingFace Inference API
    - lmstudio: LM Studio local server
    - localai: LocalAI server
    - openrouter: OpenRouter API (aggregator)
    """
    
    def __init__(
        self,
        backend: Literal["ollama", "huggingface", "lmstudio", "localai", "openrouter"] = "ollama",
        model_name: str = "llama3.2",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize OpenClaw model
        
        Args:
            backend: Backend to use (ollama, huggingface, lmstudio, localai, openrouter)
            model_name: Model name (depends on backend)
            api_key: API key (for huggingface, openrouter)
            base_url: Custom base URL (for local servers)
        """
        super().__init__(f"openclaw-{backend}-{model_name}")
        
        self.backend = backend
        self.model_name_raw = model_name
        self.api_key = api_key or os.getenv('OPENCLAW_API_KEY') or os.getenv('HUGGINGFACE_API_KEY')
        
        # Configure backend-specific settings
        self._configure_backend(base_url)
    
    def _configure_backend(self, base_url: Optional[str]):
        """Configure backend-specific settings"""
        if self.backend == "ollama":
            self.api_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
            self.chat_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434/api/chat')
            self.requires_auth = False
            
        elif self.backend == "huggingface":
            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name_raw}"
            self.requires_auth = True
            
        elif self.backend == "lmstudio":
            self.api_url = base_url or os.getenv('LMSTUDIO_URL', 'http://localhost:1234/v1/chat/completions')
            self.requires_auth = False
            
        elif self.backend == "localai":
            self.api_url = base_url or os.getenv('LOCALAI_URL', 'http://localhost:8080/v1/chat/completions')
            self.requires_auth = False
            
        elif self.backend == "openrouter":
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            self.requires_auth = True
            self.api_key = self.api_key or os.getenv('OPENROUTER_API_KEY')
    
    def predict(self, market_data: Dict) -> Dict:
        """Generate trading signal using OpenClaw backend"""
        try:
            prompt = self._create_analysis_prompt(market_data)
            
            # Route to appropriate backend
            if self.backend == "ollama":
                return self._predict_ollama(prompt)
            elif self.backend == "huggingface":
                return self._predict_huggingface(prompt)
            elif self.backend == "lmstudio":
                return self._predict_lmstudio(prompt)
            elif self.backend == "localai":
                return self._predict_localai(prompt)
            elif self.backend == "openrouter":
                return self._predict_openrouter(prompt)
            else:
                raise ValueError(f"Unknown backend: {self.backend}")
                
        except Exception as e:
            print(f"OpenClaw prediction error ({self.backend}): {e}")
            return {
                'signal': 'CALL',
                'confidence': 50,
                'reasoning': f'Error: {str(e)}',
                'model': self.model_name
            }
    
    def _predict_ollama(self, prompt: str) -> Dict:
        """Predict using Ollama local server"""
        try:
            # Try chat endpoint first (preferred)
            payload = {
                "model": self.model_name_raw,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert binary options trading analyst. Respond ONLY with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200
                }
            }
            
            response = requests.post(self.chat_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['message']['content']
            
            return self._parse_response(content)
            
        except Exception as e:
            print(f"Ollama error: {e}")
            # Fallback to generate endpoint
            try:
                payload = {
                    "model": self.model_name_raw,
                    "prompt": f"You are a trading analyst. {prompt}\n\nRespond with JSON only.",
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200
                    }
                }
                
                response = requests.post(self.api_url, json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                content = result['response']
                
                return self._parse_response(content)
            except Exception as e2:
                raise Exception(f"Ollama fallback failed: {e2}")
    
    def _predict_huggingface(self, prompt: str) -> Dict:
        """Predict using HuggingFace Inference API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": f"You are a trading analyst. {prompt}\n\nRespond with JSON: {{\"signal\": \"CALL\" or \"PUT\", \"confidence\": 0-100, \"reasoning\": \"...\"}}",
            "parameters": {
                "temperature": 0.3,
                "max_new_tokens": 200,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # HuggingFace returns array
        if isinstance(result, list) and len(result) > 0:
            content = result[0].get('generated_text', '')
        else:
            content = result.get('generated_text', '')
        
        return self._parse_response(content)
    
    def _predict_lmstudio(self, prompt: str) -> Dict:
        """Predict using LM Studio local server"""
        payload = {
            "model": self.model_name_raw,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert binary options trading analyst. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        response = requests.post(self.api_url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return self._parse_response(content)
    
    def _predict_localai(self, prompt: str) -> Dict:
        """Predict using LocalAI server"""
        payload = {
            "model": self.model_name_raw,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert binary options trading analyst. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        response = requests.post(self.api_url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return self._parse_response(content)
    
    def _predict_openrouter(self, prompt: str) -> Dict:
        """Predict using OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/kael-trading",
            "X-Title": "KAEL Trading System"
        }
        
        payload = {
            "model": self.model_name_raw,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert binary options trading analyst. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return self._parse_response(content)
    
    def _parse_response(self, content: str) -> Dict:
        """Parse LLM response and extract trading signal"""
        try:
            # Try to extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                prediction = json.loads(json_str)
            else:
                # Try parsing entire content as JSON
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
            
        except json.JSONDecodeError:
            # Fallback: try to extract signal from text
            content_upper = content.upper()
            
            if 'PUT' in content_upper and 'CALL' not in content_upper:
                signal = 'PUT'
            else:
                signal = 'CALL'
            
            # Try to extract confidence
            confidence = 60  # Default
            if 'CONFIDENCE' in content_upper:
                # Try to find number after confidence
                import re
                match = re.search(r'CONFIDENCE[:\s]+(\d+)', content_upper)
                if match:
                    confidence = int(match.group(1))
            
            return {
                'signal': signal,
                'confidence': confidence,
                'reasoning': content[:200],  # First 200 chars
                'model': self.model_name
            }
    
    def get_model_info(self) -> Dict:
        """Return model metadata"""
        return {
            'name': self.model_name,
            'provider': f'OpenClaw-{self.backend}',
            'model': self.model_name_raw,
            'backend': self.backend,
            'type': 'Open-Source LLM',
            'accuracy': self.get_accuracy(),
            'total_predictions': self.total_predictions,
            'requires_auth': self.requires_auth
        }
    
    @staticmethod
    def list_available_models() -> Dict[str, list]:
        """List popular models for each backend"""
        return {
            'ollama': [
                'llama3.2',
                'llama3.1',
                'llama2',
                'mistral',
                'mixtral',
                'phi3',
                'gemma2',
                'qwen2.5',
                'codellama',
                'deepseek-coder'
            ],
            'huggingface': [
                'meta-llama/Llama-3.2-3B-Instruct',
                'mistralai/Mistral-7B-Instruct-v0.3',
                'google/gemma-2-9b-it',
                'Qwen/Qwen2.5-7B-Instruct',
                'microsoft/Phi-3-mini-4k-instruct'
            ],
            'openrouter': [
                'meta-llama/llama-3.2-3b-instruct:free',
                'mistralai/mistral-7b-instruct:free',
                'google/gemma-2-9b-it:free',
                'qwen/qwen-2.5-7b-instruct:free',
                'microsoft/phi-3-mini-128k-instruct:free'
            ],
            'lmstudio': [
                'Any model loaded in LM Studio'
            ],
            'localai': [
                'Any model configured in LocalAI'
            ]
        }
    
    @staticmethod
    def get_recommended_model(backend: str) -> str:
        """Get recommended model for backend"""
        recommendations = {
            'ollama': 'llama3.2',
            'huggingface': 'meta-llama/Llama-3.2-3B-Instruct',
            'lmstudio': 'llama-3.2-3b-instruct',
            'localai': 'llama-3.2-3b-instruct',
            'openrouter': 'meta-llama/llama-3.2-3b-instruct:free'
        }
        return recommendations.get(backend, 'llama3.2')


# Convenience function to create OpenClaw model
def create_openclaw_model(
    backend: str = "ollama",
    model_name: Optional[str] = None,
    **kwargs
) -> OpenClawModel:
    """
    Create OpenClaw model with recommended settings
    
    Args:
        backend: Backend to use
        model_name: Model name (uses recommended if None)
        **kwargs: Additional arguments for OpenClawModel
    
    Returns:
        Configured OpenClawModel instance
    """
    if model_name is None:
        model_name = OpenClawModel.get_recommended_model(backend)
    
    return OpenClawModel(backend=backend, model_name=model_name, **kwargs)