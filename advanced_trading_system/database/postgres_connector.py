"""
PostgreSQL/TimescaleDB Connection Manager
Handles database connections with pooling and advanced features
"""
import os
import psycopg2
from psycopg2 import pool, extras
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import json
from datetime import datetime


class PostgresConnector:
    """PostgreSQL connection manager with pooling"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize PostgreSQL connector

        Args:
            config: Database configuration dict, or None to use env vars
        """
        if config:
            self.config = config
        else:
            self.config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'database': os.getenv('POSTGRES_DB', 'trading_db'),
                'user': os.getenv('POSTGRES_USER', 'trading_user'),
                'password': os.getenv('POSTGRES_PASSWORD', 'your_password')
            }

        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Create connection pool"""
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                # Performance settings
                options='-c statement_timeout=30000'  # 30s timeout
            )
            print(f"✓ PostgreSQL connection pool initialized ({self.config['host']}:{self.config['port']})")
        except Exception as e:
            print(f"✗ Failed to create connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections

        Usage:
            with connector.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM trades")
        """
        conn = self.connection_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.connection_pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List]:
        """
        Execute a query and return results

        Args:
            query: SQL query string
            params: Query parameters (for prepared statements)
            fetch: Whether to fetch results

        Returns:
            List of tuples if fetch=True, None otherwise
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                return None

    def execute_many(self, query: str, data: List[tuple]):
        """
        Execute batch insert/update

        Args:
            query: SQL query with placeholders
            data: List of tuples with data
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                extras.execute_batch(cur, query, data, page_size=100)

    def insert_trade(self, trade_data: Dict) -> int:
        """
        Insert trade into database

        Args:
            trade_data: Dictionary with trade details

        Returns:
            trade_id of inserted trade
        """
        query = """
        INSERT INTO trades (
            timestamp, pair, direction, amount, duration, result, profit,
            entry_price, exit_price, ai_signal_confidence, ai_model_agreement, ai_models_count,
            rsi_14, rsi_7, rsi_21, macd_value, macd_signal, macd_histogram,
            bb_upper, bb_middle, bb_lower, bb_position, bb_width,
            ema_12, ema_26, ema_50, ema_200, sma_20, sma_50, sma_200,
            atr_14, stochastic_k, stochastic_d, adx, cci_14, williams_r_14,
            volume, volume_ma_20, obv, mfi,
            trend, trend_strength, volatility, volatility_value,
            support_level, resistance_level, candlestick_pattern,
            hour_of_day, day_of_week, market_session, market_regime, regime_confidence,
            strategy_version, model_version, notes
        ) VALUES (
            %(timestamp)s, %(pair)s, %(direction)s, %(amount)s, %(duration)s, %(result)s, %(profit)s,
            %(entry_price)s, %(exit_price)s, %(ai_signal_confidence)s, %(ai_model_agreement)s, %(ai_models_count)s,
            %(rsi_14)s, %(rsi_7)s, %(rsi_21)s, %(macd_value)s, %(macd_signal)s, %(macd_histogram)s,
            %(bb_upper)s, %(bb_middle)s, %(bb_lower)s, %(bb_position)s, %(bb_width)s,
            %(ema_12)s, %(ema_26)s, %(ema_50)s, %(ema_200)s, %(sma_20)s, %(sma_50)s, %(sma_200)s,
            %(atr_14)s, %(stochastic_k)s, %(stochastic_d)s, %(adx)s, %(cci_14)s, %(williams_r_14)s,
            %(volume)s, %(volume_ma_20)s, %(obv)s, %(mfi)s,
            %(trend)s, %(trend_strength)s, %(volatility)s, %(volatility_value)s,
            %(support_level)s, %(resistance_level)s, %(candlestick_pattern)s,
            %(hour_of_day)s, %(day_of_week)s, %(market_session)s, %(market_regime)s, %(regime_confidence)s,
            %(strategy_version)s, %(model_version)s, %(notes)s
        ) RETURNING trade_id;
        """

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, trade_data)
                trade_id = cur.fetchone()[0]
                return trade_id

    def insert_ai_prediction(self, prediction_data: Dict) -> int:
        """
        Insert AI model prediction

        Args:
            prediction_data: Prediction details including model_id, signal, confidence

        Returns:
            prediction_id
        """
        query = """
        INSERT INTO ai_predictions (
            timestamp, trade_id, model_id, signal, confidence, reasoning,
            feature_importance, inference_time_ms, tokens_used, cost
        ) VALUES (
            %(timestamp)s, %(trade_id)s, %(model_id)s, %(signal)s, %(confidence)s, %(reasoning)s,
            %(feature_importance)s, %(inference_time_ms)s, %(tokens_used)s, %(cost)s
        ) RETURNING prediction_id;
        """

        # Convert feature_importance dict to JSON
        if 'feature_importance' in prediction_data and prediction_data['feature_importance']:
            prediction_data['feature_importance'] = json.dumps(prediction_data['feature_importance'])

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, prediction_data)
                prediction_id = cur.fetchone()[0]
                return prediction_id

    def update_trade_result(self, trade_id: int, result: str, profit: float, exit_price: float):
        """
        Update trade with final result

        Args:
            trade_id: ID of trade to update
            result: WIN or LOSS
            profit: Profit/loss amount
            exit_price: Exit price
        """
        query = """
        UPDATE trades
        SET result = %s, profit = %s, exit_price = %s, updated_at = NOW()
        WHERE trade_id = %s;
        """
        self.execute_query(query, (result, profit, exit_price, trade_id), fetch=False)

    def get_model_performance(self, model_id: int, days: int = 7) -> Dict:
        """
        Get model performance stats

        Args:
            model_id: Model ID
            days: Number of days to look back

        Returns:
            Performance statistics dict
        """
        query = """
        SELECT
            COUNT(*) as total_predictions,
            SUM(CASE WHEN was_correct = TRUE THEN 1 ELSE 0 END) as correct,
            ROUND(AVG(CASE WHEN was_correct = TRUE THEN 100.0 ELSE 0.0 END), 2) as accuracy,
            ROUND(AVG(confidence), 2) as avg_confidence,
            SUM(cost) as total_cost
        FROM ai_predictions
        WHERE model_id = %s
        AND timestamp > NOW() - INTERVAL '%s days'
        GROUP BY model_id;
        """

        result = self.execute_query(query, (model_id, days))
        if result:
            return dict(result[0])
        return {}

    def get_winning_patterns(self, min_occurrences: int = 5, min_win_rate: float = 60.0) -> List[Dict]:
        """
        Find winning patterns from materialized view

        Args:
            min_occurrences: Minimum number of trades
            min_win_rate: Minimum win rate %

        Returns:
            List of winning patterns
        """
        query = """
        SELECT *
        FROM mv_winning_patterns
        WHERE trades >= %s
        AND win_rate >= %s
        ORDER BY win_rate DESC, avg_profit DESC
        LIMIT 50;
        """

        results = self.execute_query(query, (min_occurrences, min_win_rate))
        return [dict(row) for row in results] if results else []

    def insert_ml_features(self, feature_data: Dict) -> int:
        """
        Insert ML features for training

        Args:
            feature_data: Feature vector and labels

        Returns:
            feature_id
        """
        query = """
        INSERT INTO ml_features (
            timestamp, pair, feature_vector,
            label_5min, label_15min, label_1h,
            feature_version, is_training_data
        ) VALUES (
            %(timestamp)s, %(pair)s, %(feature_vector)s,
            %(label_5min)s, %(label_15min)s, %(label_1h)s,
            %(feature_version)s, %(is_training_data)s
        ) RETURNING feature_id;
        """

        # Convert feature vector to JSON
        if 'feature_vector' in feature_data:
            feature_data['feature_vector'] = json.dumps(feature_data['feature_vector'])

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, feature_data)
                feature_id = cur.fetchone()[0]
                return feature_id

    def get_training_data(self, pair: str = None, limit: int = 10000) -> List[Dict]:
        """
        Get ML training data

        Args:
            pair: Currency pair filter (optional)
            limit: Maximum records to return

        Returns:
            List of feature records
        """
        query = """
        SELECT
            timestamp, pair, feature_vector,
            label_5min, label_15min, label_1h,
            actual_5min, actual_15min, actual_1h
        FROM ml_features
        WHERE is_training_data = TRUE
        """

        if pair:
            query += " AND pair = %s"
            params = (pair,)
        else:
            params = None

        query += f" ORDER BY timestamp DESC LIMIT {limit};"

        results = self.execute_query(query, params)

        # Parse JSON feature vectors
        if results:
            for row in results:
                if row['feature_vector']:
                    row['feature_vector'] = json.loads(row['feature_vector'])

        return [dict(row) for row in results] if results else []

    def refresh_materialized_views(self):
        """Refresh all materialized views"""
        views = ['mv_model_performance_realtime', 'mv_winning_patterns']

        for view in views:
            query = f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view};"
            try:
                self.execute_query(query, fetch=False)
                print(f"✓ Refreshed {view}")
            except Exception as e:
                print(f"✗ Failed to refresh {view}: {e}")

    def get_recent_trades(self, limit: int = 100, pair: str = None) -> List[Dict]:
        """
        Get recent trades

        Args:
            limit: Number of trades to return
            pair: Currency pair filter (optional)

        Returns:
            List of trade records
        """
        query = """
        SELECT
            trade_id, timestamp, pair, direction, amount, duration,
            result, profit, entry_price, exit_price,
            ai_signal_confidence, ai_model_agreement,
            market_regime, trend, volatility
        FROM trades
        """

        if pair:
            query += " WHERE pair = %s"
            params = (pair,)
        else:
            params = None

        query += f" ORDER BY timestamp DESC LIMIT {limit};"

        results = self.execute_query(query, params)
        return [dict(row) for row in results] if results else []

    def close(self):
        """Close all connections in pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ PostgreSQL connection pool closed")


# Convenience function for creating connector
def create_connector(config: Optional[Dict] = None) -> PostgresConnector:
    """
    Create and return PostgresConnector instance

    Args:
        config: Optional database configuration

    Returns:
        PostgresConnector instance
    """
    return PostgresConnector(config)
