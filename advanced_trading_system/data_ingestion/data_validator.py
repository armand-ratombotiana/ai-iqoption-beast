"""
Data Validator
Validates and sanitizes market data
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataValidator:
    """
    Validates market data for quality and completeness
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate_candles(self, candles: List[Dict], min_count: int = 20) -> bool:
        """
        Validate candle data

        Args:
            candles: List of candle dictionaries
            min_count: Minimum required candles

        Returns:
            True if valid, False otherwise
        """
        if not candles:
            self.logger.warning("No candles provided")
            return False

        if len(candles) < min_count:
            self.logger.warning(
                f"Insufficient candles: {len(candles)} < {min_count}"
            )
            return False

        # Validate each candle has required fields
        required_fields = ['open', 'high', 'low', 'close']

        for i, candle in enumerate(candles):
            for field in required_fields:
                if field not in candle:
                    self.logger.error(
                        f"Candle {i} missing required field: {field}"
                    )
                    return False

                # Check for valid numeric values
                try:
                    value = float(candle[field])
                    if value <= 0:
                        self.logger.error(
                            f"Candle {i} has invalid {field}: {value}"
                        )
                        return False
                except (ValueError, TypeError):
                    self.logger.error(
                        f"Candle {i} has non-numeric {field}: {candle[field]}"
                    )
                    return False

            # Validate OHLC relationships
            if not self._validate_ohlc(candle):
                self.logger.error(f"Candle {i} has invalid OHLC relationships")
                return False

        return True

    def _validate_ohlc(self, candle: Dict) -> bool:
        """
        Validate OHLC relationships (high >= low, etc.)

        Args:
            candle: Candle dictionary

        Returns:
            True if valid, False otherwise
        """
        try:
            high = float(candle['high'])
            low = float(candle['low'])
            open_price = float(candle['open'])
            close = float(candle['close'])

            # High must be >= all other prices
            if high < low or high < open_price or high < close:
                return False

            # Low must be <= all other prices
            if low > high or low > open_price or low > close:
                return False

            return True

        except (KeyError, ValueError, TypeError):
            return False

    def validate_market_data(self, market_data: Dict) -> bool:
        """
        Validate complete market data dictionary

        Args:
            market_data: Market data dictionary

        Returns:
            True if valid, False otherwise
        """
        if not market_data:
            self.logger.warning("Empty market data")
            return False

        # Required fields
        required_fields = ['pair', 'current_price', 'timestamp']

        for field in required_fields:
            if field not in market_data:
                self.logger.error(f"Missing required field: {field}")
                return False

        # Validate price
        try:
            price = float(market_data['current_price'])
            if price <= 0:
                self.logger.error(f"Invalid price: {price}")
                return False
        except (ValueError, TypeError):
            self.logger.error(
                f"Non-numeric price: {market_data['current_price']}"
            )
            return False

        # Validate timestamp
        try:
            datetime.fromisoformat(market_data['timestamp'])
        except (ValueError, TypeError):
            self.logger.error(
                f"Invalid timestamp: {market_data['timestamp']}"
            )
            return False

        return True

    def validate_indicator(self, name: str, value: Any,
                          min_val: Optional[float] = None,
                          max_val: Optional[float] = None) -> bool:
        """
        Validate technical indicator value

        Args:
            name: Indicator name
            value: Indicator value
            min_val: Minimum valid value
            max_val: Maximum valid value

        Returns:
            True if valid, False otherwise
        """
        try:
            numeric_value = float(value)

            if min_val is not None and numeric_value < min_val:
                self.logger.warning(
                    f"{name} below minimum: {numeric_value} < {min_val}"
                )
                return False

            if max_val is not None and numeric_value > max_val:
                self.logger.warning(
                    f"{name} above maximum: {numeric_value} > {max_val}"
                )
                return False

            return True

        except (ValueError, TypeError):
            self.logger.error(f"{name} is not numeric: {value}")
            return False

    def sanitize_candles(self, candles: List[Dict]) -> List[Dict]:
        """
        Sanitize candle data by removing invalid entries

        Args:
            candles: List of candle dictionaries

        Returns:
            List of valid candles
        """
        sanitized = []

        for candle in candles:
            if self._validate_ohlc(candle):
                # Ensure all required fields exist
                sanitized_candle = {
                    'open': float(candle.get('open', 0)),
                    'high': float(candle.get('high', 0)),
                    'low': float(candle.get('low', 0)),
                    'close': float(candle.get('close', 0)),
                    'volume': float(candle.get('volume', 0)),
                    'time': candle.get('time', 0)
                }
                sanitized.append(sanitized_candle)

        if len(sanitized) < len(candles):
            self.logger.warning(
                f"Removed {len(candles) - len(sanitized)} invalid candles"
            )

        return sanitized

    def check_data_quality(self, candles: List[Dict]) -> Dict[str, Any]:
        """
        Assess overall data quality

        Args:
            candles: List of candle dictionaries

        Returns:
            Dictionary with quality metrics
        """
        if not candles:
            return {
                'quality_score': 0,
                'issues': ['No data'],
                'valid': False
            }

        issues = []
        quality_score = 100

        # Check for gaps in data
        if len(candles) < 50:
            issues.append('Insufficient data points')
            quality_score -= 20

        # Check for zero volumes
        zero_volumes = sum(1 for c in candles if c.get('volume', 0) == 0)
        if zero_volumes > len(candles) * 0.5:
            issues.append('High percentage of zero volumes')
            quality_score -= 15

        # Check for price anomalies (extreme spikes)
        prices = [c['close'] for c in candles]
        avg_price = sum(prices) / len(prices)

        anomalies = 0
        for price in prices:
            if abs(price - avg_price) > avg_price * 0.1:  # 10% deviation
                anomalies += 1

        if anomalies > len(prices) * 0.1:
            issues.append('High number of price anomalies')
            quality_score -= 10

        # Check for duplicate timestamps
        timestamps = [c.get('time', 0) for c in candles]
        if len(timestamps) != len(set(timestamps)):
            issues.append('Duplicate timestamps detected')
            quality_score -= 15

        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'valid': quality_score >= 70,
            'total_candles': len(candles),
            'zero_volumes': zero_volumes,
            'anomalies': anomalies
        }
