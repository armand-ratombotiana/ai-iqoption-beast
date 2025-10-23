"""
Market Data Provider
High-level interface for retrieving and processing market data
"""
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .connection_manager import ConnectionManager
from .data_validator import DataValidator


class MarketDataProvider:
    """
    Provides clean, validated market data with caching and error handling
    """

    def __init__(self, connection_manager: ConnectionManager,
                 enable_caching: bool = True, cache_ttl: int = 300):
        """
        Initialize market data provider

        Args:
            connection_manager: ConnectionManager instance
            enable_caching: Enable data caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.connection_manager = connection_manager
        self.validator = DataValidator()
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl

        # Cache storage
        self._cache = {}
        self._cache_timestamps = {}

        self.logger = logging.getLogger(self.__class__.__name__)

        # Statistics
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'failed_requests': 0,
            'data_quality_issues': 0
        }

    def get_candles(self, pair: str, timeframe: str = '1m',
                   count: int = 100, use_cache: bool = True) -> Optional[List[Dict]]:
        """
        Get candle data with validation and caching

        Args:
            pair: Trading pair (e.g., 'EURUSD')
            timeframe: Timeframe (e.g., '1m', '5m')
            count: Number of candles to retrieve
            use_cache: Use cached data if available

        Returns:
            List of candle dictionaries or None on failure
        """
        self.stats['total_requests'] += 1

        # Check cache
        if use_cache and self.enable_caching:
            cached_data = self._get_from_cache(pair, timeframe)
            if cached_data:
                self.stats['cache_hits'] += 1
                self.logger.debug(f"Cache hit for {pair} {timeframe}")
                return cached_data

        self.stats['cache_misses'] += 1

        # Get API instance
        api = self.connection_manager.get_api()
        if not api:
            self.logger.error("API not available")
            self.stats['failed_requests'] += 1
            return None

        # Retrieve candles with retry logic
        candles = self._fetch_candles_with_retry(api, pair, timeframe, count)

        if not candles:
            self.stats['failed_requests'] += 1
            return None

        # Validate data
        if not self.validator.validate_candles(candles, min_count=20):
            self.logger.warning(f"Invalid candle data for {pair}")
            self.stats['data_quality_issues'] += 1
            # Try to sanitize
            candles = self.validator.sanitize_candles(candles)
            if not candles:
                return None

        # Check data quality
        quality = self.validator.check_data_quality(candles)
        if not quality['valid']:
            self.logger.warning(
                f"Low quality data for {pair}: {quality['issues']}"
            )
            self.stats['data_quality_issues'] += 1

        # Cache the data
        if self.enable_caching:
            self._add_to_cache(pair, timeframe, candles)

        return candles

    def _fetch_candles_with_retry(self, api, pair: str, timeframe: str,
                                  count: int, max_retries: int = 3) -> Optional[List[Dict]]:
        """
        Fetch candles with retry logic

        Args:
            api: IQ_Option API instance
            pair: Trading pair
            timeframe: Timeframe
            count: Number of candles
            max_retries: Maximum retry attempts

        Returns:
            List of candles or None
        """
        # Convert timeframe to seconds
        timeframe_map = {
            '1m': 60, '5m': 300, '15m': 900, '30m': 1800,
            '1h': 3600, '4h': 14400, '1d': 86400
        }
        timeframe_seconds = timeframe_map.get(timeframe, 60)

        # Remove -OTC suffix for candle streaming
        clean_pair = pair.replace('-OTC', '')

        for attempt in range(1, max_retries + 1):
            try:
                self.logger.debug(
                    f"Fetching candles for {pair} (attempt {attempt}/{max_retries})"
                )

                # Start candles stream
                api.start_candles_stream(clean_pair, timeframe_seconds, count)
                time.sleep(3)  # Wait for data

                # Get realtime candles
                candles_dict = api.get_realtime_candles(clean_pair, timeframe_seconds)

                # Stop stream
                api.stop_candles_stream(clean_pair, timeframe_seconds)

                if not candles_dict:
                    raise ValueError("No candles received")

                # Convert to list format
                candles = []
                for timestamp in sorted(candles_dict.keys()):
                    candle = candles_dict[timestamp]
                    candles.append({
                        'time': timestamp,
                        'open': candle['open'],
                        'high': candle['max'],
                        'low': candle['min'],
                        'close': candle['close'],
                        'volume': candle.get('volume', 0)
                    })

                # Return only requested count
                return candles[-count:]

            except Exception as e:
                self.logger.error(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(2)
                else:
                    self.logger.error(f"Failed to fetch candles after {max_retries} attempts")
                    return None

        return None

    def get_current_price(self, pair: str) -> Optional[float]:
        """
        Get current price for a pair

        Args:
            pair: Trading pair

        Returns:
            Current price or None
        """
        candles = self.get_candles(pair, timeframe='1m', count=1, use_cache=False)
        if candles and len(candles) > 0:
            return candles[-1]['close']
        return None

    def get_market_status(self, pair: str) -> Dict[str, bool]:
        """
        Check if market is open for trading

        Args:
            pair: Trading pair

        Returns:
            Dictionary with binary and digital market status
        """
        api = self.connection_manager.get_api()
        if not api:
            return {'binary': False, 'digital': False}

        try:
            all_assets = api.get_all_open_time()

            if pair in all_assets:
                asset_data = all_assets[pair]
                return {
                    'binary': asset_data.get('binary', {}).get('open', False),
                    'digital': asset_data.get('digital', {}).get('open', False)
                }

        except Exception as e:
            self.logger.error(f"Error checking market status: {e}")

        return {'binary': False, 'digital': False}

    def get_available_assets(self) -> Dict[str, List[str]]:
        """
        Get list of available trading assets

        Returns:
            Dictionary with binary and digital asset lists
        """
        api = self.connection_manager.get_api()
        if not api:
            return {'binary': [], 'digital': []}

        try:
            all_assets = api.get_all_open_time()

            binary_assets = []
            digital_assets = []

            for asset_name, asset_data in all_assets.items():
                if 'binary' in asset_data and asset_data['binary'].get('open'):
                    binary_assets.append(asset_name)
                if 'digital' in asset_data and asset_data['digital'].get('open'):
                    digital_assets.append(asset_name)

            return {
                'binary': binary_assets,
                'digital': digital_assets
            }

        except Exception as e:
            self.logger.error(f"Error getting available assets: {e}")
            return {'binary': [], 'digital': []}

    def _get_from_cache(self, pair: str, timeframe: str) -> Optional[List[Dict]]:
        """Get data from cache if not expired"""
        cache_key = f"{pair}_{timeframe}"

        if cache_key not in self._cache:
            return None

        # Check if cache is expired
        cache_time = self._cache_timestamps.get(cache_key)
        if cache_time:
            age = (datetime.now() - cache_time).total_seconds()
            if age > self.cache_ttl:
                # Cache expired
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
                return None

        return self._cache[cache_key]

    def _add_to_cache(self, pair: str, timeframe: str, data: List[Dict]):
        """Add data to cache"""
        cache_key = f"{pair}_{timeframe}"
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        self.logger.info("Cache cleared")

    def get_statistics(self) -> Dict:
        """
        Get provider statistics

        Returns:
            Dictionary with statistics
        """
        cache_hit_rate = 0
        if self.stats['total_requests'] > 0:
            cache_hit_rate = (
                self.stats['cache_hits'] / self.stats['total_requests'] * 100
            )

        return {
            **self.stats,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_size': len(self._cache)
        }

    def reset_statistics(self):
        """Reset statistics counters"""
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'failed_requests': 0,
            'data_quality_issues': 0
        }
        self.logger.info("Statistics reset")
