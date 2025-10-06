"""
Pydantic Models for API Requests and Responses
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class TradeDirection(str, Enum):
    CALL = "CALL"
    PUT = "PUT"


class TradeStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TradeResult(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    PENDING = "PENDING"


# Request Models
class TradeRequest(BaseModel):
    """Request model for executing trades"""
    pair: str = Field(..., description="Trading pair (e.g., EURUSD-OTC)")
    direction: TradeDirection = Field(..., description="Trade direction")
    amount: float = Field(..., gt=0, description="Trade amount")
    duration: int = Field(default=1, ge=1, le=5, description="Trade duration in minutes")
    confidence: Optional[int] = Field(None, ge=0, le=100, description="AI confidence level")
    
    @validator('pair')
    def validate_pair(cls, v):
        allowed_pairs = ["EURUSD-OTC", "AUDCHF-OTC", "GBPUSD-OTC", "USDJPY-OTC"]
        if v not in allowed_pairs:
            raise ValueError(f"Pair must be one of {allowed_pairs}")
        return v


class BacktestRequest(BaseModel):
    """Request model for backtesting"""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_balance: float = Field(default=10000, gt=0, description="Initial balance")
    strategy_config: Optional[Dict] = Field(None, description="Strategy configuration")


class PredictionRequest(BaseModel):
    """Request model for AI predictions"""
    pair: str = Field(..., description="Trading pair")
    market_data: Optional[Dict] = Field(None, description="Current market data")


# Response Models
class TradeResponse(BaseModel):
    """Response model for trade execution"""
    trade_id: str = Field(..., description="Unique trade identifier")
    status: str = Field(..., description="Trade status")
    message: str = Field(..., description="Response message")
    timestamp: str = Field(..., description="Execution timestamp")


class MarketDataResponse(BaseModel):
    """Response model for market data"""
    pair: str = Field(..., description="Trading pair")
    current_price: float = Field(..., description="Current price")
    timestamp: str = Field(..., description="Data timestamp")
    spread: float = Field(..., description="Bid-ask spread")
    confidence: float = Field(..., description="Data confidence level")
    sources: int = Field(..., description="Number of data sources")
    candles: List[Dict] = Field(default=[], description="Recent candle data")


class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    status: str = Field(..., description="System status")
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    total_trades: int = Field(..., description="Total trades executed")
    active_trades: int = Field(..., description="Currently active trades")
    win_rate: float = Field(..., description="Overall win rate percentage")
    current_balance: float = Field(..., description="Current account balance")
    last_trade_time: Optional[str] = Field(None, description="Last trade timestamp")
    ai_models_active: int = Field(..., description="Number of active AI models")
    data_providers_connected: int = Field(..., description="Connected data providers")


class PerformanceResponse(BaseModel):
    """Response model for performance metrics"""
    total_trades: int = Field(..., description="Total number of trades")
    wins: int = Field(..., description="Number of winning trades")
    losses: int = Field(..., description="Number of losing trades")
    win_rate: float = Field(..., description="Win rate percentage")
    total_profit: float = Field(..., description="Total profit/loss")
    avg_profit: float = Field(..., description="Average profit per trade")
    max_profit: float = Field(..., description="Maximum single trade profit")
    max_loss: float = Field(..., description="Maximum single trade loss")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    period_days: int = Field(..., description="Analysis period in days")


class ConfigResponse(BaseModel):
    """Response model for system configuration"""
    environment: str = Field(..., description="Environment (dev/prod)")
    account_type: str = Field(..., description="Account type (demo/real)")
    base_amount: float = Field(..., description="Base trade amount")
    min_amount: float = Field(..., description="Minimum trade amount")
    max_amount: float = Field(..., description="Maximum trade amount")
    consensus_threshold: float = Field(..., description="AI consensus threshold")
    min_confidence: int = Field(..., description="Minimum confidence level")
    ai_models_enabled: int = Field(..., description="Number of enabled AI models")
    data_providers: List[str] = Field(..., description="Configured data providers")


class AIModelResponse(BaseModel):
    """Response model for AI model information"""
    name: str = Field(..., description="Model name")
    model: str = Field(..., description="Model version/type")
    weight: float = Field(..., description="Model weight in consensus")
    enabled: bool = Field(..., description="Model enabled status")
    accuracy: float = Field(..., description="Model accuracy percentage")
    total_predictions: int = Field(..., description="Total predictions made")
    avg_response_time: float = Field(..., description="Average response time in seconds")


class PredictionResponse(BaseModel):
    """Response model for AI predictions"""
    signal: TradeDirection = Field(..., description="Trading signal")
    confidence: int = Field(..., ge=0, le=100, description="Confidence level")
    reasoning: str = Field(..., description="Prediction reasoning")
    models_voted: Dict[str, Dict] = Field(..., description="Individual model votes")
    consensus_reached: bool = Field(..., description="Whether consensus was reached")
    timestamp: str = Field(..., description="Prediction timestamp")
    feature_importance: Optional[Dict] = Field(None, description="Feature importance scores")


class BacktestResponse(BaseModel):
    """Response model for backtesting results"""
    summary: Dict = Field(..., description="Summary statistics")
    risk_metrics: Dict = Field(..., description="Risk analysis metrics")
    period: Dict = Field(..., description="Testing period information")
    equity_curve: Optional[List[Dict]] = Field(None, description="Equity curve data")
    trades: Optional[List[Dict]] = Field(None, description="Individual trade details")


class TradeHistoryResponse(BaseModel):
    """Response model for trade history"""
    trade_id: str = Field(..., description="Trade identifier")
    timestamp: str = Field(..., description="Trade timestamp")
    pair: str = Field(..., description="Trading pair")
    direction: TradeDirection = Field(..., description="Trade direction")
    amount: float = Field(..., description="Trade amount")
    duration: int = Field(..., description="Trade duration")
    result: Optional[TradeResult] = Field(None, description="Trade result")
    profit: Optional[float] = Field(None, description="Profit/loss amount")
    entry_price: Optional[float] = Field(None, description="Entry price")
    exit_price: Optional[float] = Field(None, description="Exit price")
    ai_confidence: Optional[int] = Field(None, description="AI confidence level")


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Overall system status")
    timestamp: str = Field(..., description="Check timestamp")
    components: Dict[str, str] = Field(..., description="Component health status")
    version: str = Field(..., description="System version")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


# Utility Models
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=50, ge=1, le=1000, description="Page size")


class DateRangeParams(BaseModel):
    """Date range parameters"""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class FilterParams(BaseModel):
    """Common filter parameters"""
    pair: Optional[str] = Field(None, description="Filter by trading pair")
    status: Optional[str] = Field(None, description="Filter by status")
    result: Optional[TradeResult] = Field(None, description="Filter by trade result")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum trade amount")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum trade amount")


# Configuration Models
class AIModelConfig(BaseModel):
    """AI model configuration"""
    name: str = Field(..., description="Model name")
    enabled: bool = Field(default=True, description="Enable model")
    weight: float = Field(default=1.0, ge=0.1, le=5.0, description="Model weight")
    timeout: int = Field(default=30, ge=1, le=300, description="Timeout in seconds")


class TradingConfig(BaseModel):
    """Trading configuration"""
    base_amount: float = Field(..., gt=0, description="Base trade amount")
    min_amount: float = Field(..., gt=0, description="Minimum trade amount")
    max_amount: float = Field(..., gt=0, description="Maximum trade amount")
    default_duration: int = Field(default=1, ge=1, le=5, description="Default duration")
    
    @validator('max_amount')
    def max_amount_validation(cls, v, values):
        if 'min_amount' in values and v <= values['min_amount']:
            raise ValueError('max_amount must be greater than min_amount')
        return v


class RiskConfig(BaseModel):
    """Risk management configuration"""
    max_daily_loss: float = Field(..., gt=0, description="Maximum daily loss")
    max_consecutive_losses: int = Field(..., ge=1, description="Max consecutive losses")
    position_size_method: str = Field(default="kelly", description="Position sizing method")


# Analytics Models
class PerformanceMetrics(BaseModel):
    """Detailed performance metrics"""
    total_trades: int = Field(..., description="Total trades")
    win_rate: float = Field(..., description="Win rate percentage")
    profit_factor: float = Field(..., description="Profit factor")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    avg_trade_duration: float = Field(..., description="Average trade duration")
    best_pair: Optional[str] = Field(None, description="Best performing pair")
    worst_pair: Optional[str] = Field(None, description="Worst performing pair")


class ModelPerformance(BaseModel):
    """AI model performance metrics"""
    model_name: str = Field(..., description="Model name")
    accuracy: float = Field(..., description="Prediction accuracy")
    precision: float = Field(..., description="Precision score")
    recall: float = Field(..., description="Recall score")
    f1_score: float = Field(..., description="F1 score")
    total_predictions: int = Field(..., description="Total predictions")
    avg_confidence: float = Field(..., description="Average confidence")
    response_time_ms: float = Field(..., description="Average response time")


class MarketAnalysis(BaseModel):
    """Market analysis results"""
    pair: str = Field(..., description="Trading pair")
    trend: str = Field(..., description="Market trend")
    volatility: str = Field(..., description="Volatility level")
    support_level: float = Field(..., description="Support level")
    resistance_level: float = Field(..., description="Resistance level")
    technical_indicators: Dict = Field(..., description="Technical indicators")
    sentiment: Optional[str] = Field(None, description="Market sentiment")
    recommendation: str = Field(..., description="Trading recommendation")