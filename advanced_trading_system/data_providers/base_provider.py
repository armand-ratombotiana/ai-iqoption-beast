"""
Base Data Provider Interface
Abstract base class for all market data providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio


class BaseDataProvider(ABC):
    """Abstract base class for market data providers"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.is_connected = False
        self.last_error = None
        self.connection_retries = 0
        self.max_retries = 3

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
    async def get_candles(self, pair: str, timeframe: str, count: int) -> List[Dict]:
        """Get historical candles"""
        pass

    @abstractmethod
    async def get_available_pairs(self) -> List[str]:
        """Get list of available trading pairs"""
        pass

    @abstractmethod
    def is_market_open(self, pair: str) -> bool:
        """Check if market is open for trading"""
        pass

    async def health_check(self) -> Dict:
        """Check provider health status"""
        try:
            # Try to get a simple price quote
            test_pair = "EURUSD-OTC"  # Common pair for testing
            price = await self.get_current_price(test_pair)
            
            return {
                'provider': self.provider_name,
                'status': 'healthy' if price is not None else 'unhealthy',
                'connected': self.is_connected,
                'last_error': self.last_error,
                'test_price': price,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'provider': self.provider_name,
                'status': 'error',
                'connected': False,
                'last_error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def retry_connection(self) -> bool:
        """Retry connection with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                if await self.connect():
                    self.connection_retries = 0
                    return True
                
                # Exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                self.last_error = str(e)
                self.connection_retries += 1
                
        return False

    def get_provider_info(self) -> Dict:
        """Get provider information"""
        return {
            'name': self.provider_name,
            'connected': self.is_connected,
            'last_error': self.last_error,
            'connection_retries': self.connection_retries
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


class DataProviderError(Exception):
    """Custom exception for data provider errors"""
    
    def __init__(self, provider: str, message: str, original_error: Exception = None):
        self.provider = provider
        self.message = message
        self.original_error = original_error
        super().__init__(f"{provider}: {message}")


class ConnectionError(DataProviderError):
    """Connection-related errors"""
    pass


class DataError(DataProviderError):
    """Data-related errors"""
    pass


class RateLimitError(DataProviderError):
    """Rate limiting errors"""
    pass