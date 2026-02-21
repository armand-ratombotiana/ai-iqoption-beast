import time
import logging
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from utils.error_handling import (
    with_circuit_breaker,
    with_timeout,
    retry_with_backoff,
    ApiError
)

class ApiClient:
    """Enhanced wrapper for IQ Option API with robust error handling"""

    def __init__(self, email: str, password: str, mode: str = 'demo',
                 min_interval: float = 0.3, max_retries: int = 3,
                 backoff_base: float = 1.5):
        self.logger = logging.getLogger('ApiClient')
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.last_call = 0
        self.api = IQ_Option(email, password)
        self.mode = mode
        
        # Connection status
        self._is_connected = False
        self._last_check = 0
        self._check_interval = 30  # Check connection every 30 seconds
        
        # Initialize connection
        self.connect()
        
    def connect(self) -> bool:
        """Connect to IQ Option API"""
        try:
            self.logger.info(f"Connecting to IQ Option...")
            check, reason = retry_with_backoff(self.api.connect)
            
            if not check:
                raise ApiError(f"Connection failed: {reason}")
                
            # Set trading mode
            if self.mode == 'live':
                self.api.change_balance('REAL')
                self.logger.warning("⚠️ LIVE MODE ENABLED")
            else:
                self.api.change_balance('PRACTICE')
                self.logger.info("Demo mode enabled")
                
            self._is_connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self._is_connected = False
            raise ApiError(f"Failed to connect: {str(e)}")
            
    def _ensure_connected(self):
        """Ensure API is connected, reconnect if needed"""
        current_time = time.time()
        
        # Check connection periodically
        if current_time - self._last_check > self._check_interval:
            self._last_check = current_time
            
            try:
                if not self.api.check_connect():
                    self.logger.warning("Connection lost, reconnecting...")
                    self.connect()
            except Exception as e:
                self.logger.error(f"Connection check failed: {e}")
                self._is_connected = False
                raise ApiError("Connection check failed")
                
    def _rate_limit(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
        
    @with_circuit_breaker(max_failures=3, reset_timeout=300)
    @with_timeout(seconds=10)
    def get_balance(self) -> float:
        """Get account balance"""
        self._ensure_connected()
        self._rate_limit()
        return retry_with_backoff(self.api.get_balance)
        
    @with_circuit_breaker(max_failures=3, reset_timeout=300)
    @with_timeout(seconds=10)
    def get_candles(self, instrument: str, size: int, count: int,
                    timestamp: int) -> Optional[list]:
        """Get candle data"""
        self._ensure_connected()
        self._rate_limit()
        
        candles = retry_with_backoff(
            self.api.get_candles,
            instrument, size, count, timestamp
        )
        
        if not candles or len(candles) < count // 2:
            raise ApiError(f"Invalid candle data for {instrument}")
            
        return candles
        
    @with_circuit_breaker(max_failures=3, reset_timeout=300)
    @with_timeout(seconds=10)
    def get_all_profit(self) -> Dict[str, Any]:
        """Get profit for all assets"""
        self._ensure_connected()
        self._rate_limit()
        return retry_with_backoff(self.api.get_all_profit)
        
    @with_circuit_breaker(max_failures=3, reset_timeout=300)
    @with_timeout(seconds=15)
    def buy(self, amount: float, instrument: str,
            action: str, duration: int) -> Tuple[bool, str]:
        """Place a trade"""
        self._ensure_connected()
        self._rate_limit()
        
        # Validate parameters
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if action not in ['call', 'put']:
            raise ValueError("Action must be 'call' or 'put'")
        if duration <= 0:
            raise ValueError("Duration must be positive")
            
        # Place order with retry
        success, order_id = retry_with_backoff(
            self.api.buy,
            amount, instrument, action, duration
        )
        
        if not success:
            raise ApiError(f"Order failed for {instrument}")
            
        return success, order_id
        
    @with_circuit_breaker(max_failures=3, reset_timeout=300)
    @with_timeout(seconds=10)
    def check_win_v3(self, order_id: str) -> Optional[float]:
        """Check trade result"""
        self._ensure_connected()
        self._rate_limit()
        return retry_with_backoff(self.api.check_win_v3, order_id)
        
    @with_circuit_breaker(max_failures=3, reset_timeout=300)
    def get_all_open_time(self) -> Dict[str, Any]:
        """Get all open markets"""
        self._ensure_connected()
        self._rate_limit()
        return retry_with_backoff(self.api.get_all_open_time)
        
    def get_server_timestamp(self) -> int:
        """Get server timestamp"""
        return self.api.get_server_timestamp()
        
    def close(self):
        """Close API connection"""
        try:
            if hasattr(self.api, 'close'):
                self.api.close()
            self._is_connected = False
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")