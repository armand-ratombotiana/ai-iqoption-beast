"""
Multi-Data Provider System
Aggregates data from multiple providers for robustness and consensus pricing
"""
import asyncio
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import aioredis
import json

from .base_provider import BaseDataProvider, DataProviderError


class MultiDataProvider:
    """
    Manages multiple data providers and provides consensus data
    Features:
    - Consensus pricing from multiple sources
    - Automatic failover
    - Data quality monitoring
    - Caching with Redis
    - Provider health monitoring
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.providers: Dict[str, BaseDataProvider] = {}
        self.provider_weights: Dict[str, float] = {}
        self.provider_health: Dict[str, Dict] = {}
        self.redis_url = redis_url
        self.redis = None
        self.cache_ttl = 5  # Cache for 5 seconds
        self.min_providers_for_consensus = 2

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            print("✅ Redis connection established")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.redis = None

    async def add_provider(self, provider: BaseDataProvider, weight: float = 1.0):
        """Add a data provider with specified weight"""
        self.providers[provider.provider_name] = provider
        self.provider_weights[provider.provider_name] = weight
        
        # Initialize health status
        self.provider_health[provider.provider_name] = {
            'status': 'unknown',
            'last_check': None,
            'error_count': 0,
            'success_count': 0
        }
        
        print(f"✅ Added provider: {provider.provider_name} (weight: {weight})")

    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all providers"""
        connection_results = {}
        
        # Connect to all providers concurrently
        tasks = []
        for name, provider in self.providers.items():
            tasks.append(self._connect_provider(name, provider))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (name, _) in enumerate(self.providers.items()):
            if isinstance(results[i], Exception):
                connection_results[name] = False
                print(f"❌ Failed to connect to {name}: {results[i]}")
            else:
                connection_results[name] = results[i]
                status = "✅" if results[i] else "❌"
                print(f"{status} {name} connection: {results[i]}")
        
        return connection_results

    async def _connect_provider(self, name: str, provider: BaseDataProvider) -> bool:
        """Connect to a single provider"""
        try:
            success = await provider.connect()
            self._update_provider_health(name, success, None)
            return success
        except Exception as e:
            self._update_provider_health(name, False, str(e))
            return False

    async def disconnect_all(self):
        """Disconnect from all providers"""
        tasks = []
        for provider in self.providers.values():
            tasks.append(provider.disconnect())
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        if self.redis:
            await self.redis.close()

    async def get_consensus_price(self, pair: str) -> Optional[Dict]:
        """
        Get consensus price from multiple providers
        
        Returns:
        {
            'price': float,
            'confidence': float,
            'sources': int,
            'spread': float,
            'providers': Dict[str, float]
        }
        """
        # Check cache first
        cached_price = await self._get_cached_price(pair)
        if cached_price:
            return cached_price

        # Get prices from all available providers
        price_tasks = []
        for name, provider in self.providers.items():
            if provider.is_connected:
                price_tasks.append(self._get_provider_price(name, provider, pair))

        if not price_tasks:
            return None

        # Execute all price requests concurrently
        price_results = await asyncio.gather(*price_tasks, return_exceptions=True)

        # Process results
        valid_prices = {}
        for i, (name, _) in enumerate([(n, p) for n, p in self.providers.items() if p.is_connected]):
            result = price_results[i]
            if isinstance(result, Exception):
                self._update_provider_health(name, False, str(result))
            elif result is not None:
                valid_prices[name] = result
                self._update_provider_health(name, True, None)

        if len(valid_prices) < self.min_providers_for_consensus:
            return None

        # Calculate consensus
        consensus = self._calculate_price_consensus(valid_prices)
        
        # Cache the result
        await self._cache_price(pair, consensus)
        
        return consensus

    async def _get_provider_price(self, name: str, provider: BaseDataProvider, pair: str) -> Optional[float]:
        """Get price from a single provider with timeout"""
        try:
            # Set timeout for each provider
            price = await asyncio.wait_for(provider.get_current_price(pair), timeout=3.0)
            return price
        except asyncio.TimeoutError:
            raise DataProviderError(name, "Timeout getting price")
        except Exception as e:
            raise DataProviderError(name, f"Error getting price: {str(e)}")

    def _calculate_price_consensus(self, prices: Dict[str, float]) -> Dict:
        """Calculate weighted consensus price"""
        if not prices:
            return None

        # Apply weights
        weighted_prices = []
        total_weight = 0
        
        for provider_name, price in prices.items():
            weight = self.provider_weights.get(provider_name, 1.0)
            
            # Adjust weight based on provider health
            health = self.provider_health.get(provider_name, {})
            success_rate = self._calculate_success_rate(health)
            adjusted_weight = weight * success_rate
            
            weighted_prices.extend([price] * int(adjusted_weight * 10))  # Scale for integer weights
            total_weight += adjusted_weight

        if not weighted_prices:
            return None

        # Calculate statistics
        consensus_price = statistics.median(weighted_prices)  # Use median for robustness
        price_values = list(prices.values())
        
        spread = max(price_values) - min(price_values)
        std_dev = np.std(price_values)
        
        # Calculate confidence based on agreement
        # Higher agreement (lower spread/std) = higher confidence
        max_allowed_spread = consensus_price * 0.001  # 0.1% of price
        confidence = max(0.5, 1.0 - (spread / max_allowed_spread)) if max_allowed_spread > 0 else 0.5
        confidence = min(1.0, confidence)

        return {
            'price': round(consensus_price, 6),
            'confidence': round(confidence, 3),
            'sources': len(prices),
            'spread': round(spread, 6),
            'std_dev': round(std_dev, 6),
            'providers': prices,
            'timestamp': datetime.now().isoformat()
        }

    async def get_consensus_candles(self, pair: str, timeframe: str = '1m', count: int = 100) -> Optional[List[Dict]]:
        """Get consensus candles from multiple providers"""
        # Get candles from all available providers
        candle_tasks = []
        for name, provider in self.providers.items():
            if provider.is_connected:
                candle_tasks.append(self._get_provider_candles(name, provider, pair, timeframe, count))

        if not candle_tasks:
            return None

        candle_results = await asyncio.gather(*candle_tasks, return_exceptions=True)

        # Process results
        valid_candles = {}
        for i, (name, _) in enumerate([(n, p) for n, p in self.providers.items() if p.is_connected]):
            result = candle_results[i]
            if isinstance(result, Exception):
                self._update_provider_health(name, False, str(result))
            elif result:
                valid_candles[name] = result
                self._update_provider_health(name, True, None)

        if not valid_candles:
            return None

        # For now, return candles from the most reliable provider
        # In future, could implement candle consensus
        best_provider = max(
            valid_candles.keys(),
            key=lambda p: self._calculate_success_rate(self.provider_health.get(p, {}))
        )
        
        return valid_candles[best_provider]

    async def _get_provider_candles(self, name: str, provider: BaseDataProvider, 
                                   pair: str, timeframe: str, count: int) -> Optional[List[Dict]]:
        """Get candles from a single provider with timeout"""
        try:
            candles = await asyncio.wait_for(
                provider.get_candles(pair, timeframe, count), 
                timeout=10.0
            )
            return candles
        except asyncio.TimeoutError:
            raise DataProviderError(name, "Timeout getting candles")
        except Exception as e:
            raise DataProviderError(name, f"Error getting candles: {str(e)}")

    async def health_check_all(self) -> Dict[str, Dict]:
        """Check health of all providers"""
        health_tasks = []
        for name, provider in self.providers.items():
            health_tasks.append(self._check_provider_health(name, provider))

        health_results = await asyncio.gather(*health_tasks, return_exceptions=True)

        all_health = {}
        for i, (name, _) in enumerate(self.providers.items()):
            if isinstance(health_results[i], Exception):
                all_health[name] = {
                    'status': 'error',
                    'error': str(health_results[i]),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                all_health[name] = health_results[i]

        return all_health

    async def _check_provider_health(self, name: str, provider: BaseDataProvider) -> Dict:
        """Check health of a single provider"""
        try:
            health = await provider.health_check()
            self._update_provider_health(name, health['status'] == 'healthy', health.get('last_error'))
            return health
        except Exception as e:
            self._update_provider_health(name, False, str(e))
            return {
                'provider': name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _update_provider_health(self, name: str, success: bool, error: Optional[str]):
        """Update provider health statistics"""
        if name not in self.provider_health:
            self.provider_health[name] = {
                'status': 'unknown',
                'last_check': None,
                'error_count': 0,
                'success_count': 0
            }

        health = self.provider_health[name]
        health['last_check'] = datetime.now().isoformat()
        
        if success:
            health['success_count'] += 1
            health['status'] = 'healthy'
        else:
            health['error_count'] += 1
            health['status'] = 'unhealthy'
            health['last_error'] = error

    def _calculate_success_rate(self, health: Dict) -> float:
        """Calculate success rate for a provider"""
        total = health.get('success_count', 0) + health.get('error_count', 0)
        if total == 0:
            return 0.5  # Default for new providers
        
        return health.get('success_count', 0) / total

    async def _get_cached_price(self, pair: str) -> Optional[Dict]:
        """Get cached price from Redis"""
        if not self.redis:
            return None

        try:
            cached = await self.redis.get(f"price:{pair}")
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        
        return None

    async def _cache_price(self, pair: str, consensus: Dict):
        """Cache price in Redis"""
        if not self.redis:
            return

        try:
            await self.redis.setex(
                f"price:{pair}",
                self.cache_ttl,
                json.dumps(consensus)
            )
        except Exception:
            pass

    def get_provider_summary(self) -> Dict:
        """Get summary of all providers"""
        summary = {
            'total_providers': len(self.providers),
            'connected_providers': sum(1 for p in self.providers.values() if p.is_connected),
            'providers': {}
        }

        for name, provider in self.providers.items():
            health = self.provider_health.get(name, {})
            summary['providers'][name] = {
                'connected': provider.is_connected,
                'weight': self.provider_weights.get(name, 1.0),
                'success_rate': self._calculate_success_rate(health),
                'status': health.get('status', 'unknown'),
                'last_check': health.get('last_check')
            }

        return summary

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        await self.connect_all()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect_all()