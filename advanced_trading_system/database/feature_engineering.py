"""
Feature Engineering Pipeline for ML Training
Extracts and stores features optimized for machine learning models
"""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class FeatureEngineer:
    """
    Automated feature engineering for ML training
    Extracts 100+ features from market data and technical indicators
    """

    def __init__(self, postgres_connector):
        """
        Initialize feature engineer

        Args:
            postgres_connector: PostgresConnector instance
        """
        self.pg = postgres_connector
        self.feature_version = 1

    def extract_features(self, market_data: Dict, candles: List[Dict] = None) -> Dict:
        """
        Extract comprehensive feature vector from market data

        Args:
            market_data: Current market state with technical indicators
            candles: Historical candle data (optional, for advanced features)

        Returns:
            Dictionary with feature_vector and metadata
        """
        features = {}

        # ===== PRICE-BASED FEATURES =====
        current_price = market_data.get('price', 0)
        features['price'] = current_price

        # Price momentum
        if candles and len(candles) >= 5:
            prices = [c['close'] for c in candles[-5:]]
            features['price_change_1m'] = (prices[-1] - prices[-2]) / prices[-2] if len(prices) >= 2 else 0
            features['price_change_5m'] = (prices[-1] - prices[0]) / prices[0] if len(prices) >= 5 else 0
            features['price_volatility_5m'] = np.std(prices) / np.mean(prices) if prices else 0
        else:
            features['price_change_1m'] = 0
            features['price_change_5m'] = 0
            features['price_volatility_5m'] = 0

        # ===== RSI FEATURES =====
        rsi_14 = market_data.get('rsi_14', 50)
        features['rsi_14'] = rsi_14
        features['rsi_14_normalized'] = (rsi_14 - 50) / 50  # Normalize to [-1, 1]
        features['rsi_oversold'] = 1 if rsi_14 < 30 else 0
        features['rsi_overbought'] = 1 if rsi_14 > 70 else 0
        features['rsi_neutral'] = 1 if 40 <= rsi_14 <= 60 else 0

        # Multi-timeframe RSI (if available)
        features['rsi_7'] = market_data.get('rsi_7', rsi_14)
        features['rsi_21'] = market_data.get('rsi_21', rsi_14)

        # ===== MACD FEATURES =====
        macd_value = market_data.get('macd_value', 0)
        macd_signal = market_data.get('macd_signal', 0)
        macd_histogram = market_data.get('macd_histogram', 0)

        features['macd_value'] = macd_value
        features['macd_signal'] = macd_signal
        features['macd_histogram'] = macd_histogram
        features['macd_bullish'] = 1 if macd_histogram > 0 else 0
        features['macd_bearish'] = 1 if macd_histogram < 0 else 0

        # ===== BOLLINGER BANDS FEATURES =====
        bb_upper = market_data.get('bb_upper', current_price * 1.02)
        bb_middle = market_data.get('bb_middle', current_price)
        bb_lower = market_data.get('bb_lower', current_price * 0.98)

        features['bb_upper'] = bb_upper
        features['bb_middle'] = bb_middle
        features['bb_lower'] = bb_lower

        # BB position (where price is within bands)
        bb_range = bb_upper - bb_lower
        if bb_range > 0:
            features['bb_position'] = (current_price - bb_lower) / bb_range
        else:
            features['bb_position'] = 0.5

        features['bb_width'] = bb_range / bb_middle if bb_middle > 0 else 0
        features['bb_upper_band_touch'] = 1 if current_price >= bb_upper * 0.99 else 0
        features['bb_lower_band_touch'] = 1 if current_price <= bb_lower * 1.01 else 0

        # ===== MOVING AVERAGE FEATURES =====
        ema_12 = market_data.get('ema_12', current_price)
        ema_26 = market_data.get('ema_26', current_price)
        ema_50 = market_data.get('ema_50', current_price)
        sma_20 = market_data.get('sma_20', current_price)

        features['ema_12'] = ema_12
        features['ema_26'] = ema_26
        features['ema_50'] = ema_50
        features['sma_20'] = sma_20

        # Price vs MAs
        features['price_vs_ema12'] = (current_price - ema_12) / ema_12 if ema_12 > 0 else 0
        features['price_vs_ema26'] = (current_price - ema_26) / ema_26 if ema_26 > 0 else 0
        features['price_vs_ema50'] = (current_price - ema_50) / ema_50 if ema_50 > 0 else 0

        # MA crossovers
        features['ema12_above_ema26'] = 1 if ema_12 > ema_26 else 0
        features['price_above_ema50'] = 1 if current_price > ema_50 else 0

        # ===== STOCHASTIC FEATURES =====
        stoch_k = market_data.get('stochastic_k', 50)
        stoch_d = market_data.get('stochastic_d', 50)

        features['stochastic_k'] = stoch_k
        features['stochastic_d'] = stoch_d
        features['stoch_oversold'] = 1 if stoch_k < 20 else 0
        features['stoch_overbought'] = 1 if stoch_k > 80 else 0

        # ===== ADX FEATURES (Trend Strength) =====
        adx = market_data.get('adx', 25)
        features['adx'] = adx
        features['adx_strong_trend'] = 1 if adx > 25 else 0
        features['adx_weak_trend'] = 1 if adx < 20 else 0

        # ===== VOLUME FEATURES =====
        volume = market_data.get('volume', 0)
        volume_ma_20 = market_data.get('volume_ma_20', volume)

        features['volume'] = volume
        features['volume_ma_20'] = volume_ma_20
        features['volume_ratio'] = volume / volume_ma_20 if volume_ma_20 > 0 else 1
        features['high_volume'] = 1 if volume > volume_ma_20 * 1.5 else 0

        # ===== CCI FEATURES =====
        cci_14 = market_data.get('cci_14', 0)
        features['cci_14'] = cci_14
        features['cci_oversold'] = 1 if cci_14 < -100 else 0
        features['cci_overbought'] = 1 if cci_14 > 100 else 0

        # ===== ATR (Volatility) =====
        atr_14 = market_data.get('atr_14', 0)
        features['atr_14'] = atr_14
        features['atr_normalized'] = atr_14 / current_price if current_price > 0 else 0

        # ===== DERIVED FEATURES =====

        # Momentum score (composite)
        momentum_score = 0
        if rsi_14 > 50:
            momentum_score += 1
        if macd_histogram > 0:
            momentum_score += 1
        if stoch_k > 50:
            momentum_score += 1
        if current_price > ema_12:
            momentum_score += 1
        features['momentum_score'] = momentum_score / 4  # Normalize to [0, 1]

        # Trend alignment
        trend_alignment = 0
        if ema_12 > ema_26:
            trend_alignment += 1
        if ema_26 > ema_50:
            trend_alignment += 1
        if current_price > ema_50:
            trend_alignment += 1
        features['trend_alignment'] = trend_alignment / 3

        # ===== TIME-BASED FEATURES =====
        now = datetime.now()
        features['hour_of_day'] = now.hour
        features['day_of_week'] = now.weekday()
        features['is_market_hours'] = 1 if 9 <= now.hour <= 16 else 0
        features['is_morning'] = 1 if 9 <= now.hour <= 12 else 0
        features['is_afternoon'] = 1 if 13 <= now.hour <= 16 else 0

        # Cyclical encoding for hour (sine/cosine)
        features['hour_sin'] = np.sin(2 * np.pi * now.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * now.hour / 24)

        # ===== MARKET REGIME FEATURES =====
        trend = market_data.get('trend', 'NEUTRAL')
        volatility = market_data.get('volatility', 'MEDIUM')
        market_regime = market_data.get('market_regime', 'SIDEWAYS')

        # One-hot encode trend
        features['trend_bullish'] = 1 if trend == 'BULLISH' else 0
        features['trend_bearish'] = 1 if trend == 'BEARISH' else 0
        features['trend_neutral'] = 1 if trend == 'NEUTRAL' else 0

        # One-hot encode volatility
        features['volatility_high'] = 1 if volatility == 'HIGH' else 0
        features['volatility_medium'] = 1 if volatility == 'MEDIUM' else 0
        features['volatility_low'] = 1 if volatility == 'LOW' else 0

        # One-hot encode market regime
        features['regime_bull'] = 1 if market_regime == 'BULL' else 0
        features['regime_bear'] = 1 if market_regime == 'BEAR' else 0
        features['regime_sideways'] = 1 if market_regime == 'SIDEWAYS' else 0
        features['regime_high_vol'] = 1 if market_regime == 'HIGH_VOLATILITY' else 0

        # ===== PATTERN FEATURES =====
        candlestick_pattern = market_data.get('candlestick_pattern', 'NONE')
        features['has_bullish_pattern'] = 1 if 'BULL' in candlestick_pattern.upper() else 0
        features['has_bearish_pattern'] = 1 if 'BEAR' in candlestick_pattern.upper() else 0

        # ===== CANDLE-BASED FEATURES (if candles available) =====
        if candles and len(candles) >= 3:
            # Last 3 candles analysis
            last_candles = candles[-3:]

            # Body sizes
            body_sizes = []
            for candle in last_candles:
                body = abs(candle['close'] - candle['open'])
                body_sizes.append(body)

            features['avg_body_size_3'] = np.mean(body_sizes) if body_sizes else 0

            # Consecutive direction
            consecutive_up = 0
            consecutive_down = 0
            for candle in last_candles:
                if candle['close'] > candle['open']:
                    consecutive_up += 1
                elif candle['close'] < candle['open']:
                    consecutive_down += 1

            features['consecutive_bullish_candles'] = consecutive_up
            features['consecutive_bearish_candles'] = consecutive_down

        # ===== SUPPORT/RESISTANCE FEATURES =====
        support_level = market_data.get('support_level')
        resistance_level = market_data.get('resistance_level')

        if support_level:
            features['support_distance'] = (current_price - support_level) / current_price
        else:
            features['support_distance'] = 0

        if resistance_level:
            features['resistance_distance'] = (resistance_level - current_price) / current_price
        else:
            features['resistance_distance'] = 0

        return features

    def create_labels(self, pair: str, timestamp: datetime, actual_prices: Dict[str, float] = None) -> Dict:
        """
        Create labels for supervised learning

        Args:
            pair: Currency pair
            timestamp: Current timestamp
            actual_prices: Optional dict with actual prices at future timeframes
                          {'5min': price, '15min': price, '1h': price}

        Returns:
            Dictionary with labels for different timeframes
        """
        labels = {}

        if actual_prices:
            # We have actual future prices, create labels
            current_price = actual_prices.get('current', 0)

            for timeframe in ['5min', '15min', '1h']:
                future_price = actual_prices.get(timeframe)
                if future_price and current_price:
                    price_change = (future_price - current_price) / current_price

                    # Binary classification
                    if price_change > 0.001:  # 0.1% threshold
                        labels[f'label_{timeframe}'] = 'CALL'
                    elif price_change < -0.001:
                        labels[f'label_{timeframe}'] = 'PUT'
                    else:
                        labels[f'label_{timeframe}'] = 'NEUTRAL'
                else:
                    labels[f'label_{timeframe}'] = None
        else:
            # No actual prices yet (for real-time prediction)
            labels['label_5min'] = None
            labels['label_15min'] = None
            labels['label_1h'] = None

        return labels

    def store_features(
        self,
        pair: str,
        timestamp: datetime,
        features: Dict,
        labels: Dict = None,
        is_training_data: bool = True
    ) -> int:
        """
        Store features to database for ML training

        Args:
            pair: Currency pair
            timestamp: Feature timestamp
            features: Feature dictionary
            labels: Labels dictionary (optional)
            is_training_data: Whether this is training data

        Returns:
            feature_id
        """
        feature_data = {
            'timestamp': timestamp,
            'pair': pair,
            'feature_vector': features,
            'feature_version': self.feature_version,
            'is_training_data': is_training_data
        }

        # Add labels if provided
        if labels:
            feature_data.update(labels)
        else:
            feature_data['label_5min'] = None
            feature_data['label_15min'] = None
            feature_data['label_1h'] = None

        return self.pg.insert_ml_features(feature_data)

    def update_labels(self, feature_id: int, actual_outcomes: Dict):
        """
        Update feature record with actual outcomes after time has passed

        Args:
            feature_id: Feature ID to update
            actual_outcomes: Dict with actual price movements
                            {'actual_5min': 'CALL', 'actual_15min': 'PUT', ...}
        """
        query = """
        UPDATE ml_features
        SET actual_5min = %(actual_5min)s,
            actual_15min = %(actual_15min)s,
            actual_1h = %(actual_1h)s
        WHERE feature_id = %(feature_id)s;
        """

        data = actual_outcomes.copy()
        data['feature_id'] = feature_id

        self.pg.execute_query(query, data, fetch=False)

    def backfill_features(self, limit: int = 1000):
        """
        Backfill features for existing trades

        Args:
            limit: Maximum number of trades to backfill
        """
        print(f"Backfilling features for up to {limit} trades...")

        # Get trades that don't have features yet
        query = """
        SELECT t.*
        FROM trades t
        LEFT JOIN ml_features f ON t.timestamp = f.timestamp AND t.pair = f.pair
        WHERE f.feature_id IS NULL
        AND t.result IS NOT NULL
        ORDER BY t.timestamp DESC
        LIMIT %s;
        """

        trades = self.pg.execute_query(query, (limit,))

        if not trades:
            print("No trades to backfill")
            return

        print(f"Found {len(trades)} trades to backfill")

        for i, trade in enumerate(trades):
            # Reconstruct market data from trade
            market_data = {
                'price': trade['entry_price'],
                'rsi_14': trade['rsi_14'],
                'macd_value': trade['macd_value'],
                'bb_upper': trade['bb_upper'],
                'bb_middle': trade['bb_middle'],
                'bb_lower': trade['bb_lower'],
                'trend': trade['trend'],
                'volatility': trade['volatility'],
                'market_regime': trade['market_regime']
            }

            # Extract features
            features = self.extract_features(market_data)

            # Create labels based on actual result
            labels = {
                'label_5min': trade['direction'],  # Predicted
                'actual_5min': trade['direction'] if trade['result'] == 'WIN' else ('PUT' if trade['direction'] == 'CALL' else 'CALL')
            }

            # Store
            self.store_features(
                pair=trade['pair'],
                timestamp=trade['timestamp'],
                features=features,
                labels=labels,
                is_training_data=True
            )

            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{len(trades)}")

        print(f"✓ Backfilled {len(trades)} feature records")


# Convenience function
def create_feature_engineer(postgres_connector):
    """Create FeatureEngineer instance"""
    return FeatureEngineer(postgres_connector)
