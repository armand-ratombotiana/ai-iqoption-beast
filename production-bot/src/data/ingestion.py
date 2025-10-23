"""
Data Ingestion Module
Fetches and processes market data for AI analysis
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np


logger = logging.getLogger(__name__)


@dataclass
class CandleData:
    """Single candle/bar data"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }


@dataclass
class MarketData:
    """Aggregated market data for an asset"""
    asset: str
    candles: List[CandleData]
    fetch_time: datetime
    timeframe: int  # seconds

    def get_closes(self) -> List[float]:
        """Get list of closing prices"""
        return [c.close for c in self.candles]

    def get_highs(self) -> List[float]:
        """Get list of high prices"""
        return [c.high for c in self.candles]

    def get_lows(self) -> List[float]:
        """Get list of low prices"""
        return [c.low for c in self.candles]

    def get_volumes(self) -> List[float]:
        """Get list of volumes"""
        return [c.volume for c in self.candles]

    def get_latest_price(self) -> float:
        """Get most recent closing price"""
        return self.candles[-1].close if self.candles else 0.0

    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """Check if data is too old"""
        age = (datetime.now() - self.fetch_time).total_seconds()
        return age > max_age_seconds


class DataIngestionEngine:
    """
    Handles all data ingestion from IQ Option API
    Provides clean, validated market data for AI models
    """

    def __init__(self, api, config):
        """
        Initialize data ingestion engine

        Args:
            api: IQ_Option API instance
            config: TradingConfig instance
        """
        self.api = api
        self.config = config
        self.cache: Dict[str, MarketData] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_candles(self, asset: str, count: int = 100, timeframe: int = 60) -> Optional[List[CandleData]]:
        """
        Fetch historical candle data from IQ Option

        Args:
            asset: Asset name (e.g., 'EURUSD')
            count: Number of candles to fetch
            timeframe: Candle size in seconds (default: 60 = 1 minute)

        Returns:
            List of CandleData or None if failed
        """
        try:
            self.logger.debug(f"Fetching {count} candles for {asset} (timeframe={timeframe}s)")

            # Get candles from API
            self.api.start_candles_stream(asset, timeframe, count)
            time.sleep(2)  # Wait for data to arrive

            candles_data = self.api.get_realtime_candles(asset, timeframe)

            if not candles_data:
                self.logger.warning(f"No candle data received for {asset}")
                return None

            # Convert to CandleData objects
            candles = []
            for timestamp, data in sorted(candles_data.items()):
                try:
                    candle = CandleData(
                        timestamp=int(timestamp),
                        open=float(data.get('open', 0)),
                        high=float(data.get('max', 0)),
                        low=float(data.get('min', 0)),
                        close=float(data.get('close', 0)),
                        volume=float(data.get('volume', 0))
                    )
                    candles.append(candle)
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Skipping invalid candle data: {e}")
                    continue

            self.logger.info(f"Successfully fetched {len(candles)} candles for {asset}")
            return candles

        except Exception as e:
            self.logger.error(f"Error fetching candles for {asset}: {e}")
            return None

        finally:
            # Stop candle stream
            try:
                self.api.stop_candles_stream(asset, timeframe)
            except:
                pass

    def get_market_data(self, asset: str, use_cache: bool = True) -> Optional[MarketData]:
        """
        Get comprehensive market data for an asset

        Args:
            asset: Asset name
            use_cache: Use cached data if available and fresh

        Returns:
            MarketData object or None
        """
        # Check cache
        if use_cache and asset in self.cache:
            cached = self.cache[asset]
            if not cached.is_stale(self.config.cache_expiry_seconds):
                self.logger.debug(f"Using cached data for {asset}")
                return cached

        # Fetch fresh data
        candles = self.fetch_candles(
            asset,
            count=self.config.candle_count,
            timeframe=self.config.candle_size
        )

        if not candles:
            return None

        market_data = MarketData(
            asset=asset,
            candles=candles,
            fetch_time=datetime.now(),
            timeframe=self.config.candle_size
        )

        # Update cache
        if self.config.enable_data_caching:
            self.cache[asset] = market_data

        return market_data

    def get_current_price(self, asset: str) -> Optional[float]:
        """
        Get current/latest price for an asset

        Args:
            asset: Asset name

        Returns:
            Current price or None
        """
        try:
            # Try to get from real-time data
            data = self.api.get_realtime_candles(asset, self.config.candle_size)
            if data:
                latest = max(data.keys())
                return float(data[latest].get('close', 0))

            # Fallback to market data
            market_data = self.get_market_data(asset)
            if market_data:
                return market_data.get_latest_price()

            return None

        except Exception as e:
            self.logger.error(f"Error getting current price for {asset}: {e}")
            return None

    def get_asset_info(self, asset: str) -> Optional[Dict]:
        """
        Get detailed information about an asset

        Args:
            asset: Asset name

        Returns:
            Dictionary with asset info or None
        """
        try:
            # Get payout information
            all_profit = self.api.get_all_profit()
            asset_profit = all_profit.get(asset, {})

            # Get market status
            open_time = self.api.get_all_open_time()
            binary_markets = open_time.get('binary', {})
            asset_status = binary_markets.get(asset, {})

            info = {
                'asset': asset,
                'is_open': asset_status.get('open', False),
                'binary_payout': asset_profit.get('binary', 0) * 100 if 'binary' in asset_profit else 0,
                'turbo_payout': asset_profit.get('turbo', 0) * 100 if 'turbo' in asset_profit else 0,
            }

            return info

        except Exception as e:
            self.logger.error(f"Error getting asset info for {asset}: {e}")
            return None

    def find_best_assets(self, min_payout: float = 70.0, max_assets: int = 10) -> List[Tuple[str, float]]:
        """
        Find the best available assets based on payout

        Args:
            min_payout: Minimum payout percentage required
            max_assets: Maximum number of assets to return

        Returns:
            List of (asset_name, payout_percent) tuples
        """
        try:
            self.logger.info(f"Finding best assets (min_payout={min_payout}%)")

            # Get all profit data
            all_profit = self.api.get_all_profit()

            # Get market status
            open_time = self.api.get_all_open_time()
            binary_markets = open_time.get('binary', {})

            best_assets = []

            for asset, profit_data in all_profit.items():
                # Check if market is open
                if asset not in binary_markets or not binary_markets[asset].get('open', False):
                    continue

                # Get binary option payout
                if 'binary' not in profit_data:
                    continue

                payout_percent = profit_data['binary'] * 100

                if payout_percent >= min_payout:
                    best_assets.append((asset, payout_percent))

            # Sort by payout (highest first)
            best_assets.sort(key=lambda x: x[1], reverse=True)

            self.logger.info(f"Found {len(best_assets)} assets with >={min_payout}% payout")

            return best_assets[:max_assets]

        except Exception as e:
            self.logger.error(f"Error finding best assets: {e}")
            return []

    def validate_asset_tradeable(self, asset: str) -> Tuple[bool, str]:
        """
        Validate if an asset is currently tradeable

        Args:
            asset: Asset name

        Returns:
            (is_tradeable, reason) tuple
        """
        try:
            info = self.get_asset_info(asset)

            if not info:
                return False, "Could not fetch asset information"

            if not info['is_open']:
                return False, f"Market is closed for {asset}"

            if info['binary_payout'] < 70.0:
                return False, f"Payout too low: {info['binary_payout']:.1f}%"

            return True, "Asset is tradeable"

        except Exception as e:
            return False, f"Validation error: {e}"

    def get_multiple_market_data(self, assets: List[str]) -> Dict[str, MarketData]:
        """
        Get market data for multiple assets efficiently

        Args:
            assets: List of asset names

        Returns:
            Dictionary mapping asset names to MarketData
        """
        results = {}

        for asset in assets:
            try:
                data = self.get_market_data(asset)
                if data:
                    results[asset] = data
            except Exception as e:
                self.logger.warning(f"Failed to get data for {asset}: {e}")
                continue

        return results

    def clear_cache(self):
        """Clear all cached market data"""
        self.cache.clear()
        self.logger.info("Market data cache cleared")

    def get_cache_stats(self) -> Dict:
        """Get statistics about cached data"""
        return {
            'cached_assets': len(self.cache),
            'assets': list(self.cache.keys()),
            'oldest_data': min(
                (data.fetch_time for data in self.cache.values()),
                default=None
            )
        }


def calculate_price_change(candles: List[CandleData], periods: int = 10) -> float:
    """
    Calculate price change percentage over N periods

    Args:
        candles: List of CandleData
        periods: Number of periods to calculate change over

    Returns:
        Price change percentage
    """
    if len(candles) < periods + 1:
        return 0.0

    old_price = candles[-(periods + 1)].close
    new_price = candles[-1].close

    if old_price == 0:
        return 0.0

    return ((new_price - old_price) / old_price) * 100


def calculate_volatility(candles: List[CandleData], periods: int = 20) -> float:
    """
    Calculate price volatility (standard deviation of returns)

    Args:
        candles: List of CandleData
        periods: Number of periods to calculate

    Returns:
        Volatility value
    """
    if len(candles) < periods + 1:
        return 0.0

    closes = [c.close for c in candles[-periods:]]
    returns = []

    for i in range(1, len(closes)):
        if closes[i - 1] != 0:
            ret = (closes[i] - closes[i - 1]) / closes[i - 1]
            returns.append(ret)

    if not returns:
        return 0.0

    return float(np.std(returns)) * 100
