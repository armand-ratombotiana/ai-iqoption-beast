import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

T = TypeVar('T')

class TradingError(Exception):
    """Base exception for trading errors"""
    pass

class ApiError(TradingError):
    """API related errors"""
    pass

class StrategyError(TradingError):
    """Strategy related errors"""
    pass

class DatabaseError(TradingError):
    """Database related errors"""
    pass

def with_circuit_breaker(max_failures: int = 3, reset_timeout: int = 300):
    """Circuit breaker decorator"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        failures = 0
        last_failure_time = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            nonlocal failures, last_failure_time
            
            # Check if circuit is open
            if failures >= max_failures:
                if time.time() - last_failure_time < reset_timeout:
                    raise TradingError(f"Circuit breaker open for {func.__name__}")
                failures = 0  # Reset after timeout
                
            try:
                result = func(*args, **kwargs)
                failures = 0  # Reset on success
                return result
            except Exception as e:
                failures += 1
                last_failure_time = time.time()
                logging.error(f"Circuit breaker: {func.__name__} failed {failures} times")
                raise
                
        return wrapper
    return decorator

def with_timeout(seconds: int):
    """Timeout decorator"""
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            import signal
            
            def handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set timeout
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Restore old handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                
            return result
        return wrapper
    return decorator

@retry(stop=stop_after_attempt(3), 
       wait=wait_exponential(multiplier=1, min=4, max=10))
def retry_with_backoff(func: Callable[..., T], *args, **kwargs) -> T:
    """Retry function with exponential backoff"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.warning(f"Retry failed for {func.__name__}: {str(e)}")
        raise

def safe_execute(func: Callable[..., T], default: Any = None, 
                log_error: bool = True) -> Optional[T]:
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        if log_error:
            logging.error(f"Error executing {func.__name__}: {str(e)}")
        return default