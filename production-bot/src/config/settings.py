"""
Configuration Management System
Industry-standard configuration with validation and type safety
"""

import os
from dataclasses import dataclass, field
from typing import List
from pathlib import Path


@dataclass
class TradingConfig:
    """Trading configuration with validation"""

    # Account Credentials
    iqoption_email: str = field(default_factory=lambda: os.getenv('IQOPTION_EMAIL', ''))
    iqoption_password: str = field(default_factory=lambda: os.getenv('IQOPTION_PASSWORD', ''))

    # Trading Mode
    trading_mode: str = field(default_factory=lambda: os.getenv('TRADING_MODE', 'demo'))

    # Binary Options Settings
    binary_option_duration: int = 1  # minutes
    default_trade_amount: float = field(default_factory=lambda: float(os.getenv('BASE_TRADE_AMOUNT', '1.0')))
    min_trade_amount: float = 1.0
    max_trade_amount: float = field(default_factory=lambda: float(os.getenv('MAX_TRADE_AMOUNT', '10.0')))

    # Preferred Assets
    preferred_assets: List[str] = field(default_factory=lambda:
        os.getenv('TRADING_ASSETS', 'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD').split(',')
    )

    # Risk Management
    max_daily_loss: float = field(default_factory=lambda: float(os.getenv('MAX_DAILY_LOSS', '50')))
    max_daily_profit: float = field(default_factory=lambda: float(os.getenv('MAX_DAILY_PROFIT', '100')))
    max_consecutive_losses: int = field(default_factory=lambda: int(os.getenv('MAX_CONSECUTIVE_LOSSES', '5')))
    min_balance: float = field(default_factory=lambda: float(os.getenv('MIN_BALANCE', '50')))
    max_trades_per_hour: int = field(default_factory=lambda: int(os.getenv('MAX_TRADES_PER_HOUR', '30')))
    max_trades_per_day: int = field(default_factory=lambda: int(os.getenv('MAX_TRADES_PER_DAY', '200')))
    max_risk_per_trade_percent: float = 5.0  # Maximum 5% of balance per trade

    # Martingale Strategy
    enable_martingale: bool = field(default_factory=lambda: os.getenv('ENABLE_MARTINGALE', 'true').lower() == 'true')
    martingale_multiplier: float = field(default_factory=lambda: float(os.getenv('MARTINGALE_MULTIPLIER', '1.5')))
    max_martingale_level: int = field(default_factory=lambda: int(os.getenv('MAX_MARTINGALE_LEVEL', '3')))

    # AI Settings
    min_ai_confidence: int = field(default_factory=lambda: int(os.getenv('MIN_AI_CONFIDENCE', '65')))
    min_consensus_agreement: float = field(default_factory=lambda: float(os.getenv('MIN_CONSENSUS_AGREEMENT', '0.7')))
    enable_technical_analysis: bool = True
    enable_sentiment_analysis: bool = field(default_factory=lambda: os.getenv('ENABLE_SENTIMENT', 'false').lower() == 'true')

    # Timing
    min_seconds_between_trades: int = 70
    wait_for_result_seconds: int = 80
    max_retry_attempts: int = 3
    connection_check_interval: int = 300  # 5 minutes

    # Data Ingestion
    candle_count: int = 100  # Number of candles to fetch for analysis
    candle_size: int = 60  # 1 minute candles
    enable_data_caching: bool = True
    cache_expiry_seconds: int = 300

    # Auto-Recovery
    auto_restart_on_error: bool = True
    max_restart_attempts: int = 100
    restart_delay_seconds: int = 60

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    log_dir: Path = Path('logs')
    enable_trade_log: bool = True
    enable_debug_log: bool = True

    # Monitoring
    enable_health_api: bool = True
    health_api_port: int = field(default_factory=lambda: int(os.getenv('HEALTH_API_PORT', '5001')))
    enable_metrics: bool = True

    # Emergency Controls
    enable_emergency_stop: bool = True
    emergency_stop_file: Path = Path('EMERGENCY_STOP')

    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()

    def validate(self):
        """Validate all configuration values"""
        errors = []

        # Validate credentials
        if not self.iqoption_email:
            errors.append("IQOPTION_EMAIL is required")
        if not self.iqoption_password:
            errors.append("IQOPTION_PASSWORD is required")

        # Validate trading mode
        if self.trading_mode not in ['demo', 'live']:
            errors.append(f"Invalid trading_mode: {self.trading_mode}. Must be 'demo' or 'live'")

        # Validate amounts
        if self.default_trade_amount < self.min_trade_amount:
            errors.append(f"default_trade_amount ({self.default_trade_amount}) < min_trade_amount ({self.min_trade_amount})")
        if self.max_trade_amount < self.default_trade_amount:
            errors.append(f"max_trade_amount ({self.max_trade_amount}) < default_trade_amount ({self.default_trade_amount})")

        # Validate risk limits
        if self.max_daily_loss <= 0:
            errors.append(f"max_daily_loss must be positive, got {self.max_daily_loss}")
        if self.max_daily_profit <= 0:
            errors.append(f"max_daily_profit must be positive, got {self.max_daily_profit}")
        if self.max_consecutive_losses < 1:
            errors.append(f"max_consecutive_losses must be >= 1, got {self.max_consecutive_losses}")

        # Validate AI settings
        if not (0 <= self.min_ai_confidence <= 100):
            errors.append(f"min_ai_confidence must be 0-100, got {self.min_ai_confidence}")
        if not (0.0 <= self.min_consensus_agreement <= 1.0):
            errors.append(f"min_consensus_agreement must be 0.0-1.0, got {self.min_consensus_agreement}")

        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log_level: {self.log_level}. Must be one of {valid_log_levels}")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    def is_demo_mode(self) -> bool:
        """Check if running in demo mode"""
        return self.trading_mode.lower() == 'demo'

    def is_live_mode(self) -> bool:
        """Check if running in live mode"""
        return self.trading_mode.lower() == 'live'

    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            'trading_mode': self.trading_mode,
            'binary_option_duration': self.binary_option_duration,
            'default_trade_amount': self.default_trade_amount,
            'max_daily_loss': self.max_daily_loss,
            'max_daily_profit': self.max_daily_profit,
            'max_consecutive_losses': self.max_consecutive_losses,
            'preferred_assets': self.preferred_assets,
            'enable_martingale': self.enable_martingale,
            'min_ai_confidence': self.min_ai_confidence,
            'enable_technical_analysis': self.enable_technical_analysis,
            'enable_health_api': self.enable_health_api,
            'log_level': self.log_level
        }

    def __repr__(self) -> str:
        """String representation (hide sensitive data)"""
        return (
            f"TradingConfig(\n"
            f"  mode={self.trading_mode},\n"
            f"  email={'***' if self.iqoption_email else 'NOT SET'},\n"
            f"  trade_amount=${self.default_trade_amount},\n"
            f"  max_daily_loss=${self.max_daily_loss},\n"
            f"  martingale={self.enable_martingale}\n"
            f")"
        )


# Global configuration instance
_config = None


def get_config() -> TradingConfig:
    """Get global configuration instance (singleton)"""
    global _config
    if _config is None:
        _config = TradingConfig()
    return _config


def reload_config() -> TradingConfig:
    """Reload configuration from environment"""
    global _config
    _config = TradingConfig()
    return _config
