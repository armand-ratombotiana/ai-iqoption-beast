"""
Base AI Model Interface
Abstract base class for all AI trading signal generators
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime


class BaseAIModel(ABC):
    """Abstract base class for AI models"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.total_predictions = 0
        self.correct_predictions = 0

    @abstractmethod
    def predict(self, market_data: Dict) -> Dict:
        """
        Generate trading signal from market data

        Args:
            market_data: Dictionary containing:
                - pair: str (e.g., 'EURUSD-OTC')
                - current_price: float
                - rsi_14: float
                - macd: dict
                - trend: str
                - volatility: str
                - timeframe: str (e.g., '1m', '5m')
                - ... other indicators

        Returns:
            Dictionary containing:
                - signal: str ('CALL' or 'PUT')
                - confidence: int (0-100)
                - reasoning: str
                - model: str (model name)
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        """Return model metadata"""
        pass

    def update_performance(self, prediction_correct: bool):
        """Update model performance metrics"""
        self.total_predictions += 1
        if prediction_correct:
            self.correct_predictions += 1

    def get_accuracy(self) -> float:
        """Calculate model accuracy"""
        if self.total_predictions == 0:
            return 0.0
        return (self.correct_predictions / self.total_predictions) * 100

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
    "reasoning": "<brief 1-2 sentence explanation>"
}}

Consider:
1. RSI < 30 = oversold (potential CALL), RSI > 70 = overbought (potential PUT)
2. MACD crossing above signal = bullish, below = bearish
3. Price near support = potential CALL, near resistance = potential PUT
4. Strong uptrend + pullback = CALL opportunity
5. Combine multiple indicators for higher confidence"""

        return prompt
