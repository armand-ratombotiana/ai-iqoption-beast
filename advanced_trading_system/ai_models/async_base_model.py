"""
Async Base AI Model Interface
Enhanced base class with async support and performance monitoring
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime
import asyncio
import time
import aiohttp
import json


class AsyncBaseAIModel(ABC):
    """Enhanced async base class for AI models"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.total_predictions = 0
        self.correct_predictions = 0
        self.total_response_time = 0.0
        self.error_count = 0
        self.last_error = None
        self.session = None

    async def initialize(self):
        """Initialize async resources"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10)
        )

    async def cleanup(self):
        """Cleanup async resources"""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def predict_async(self, market_data: Dict) -> Dict:
        """
        Generate trading signal from market data (async)

        Args:
            market_data: Dictionary containing market indicators

        Returns:
            Dictionary containing:
                - signal: str ('CALL' or 'PUT')
                - confidence: int (0-100)
                - reasoning: str
                - model: str (model name)
                - response_time: float (seconds)
                - feature_importance: Dict (optional)
        """
        pass

    async def predict_with_monitoring(self, market_data: Dict) -> Dict:
        """Predict with performance monitoring"""
        start_time = time.time()
        
        try:
            prediction = await self.predict_async(market_data)
            response_time = time.time() - start_time
            
            # Add monitoring data
            prediction['response_time'] = round(response_time, 3)
            prediction['model'] = self.model_name
            prediction['timestamp'] = datetime.now().isoformat()
            
            # Update statistics
            self.total_predictions += 1
            self.total_response_time += response_time
            
            return prediction
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            response_time = time.time() - start_time
            
            # Return error prediction
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reasoning': f'Error: {str(e)}',
                'model': self.model_name,
                'response_time': round(response_time, 3),
                'error': True,
                'timestamp': datetime.now().isoformat()
            }

    def update_performance(self, prediction_correct: bool):
        """Update model performance metrics"""
        if prediction_correct:
            self.correct_predictions += 1

    def get_accuracy(self) -> float:
        """Calculate model accuracy"""
        if self.total_predictions == 0:
            return 0.0
        return (self.correct_predictions / self.total_predictions) * 100

    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        if self.total_predictions == 0:
            return 0.0
        return self.total_response_time / self.total_predictions

    def get_error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_predictions == 0:
            return 0.0
        return (self.error_count / self.total_predictions) * 100

    def get_model_info(self) -> Dict:
        """Return enhanced model metadata"""
        return {
            'name': self.model_name,
            'type': 'AsyncAI',
            'accuracy': round(self.get_accuracy(), 2),
            'total_predictions': self.total_predictions,
            'correct_predictions': self.correct_predictions,
            'avg_response_time': round(self.get_avg_response_time(), 3),
            'error_rate': round(self.get_error_rate(), 2),
            'last_error': self.last_error
        }

    def _create_analysis_prompt(self, market_data: Dict) -> str:
        """Create detailed prompt for AI analysis"""
        prompt = f"""Analyze the following market data for {market_data.get('pair', 'unknown')} and provide a trading signal for binary options (1-5 minute expiration).

Market Data:
- Current Price: {market_data.get('current_price', 'N/A')}
- Trend: {market_data.get('trend', 'unknown')}
- Volatility: {market_data.get('volatility', 'unknown')}

Technical Indicators:
- RSI (14): {market_data.get('rsi_14', 'N/A')}
- RSI (7): {market_data.get('rsi_7', 'N/A')}
- MACD: {market_data.get('macd', {}).get('macd', 'N/A')}
- MACD Signal: {market_data.get('macd', {}).get('signal', 'N/A')}
- MACD Histogram: {market_data.get('macd', {}).get('histogram', 'N/A')}
- Bollinger Bands Position: {market_data.get('bb_position', 'N/A')} (0=lower, 0.5=middle, 1=upper)
- Stochastic K: {market_data.get('stochastic', {}).get('k', 'N/A')}
- ADX: {market_data.get('adx', 'N/A')} (trend strength)
- ATR: {market_data.get('atr', 'N/A')} (volatility)

Market Context:
- Support Level: {market_data.get('support', 'N/A')}
- Resistance Level: {market_data.get('resistance', 'N/A')}
- Candlestick Pattern: {market_data.get('candlestick_pattern', 'none')}
- Hour of Day: {market_data.get('hour', 'N/A')}
- Volume Trend: {market_data.get('volume_trend', 'N/A')}

Respond ONLY with valid JSON in this exact format:
{{
    "signal": "CALL" or "PUT",
    "confidence": <integer 0-100>,
    "reasoning": "<brief 1-2 sentence explanation>",
    "feature_importance": {{
        "rsi_14": <float -1 to 1>,
        "macd_histogram": <float -1 to 1>,
        "trend": <float -1 to 1>
    }}
}}

Consider:
1. RSI < 30 = oversold (potential CALL), RSI > 70 = overbought (potential PUT)
2. MACD crossing above signal = bullish, below = bearish
3. Price near support = potential CALL, near resistance = potential PUT
4. Strong uptrend + pullback = CALL opportunity
5. Combine multiple indicators for higher confidence"""

        return prompt

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()


class AsyncModelPool:
    """Pool of async AI models for concurrent predictions"""
    
    def __init__(self, max_concurrent: int = 5):
        self.models: List[AsyncBaseAIModel] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def add_model(self, model: AsyncBaseAIModel):
        """Add model to pool"""
        await model.initialize()
        self.models.append(model)
        
    async def predict_all(self, market_data: Dict) -> List[Dict]:
        """Get predictions from all models concurrently"""
        async def _predict_with_semaphore(model):
            async with self.semaphore:
                return await model.predict_with_monitoring(market_data)
        
        tasks = [_predict_with_semaphore(model) for model in self.models]
        predictions = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_predictions = []
        for i, prediction in enumerate(predictions):
            if isinstance(prediction, Exception):
                print(f"Model {self.models[i].model_name} failed: {prediction}")
            else:
                valid_predictions.append(prediction)
                
        return valid_predictions
    
    async def cleanup_all(self):
        """Cleanup all models"""
        tasks = [model.cleanup() for model in self.models]
        await asyncio.gather(*tasks, return_exceptions=True)
        
    def get_pool_stats(self) -> Dict:
        """Get statistics for all models in pool"""
        stats = {
            'total_models': len(self.models),
            'models': []
        }
        
        for model in self.models:
            stats['models'].append(model.get_model_info())
            
        return stats