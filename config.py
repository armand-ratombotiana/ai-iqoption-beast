from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass
class TradingConfig:
    """Trading configuration"""
    mode: str
    min_payout_ratio: float
    base_trade_amount: float
    binary_option_duration: int
    instrument_pool: List[str]
    
@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_consecutive_losses: int
    max_daily_loss: float
    min_balance: float
    min_seconds_between_trades: int
    
@dataclass
class ApiConfig:
    """API configuration"""
    min_interval: float
    max_retries: int
    backoff_base: float
    
@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    enable_logging: bool
    
@dataclass
class StrategyConfig:
    """Strategy configuration"""
    min_confidence_base: float
    scan_interval: int
    strategies_to_evaluate: List[str]
    
@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_health_api: bool
    health_api_port: int
    log_level: str
    log_dir: Path

class Config:
    """Global configuration"""
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.trading = TradingConfig(
            mode=os.getenv('TRADING_MODE', 'demo'),
            min_payout_ratio=float(os.getenv('MIN_PAYOUT_RATIO', '0.65')),
            base_trade_amount=float(os.getenv('BASE_TRADE_AMOUNT', '1.0')),
            binary_option_duration=1,
            instrument_pool=os.getenv('TRADING_ASSETS', 
                'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD').split(',')
        )
        
        self.risk = RiskConfig(
            max_consecutive_losses=int(os.getenv('MAX_CONSECUTIVE_LOSSES', '5')),
            max_daily_loss=float(os.getenv('MAX_DAILY_LOSS', '10.0')),
            min_balance=float(os.getenv('MIN_BALANCE', '50')),
            min_seconds_between_trades=int(os.getenv('MIN_SECONDS_BETWEEN_TRADES', '70'))
        )
        
        self.api = ApiConfig(
            min_interval=float(os.getenv('API_MIN_INTERVAL', '0.3')),
            max_retries=int(os.getenv('API_MAX_RETRIES', '3')),
            backoff_base=1.5
        )
        
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kael'),
            enable_logging=os.getenv('DB_LOGGING_ENABLED', 'true').lower() == 'true'
        )
        
        self.strategy = StrategyConfig(
            min_confidence_base=float(os.getenv('MIN_CONFIDENCE_BASE', '0.70')),
            scan_interval=int(os.getenv('STRATEGY_SCAN_INTERVAL', '5')),
            strategies_to_evaluate=[
                'enhanced_candle_count',
                'rsi_divergence',
                'macd_momentum',
                'bollinger_rsi_combo',
                'stochastic',
                'support_resistance',
                'trend_alignment'
            ]
        )
        
        self.monitoring = MonitoringConfig(
            enable_health_api=bool(os.getenv('ENABLE_HEALTH_API', True)),
            health_api_port=int(os.getenv('HEALTH_API_PORT', '5001')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_dir=Path('logs')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'trading': self.trading.__dict__,
            'risk': self.risk.__dict__,
            'api': self.api.__dict__,
            'database': self.database.__dict__,
            'strategy': self.strategy.__dict__,
            'monitoring': {
                **self.monitoring.__dict__,
                'log_dir': str(self.monitoring.log_dir)
            }
        }

# Global config instance
config = Config()