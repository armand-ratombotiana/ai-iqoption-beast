"""
API Rate Limiter and Connection Resilience Module
Protects against API throttling and connection failures
"""

import time
import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
import functools

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API calls
    Prevents hitting IQ Option API rate limits
    """

    def __init__(self, max_calls: int = 10, time_window: int = 1):
        """
        Initialize rate limiter

        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque(maxlen=max_calls)
        self.lock = threading.Lock()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()

            # Remove calls outside the time window
            while self.calls and self.calls[0] < now - self.time_window:
                self.calls.popleft()

            # If at limit, wait until oldest call expires
            if len(self.calls) >= self.max_calls:
                sleep_time = self.calls[0] + self.time_window - now
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, waiting {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    # Remove expired call
                    self.calls.popleft()

            # Record this call
            self.calls.append(time.time())


class ConnectionResilience:
    """
    Exponential backoff and retry logic for API connections
    Handles connection failures gracefully
    """

    def __init__(self,
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0):
        """
        Initialize connection resilience

        Args:
            max_retries: Maximum retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.consecutive_failures = 0
        self.last_failure_time = None

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for current attempt using exponential backoff"""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        return delay

    def execute_with_retry(self,
                          func: Callable,
                          *args,
                          **kwargs) -> Any:
        """
        Execute function with exponential backoff retry

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                # Success - reset failure count
                self.consecutive_failures = 0
                return result

            except Exception as e:
                last_exception = e
                self.consecutive_failures += 1
                self.last_failure_time = datetime.now()

                if attempt < self.max_retries - 1:
                    delay = self.get_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries} attempts failed. Last error: {e}"
                    )

        raise last_exception


class APIRateLimitedCall:
    """
    Decorator/wrapper for rate-limited API calls with retry logic
    Combines rate limiting and connection resilience
    """

    def __init__(self,
                 rate_limiter: Optional[RateLimiter] = None,
                 resilience: Optional[ConnectionResilience] = None):
        """
        Initialize API call wrapper

        Args:
            rate_limiter: RateLimiter instance (creates default if None)
            resilience: ConnectionResilience instance (creates default if None)
        """
        self.rate_limiter = rate_limiter or RateLimiter(max_calls=10, time_window=1)
        self.resilience = resilience or ConnectionResilience(max_retries=3)

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap API calls"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Wait if rate limit would be exceeded
            self.rate_limiter.wait_if_needed()

            # Execute with retry logic
            return self.resilience.execute_with_retry(func, *args, **kwargs)

        return wrapper


# Global rate limiter instances for different API endpoints
class IQOptionRateLimiters:
    """Pre-configured rate limiters for IQ Option API"""

    # Trading operations (conservative - 5 calls per second)
    TRADING = RateLimiter(max_calls=5, time_window=1)

    # Market data (moderate - 10 calls per second)
    MARKET_DATA = RateLimiter(max_calls=10, time_window=1)

    # Account info (relaxed - 2 calls per second)
    ACCOUNT = RateLimiter(max_calls=2, time_window=1)

    # Connection operations (very conservative - 1 call per 5 seconds)
    CONNECTION = RateLimiter(max_calls=1, time_window=5)


# Example usage decorators
trading_call = APIRateLimitedCall(
    rate_limiter=IQOptionRateLimiters.TRADING,
    resilience=ConnectionResilience(max_retries=3)
)

market_data_call = APIRateLimitedCall(
    rate_limiter=IQOptionRateLimiters.MARKET_DATA,
    resilience=ConnectionResilience(max_retries=2)
)

account_call = APIRateLimitedCall(
    rate_limiter=IQOptionRateLimiters.ACCOUNT,
    resilience=ConnectionResilience(max_retries=3)
)


class ConnectionHealthMonitor:
    """
    Monitors API connection health and tracks failures
    Helps detect when to back off or reconnect
    """

    def __init__(self, failure_threshold: int = 5, time_window: int = 60):
        """
        Initialize health monitor

        Args:
            failure_threshold: Number of failures before considering unhealthy
            time_window: Time window in seconds to track failures
        """
        self.failure_threshold = failure_threshold
        self.time_window = time_window
        self.failures = deque(maxlen=100)
        self.successes = deque(maxlen=100)

    def record_success(self):
        """Record successful API call"""
        self.successes.append(datetime.now())

    def record_failure(self):
        """Record failed API call"""
        self.failures.append(datetime.now())

    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        # Count recent failures
        recent_failures = sum(1 for f in self.failures if f > cutoff)

        return recent_failures < self.failure_threshold

    def get_failure_rate(self) -> float:
        """Get current failure rate (0.0 to 1.0)"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        recent_failures = sum(1 for f in self.failures if f > cutoff)
        recent_successes = sum(1 for s in self.successes if s > cutoff)

        total = recent_failures + recent_successes
        if total == 0:
            return 0.0

        return recent_failures / total

    def should_backoff(self) -> bool:
        """Determine if we should back off from API calls"""
        return self.get_failure_rate() > 0.5  # More than 50% failures

    def get_stats(self) -> dict:
        """Get connection health statistics"""
        return {
            "is_healthy": self.is_healthy(),
            "failure_rate": self.get_failure_rate(),
            "should_backoff": self.should_backoff(),
            "recent_failures": len([f for f in self.failures
                                   if f > datetime.now() - timedelta(seconds=self.time_window)]),
            "recent_successes": len([s for s in self.successes
                                    if s > datetime.now() - timedelta(seconds=self.time_window)])
        }


import threading  # Import at module level

# Global connection health monitor
connection_health = ConnectionHealthMonitor()
