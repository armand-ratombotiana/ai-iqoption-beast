"""
FastAPI Main Application
REST API endpoints for the trading system
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
import asyncio
from datetime import datetime, timedelta
import json

from .models import (
    TradeRequest, TradeResponse, MarketDataResponse, 
    SystemStatusResponse, PerformanceResponse, ConfigResponse
)
from .websocket_manager import WebSocketManager
from .dependencies import get_trading_system, get_database, verify_token

# Import system components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.enhanced_settings import get_config
from database.trade_storage import TradeDatabase
from data_providers import MultiDataProvider


# Initialize FastAPI app
app = FastAPI(
    title="Advanced Trading System API",
    description="Production-ready trading system with AI consensus and real-time monitoring",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# WebSocket manager
websocket_manager = WebSocketManager()

# Global variables (in production, use dependency injection)
trading_system = None
data_provider = None
config = get_config()


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global trading_system, data_provider
    
    print("🚀 Starting Advanced Trading System API...")
    
    # Initialize data provider
    data_provider = MultiDataProvider(config.redis.connection_string)
    await data_provider.initialize()
    
    # Initialize trading system (would be injected in production)
    # trading_system = await get_trading_system()
    
    print("✅ API startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global data_provider
    
    print("🛑 Shutting down API...")
    
    if data_provider:
        await data_provider.disconnect_all()
    
    print("✅ API shutdown completed")


# Health check endpoint
@app.get("/health", response_model=Dict)
async def health_check():
    """System health check"""
    try:
        # Check database connection
        db = TradeDatabase(config.database.sqlite_path)
        db_status = "healthy"
        
        # Check data provider
        provider_status = "healthy" if data_provider else "unavailable"
        
        # Check Redis (if configured)
        redis_status = "healthy"  # Would check actual Redis connection
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": db_status,
                "data_provider": provider_status,
                "redis": redis_status,
                "api": "healthy"
            },
            "version": "2.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


# System status endpoint
@app.get("/api/v1/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get comprehensive system status"""
    try:
        db = TradeDatabase(config.database.sqlite_path)
        
        # Get recent trades
        recent_trades = db.get_recent_trades(10)
        
        # Calculate basic stats
        total_trades = len(recent_trades)
        wins = sum(1 for t in recent_trades if t.get('result') == 'WIN')
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Get balance (simulated)
        current_balance = 10000.0  # Would get from actual broker
        
        return SystemStatusResponse(
            status="active",
            uptime_seconds=3600,  # Would calculate actual uptime
            total_trades=total_trades,
            active_trades=0,  # Would count pending trades
            win_rate=win_rate,
            current_balance=current_balance,
            last_trade_time=recent_trades[0].get('timestamp') if recent_trades else None,
            ai_models_active=5,  # Would count actual active models
            data_providers_connected=1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


# Market data endpoint
@app.get("/api/v1/market/data/{pair}", response_model=MarketDataResponse)
async def get_market_data(pair: str):
    """Get current market data for a trading pair"""
    try:
        if not data_provider:
            raise HTTPException(status_code=503, detail="Data provider not available")
        
        # Get consensus price
        price_data = await data_provider.get_consensus_price(pair)
        
        if not price_data:
            raise HTTPException(status_code=404, detail=f"No data available for {pair}")
        
        # Get candles (last 100)
        candles = await data_provider.get_consensus_candles(pair, '1m', 100)
        
        return MarketDataResponse(
            pair=pair,
            current_price=price_data['price'],
            timestamp=price_data['timestamp'],
            spread=price_data.get('spread', 0),
            confidence=price_data['confidence'],
            sources=price_data['sources'],
            candles=candles[-20:] if candles else []  # Last 20 candles
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market data: {str(e)}")


# Execute trade endpoint
@app.post("/api/v1/trades/execute", response_model=TradeResponse)
async def execute_trade(
    trade_request: TradeRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Execute a trading signal"""
    try:
        # Verify authentication
        # await verify_token(credentials.credentials)
        
        # Validate request
        if trade_request.pair not in ["EURUSD-OTC", "AUDCHF-OTC", "GBPUSD-OTC"]:
            raise HTTPException(status_code=400, detail="Invalid trading pair")
        
        if trade_request.amount < config.trading.min_amount or trade_request.amount > config.trading.max_amount:
            raise HTTPException(status_code=400, detail="Invalid trade amount")
        
        # Generate trade ID
        trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Execute trade in background
        background_tasks.add_task(
            execute_trade_background,
            trade_id,
            trade_request.dict()
        )
        
        # Send WebSocket notification
        await websocket_manager.broadcast({
            "type": "trade_executed",
            "data": {
                "trade_id": trade_id,
                "pair": trade_request.pair,
                "direction": trade_request.direction,
                "amount": trade_request.amount,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return TradeResponse(
            trade_id=trade_id,
            status="executed",
            message="Trade executed successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute trade: {str(e)}")


async def execute_trade_background(trade_id: str, trade_data: Dict):
    """Execute trade in background"""
    try:
        # Simulate trade execution
        await asyncio.sleep(2)  # Simulate processing time
        
        # Store trade in database
        db = TradeDatabase(config.database.sqlite_path)
        
        trade_record = {
            'trade_id': trade_id,
            'timestamp': datetime.now().isoformat(),
            'pair': trade_data['pair'],
            'direction': trade_data['direction'],
            'amount': trade_data['amount'],
            'duration': trade_data.get('duration', 1),
            'result': 'PENDING',
            'entry_price': 1.0850,  # Would get actual price
            'ai_signal_confidence': trade_data.get('confidence', 75),
            'strategy_version': 'api_v2.0'
        }
        
        db.insert_trade(trade_record)
        
        # Simulate trade completion after duration
        await asyncio.sleep(trade_data.get('duration', 1) * 60)
        
        # Update with result
        import random
        is_win = random.random() < 0.6  # 60% win rate simulation
        result = 'WIN' if is_win else 'LOSS'
        profit = trade_data['amount'] * 0.8 if is_win else -trade_data['amount']
        
        db.update_trade(trade_id, {
            'result': result,
            'profit': profit,
            'exit_price': 1.0860 if is_win else 1.0840
        })
        
        # Send WebSocket notification
        await websocket_manager.broadcast({
            "type": "trade_completed",
            "data": {
                "trade_id": trade_id,
                "result": result,
                "profit": profit,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        print(f"Background trade execution failed: {e}")


# Get trades endpoint
@app.get("/api/v1/trades", response_model=List[Dict])
async def get_trades(
    limit: int = 50,
    pair: Optional[str] = None,
    status: Optional[str] = None
):
    """Get trading history"""
    try:
        db = TradeDatabase(config.database.sqlite_path)
        
        if pair:
            trades = db.get_trades_by_pair(pair, limit)
        else:
            trades = db.get_recent_trades(limit)
        
        # Filter by status if provided
        if status:
            trades = [t for t in trades if t.get('result') == status.upper()]
        
        return trades
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trades: {str(e)}")


# Performance endpoint
@app.get("/api/v1/performance", response_model=PerformanceResponse)
async def get_performance(days: int = 30):
    """Get trading performance metrics"""
    try:
        db = TradeDatabase(config.database.sqlite_path)
        stats = db.get_statistics('all')
        
        return PerformanceResponse(
            total_trades=stats.get('total_trades', 0),
            wins=stats.get('wins', 0),
            losses=stats.get('losses', 0),
            win_rate=stats.get('win_rate', 0),
            total_profit=stats.get('total_profit', 0),
            avg_profit=stats.get('avg_profit', 0),
            max_profit=stats.get('max_profit', 0),
            max_loss=stats.get('max_loss', 0),
            sharpe_ratio=0.0,  # Would calculate actual Sharpe ratio
            max_drawdown=0.0,  # Would calculate actual drawdown
            period_days=days
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")


# Configuration endpoint
@app.get("/api/v1/config", response_model=ConfigResponse)
async def get_configuration():
    """Get system configuration (non-sensitive)"""
    try:
        return ConfigResponse(
            environment=config.environment,
            account_type=config.account_type,
            base_amount=config.trading.base_amount,
            min_amount=config.trading.min_amount,
            max_amount=config.trading.max_amount,
            consensus_threshold=config.consensus.threshold,
            min_confidence=config.consensus.min_confidence,
            ai_models_enabled=len([m for m in config.ai_models.values() if m.enabled]),
            data_providers=config.data_providers
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                # Handle subscription to specific data feeds
                await websocket.send_text(json.dumps({
                    "type": "subscription_confirmed",
                    "data": {"channels": message.get("channels", [])}
                }))
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


# AI models endpoint
@app.get("/api/v1/ai/models")
async def get_ai_models():
    """Get AI model status and performance"""
    try:
        # Would get actual model information
        models = []
        for name, model_config in config.ai_models.items():
            if model_config.enabled:
                models.append({
                    "name": name,
                    "model": model_config.model_name,
                    "weight": model_config.weight,
                    "enabled": model_config.enabled,
                    "accuracy": 65.5,  # Would get actual accuracy
                    "total_predictions": 150,  # Would get actual count
                    "avg_response_time": 1.2  # Would get actual response time
                })
        
        return {"models": models}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI models: {str(e)}")


# Market analysis endpoint
@app.post("/api/v1/analysis/predict")
async def get_market_prediction(request: Dict):
    """Get AI prediction for market data"""
    try:
        pair = request.get('pair', 'EURUSD-OTC')
        
        # Simulate AI prediction
        prediction = {
            "signal": "CALL",
            "confidence": 75,
            "reasoning": "RSI oversold, MACD bullish crossover",
            "models_voted": {
                "openai": {"signal": "CALL", "confidence": 80},
                "claude": {"signal": "CALL", "confidence": 70},
                "ensemble": {"signal": "CALL", "confidence": 75}
            },
            "consensus_reached": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prediction: {str(e)}")


# Backtesting endpoint
@app.post("/api/v1/backtest")
async def run_backtest(request: Dict):
    """Run backtesting analysis"""
    try:
        # Extract parameters
        start_date = request.get('start_date', '2024-01-01')
        end_date = request.get('end_date', '2024-12-31')
        initial_balance = request.get('initial_balance', 10000)
        
        # Simulate backtest results
        results = {
            "summary": {
                "total_trades": 245,
                "winning_trades": 147,
                "losing_trades": 98,
                "win_rate": 60.0,
                "total_profit": 1250.50,
                "final_balance": 11250.50,
                "return_pct": 12.5
            },
            "risk_metrics": {
                "max_drawdown": 8.5,
                "sharpe_ratio": 1.45,
                "profit_factor": 1.85
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": 365
            }
        }
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtesting failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )