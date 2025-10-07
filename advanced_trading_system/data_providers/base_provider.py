"""
Base Data Provider Interface
Abstract base class for all data providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class DataProviderError(Exception):
    """Custom exception for data provider errors"""
    def __init__(self, provider_name: str, message: str):
        self.provider_name = provider_name
        self.message = message
        super().__init__(f"{provider_name}: {message}")


class BaseDataProvider(ABC):
    """Abstract base class for data providers"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.is_connected = False
        self.last_error = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the data provider"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the data provider"""
        pass
    
    @abstractmethod
    async def get_current_price(self, pair: str) -> Optional[float]:
        """Get current price for a trading pair"""
        pass
    
    @abstractmethod
    async def get_candles(self, pair: str, timeframe: str = '1m', count: int = 100) -> Optional[List[Dict]]:
        """Get historical candles for a trading pair"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict:
        """Check provider health status"""
        pass
    
    def get_provider_info(self) -> Dict:
        """Get provider information"""
        return {
            'name': self.provider_name,
            'connected': self.is_connected,
            'last_error': self.last_error,
            'timestamp': datetime.now().isoformat()
        }