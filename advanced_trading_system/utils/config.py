"""Configuration management"""

import os
from typing import Dict, Any


class Config:
    """Application configuration"""

    # Default values
    DEFAULTS = {
        'MAX_DAILY_LOSS': 50.0,
        'MAX_DAILY_PROFIT': 100.0,
        'MAX_CONSECUTIVE_LOSSES': 3,
        'MIN_BALANCE': 50.0,
        'MARTINGALE_MULTIPLIER': 1.5,
        'MAX_MARTINGALE_LEVEL': 4,
        'MIN_CONFIDENCE_THRESHOLD': 60,
        'BASE_TRADE_AMOUNT': 1.0,
        'MAX_TRADE_MULTIPLIER': 5.0,
    }

    def __init__(self):
        self._config = {}
        self.load_from_env()

    def load_from_env(self):
        """Load configuration from environment variables"""
        for key, default in self.DEFAULTS.items():
            env_value = os.getenv(key)
            if env_value is not None:
                # Convert to appropriate type
                if isinstance(default, float):
                    self._config[key] = float(env_value)
                elif isinstance(default, int):
                    self._config[key] = int(env_value)
                else:
                    self._config[key] = env_value
            else:
                self._config[key] = default

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value

    def to_dict(self) -> Dict:
        """Get all configuration as dictionary"""
        return self._config.copy()

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access"""
        return self._config[key]

    def __setitem__(self, key: str, value: Any):
        """Allow dict-like setting"""
        self._config[key] = value

    def display(self):
        """Display configuration"""
        print(f"\n{'='*60}")
        print("IQOption AI Trading Bot - Configuration")
        print(f"{'='*60}")
        for key, value in self._config.items():
            print(f"  {key}: {value}")
        print(f"{'='*60}\n")
