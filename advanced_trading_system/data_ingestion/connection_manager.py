"""
Connection Manager
Handles IQOption API connections with retry logic and health monitoring
"""
import time
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta


class ConnectionManager:
    """
    Manages IQOption API connections with:
    - Automatic reconnection
    - Connection pooling
    - Health monitoring
    - Retry logic with exponential backoff
    """

    def __init__(self, email: str, password: str, account_type: str = 'demo',
                 max_retries: int = 5, retry_delay: int = 10):
        """
        Initialize connection manager

        Args:
            email: IQOption account email
            password: IQOption account password
            account_type: 'demo' or 'real'
            max_retries: Maximum connection retry attempts
            retry_delay: Initial delay between retries (seconds)
        """
        self.email = email
        self.password = password
        # Map account_type to IQ Option format: demo -> PRACTICE, real -> REAL
        if account_type.lower() == 'demo':
            self.account_type = 'PRACTICE'
        elif account_type.lower() == 'real':
            self.account_type = 'REAL'
        else:
            self.account_type = account_type.upper()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.api = None
        self.connected = False
        self.last_connection_time = None
        self.connection_attempts = 0
        self.total_reconnections = 0

        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self, force_reconnect: bool = False) -> Tuple[bool, str]:
        """
        Establish connection to IQOption API

        Args:
            force_reconnect: Force new connection even if already connected

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check if already connected
        if self.connected and self.api and not force_reconnect:
            if self._verify_connection():
                return True, "Already connected"

        # Import here to avoid circular dependencies
        try:
            from iqoptionapi.stable_api import IQ_Option
        except ImportError:
            return False, "IQOption API not installed"

        # Attempt connection with retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Connection attempt {attempt}/{self.max_retries}...")
                self.connection_attempts += 1

                # Create new API instance
                self.api = IQ_Option(self.email, self.password)

                # Connect
                check, reason = self.api.connect()

                if not check:
                    raise ConnectionError(f"Connection failed: {reason}")

                # Set account type
                self.api.change_balance(self.account_type)
                time.sleep(1)

                # Verify connection by getting balance
                balance = self.api.get_balance()
                if balance is None:
                    raise ConnectionError("Could not retrieve balance")

                # Connection successful
                self.connected = True
                self.last_connection_time = datetime.now()

                if force_reconnect:
                    self.total_reconnections += 1

                self.logger.info(
                    f"✅ Connected - {self.account_type} - Balance: ${balance:.2f}"
                )

                return True, f"Connected successfully (Balance: ${balance:.2f})"

            except Exception as e:
                self.logger.error(f"Connection attempt {attempt} failed: {e}")
                self.connected = False

                if attempt < self.max_retries:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    error_msg = f"Max retries ({self.max_retries}) reached"
                    self.logger.error(error_msg)
                    return False, error_msg

        return False, "Connection failed"

    def disconnect(self):
        """Safely disconnect from API"""
        try:
            if self.api:
                self.api.close()
                self.logger.info("Disconnected from IQOption API")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
        finally:
            self.connected = False
            self.api = None

    def _verify_connection(self) -> bool:
        """
        Verify connection is still alive

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            if not self.api:
                return False

            # Try to get balance as health check
            balance = self.api.get_balance()
            return balance is not None

        except Exception as e:
            self.logger.warning(f"Connection verification failed: {e}")
            return False

    def ensure_connected(self) -> bool:
        """
        Ensure connection is active, reconnect if necessary

        Returns:
            True if connected, False otherwise
        """
        if not self.connected or not self._verify_connection():
            self.logger.warning("Connection lost, attempting to reconnect...")
            success, _ = self.connect(force_reconnect=True)
            return success

        return True

    def get_api(self):
        """
        Get API instance, ensuring connection is active

        Returns:
            IQ_Option API instance or None
        """
        if self.ensure_connected():
            return self.api
        return None

    def is_connected(self) -> bool:
        """
        Check if currently connected

        Returns:
            True if connected, False otherwise
        """
        return self.connected and self.api is not None

    def get_balance(self) -> float:
        """
        Get account balance

        Returns:
            Account balance or None
        """
        if self.ensure_connected():
            try:
                return self.api.get_balance()
            except Exception as e:
                self.logger.error(f"Error getting balance: {e}")
        return None

    def get_connection_stats(self) -> dict:
        """
        Get connection statistics

        Returns:
            Dictionary with connection stats
        """
        uptime = None
        if self.last_connection_time:
            uptime = (datetime.now() - self.last_connection_time).total_seconds()

        return {
            'connected': self.connected,
            'account_type': self.account_type,
            'connection_attempts': self.connection_attempts,
            'total_reconnections': self.total_reconnections,
            'last_connection_time': self.last_connection_time.isoformat() if self.last_connection_time else None,
            'uptime_seconds': uptime
        }

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
