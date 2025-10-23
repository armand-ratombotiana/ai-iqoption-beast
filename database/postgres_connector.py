"""
PostgreSQL + TimescaleDB Connector for KAEL Trading System
High-performance time-series database for trade storage and analytics
"""
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool, extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


logger = logging.getLogger(__name__)


class PostgreSQLConnector:
    """
    PostgreSQL connector with connection pooling and TimescaleDB support
    """

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 database: str = None,
                 user: str = None,
                 password: str = None,
                 min_connections: int = 1,
                 max_connections: int = 10):
        """
        Initialize PostgreSQL connector

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database username
            password: Database password
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
        """
        # Load from environment if not provided
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'trading_db')
        self.user = user or os.getenv('DB_USERNAME', 'trading_user')
        self.password = password or os.getenv('DB_PASSWORD', 'trading123')

        self.min_connections = min_connections
        self.max_connections = max_connections

        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=self.min_connections,
                maxconn=self.max_connections,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=extras.RealDictCursor
            )
            logger.info(f"✓ PostgreSQL connection pool initialized ({self.host}:{self.port})")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Get connection from pool (context manager)

        Usage:
            with connector.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT ...")
        """
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)

    def insert_trade(self, trade_data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a trade into the database

        Args:
            trade_data: Dictionary containing trade information

        Returns:
            Trade ID if successful, None otherwise
        """
        query = """
            INSERT INTO trades (
                trade_id, timestamp, asset, direction, amount, duration,
                entry_price, exit_price, payout_rate, result, profit_loss,
                ai_signal_confidence, ai_consensus_score, ai_models_agree, ai_models_total,
                rsi_14, macd_value, macd_signal, bollinger_upper, bollinger_lower,
                ema_20, ema_50, volume, trend, volatility,
                support_level, resistance_level, hour_of_day, day_of_week, is_weekend,
                account_balance_before, account_balance_after, position_size_ratio,
                kelly_fraction, martingale_level, trading_mode, bot_version, notes
            ) VALUES (
                %(trade_id)s, %(timestamp)s, %(asset)s, %(direction)s, %(amount)s, %(duration)s,
                %(entry_price)s, %(exit_price)s, %(payout_rate)s, %(result)s, %(profit_loss)s,
                %(ai_signal_confidence)s, %(ai_consensus_score)s, %(ai_models_agree)s, %(ai_models_total)s,
                %(rsi_14)s, %(macd_value)s, %(macd_signal)s, %(bollinger_upper)s, %(bollinger_lower)s,
                %(ema_20)s, %(ema_50)s, %(volume)s, %(trend)s, %(volatility)s,
                %(support_level)s, %(resistance_level)s, %(hour_of_day)s, %(day_of_week)s, %(is_weekend)s,
                %(account_balance_before)s, %(account_balance_after)s, %(position_size_ratio)s,
                %(kelly_fraction)s, %(martingale_level)s, %(trading_mode)s, %(bot_version)s, %(notes)s
            )
            RETURNING id
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, trade_data)
                    trade_id = cursor.fetchone()['id']
                    conn.commit()
                    logger.debug(f"Inserted trade {trade_data.get('trade_id')} with ID {trade_id}")
                    return trade_id
        except Exception as e:
            logger.error(f"Error inserting trade: {e}")
            return None

    def update_trade_result(self, trade_id: str, result: str, profit_loss: float,
                           exit_price: float = None, balance_after: float = None):
        """
        Update trade result after expiration

        Args:
            trade_id: Trade identifier
            result: 'win', 'loss', or 'tie'
            profit_loss: Profit or loss amount
            exit_price: Exit price (optional)
            balance_after: Account balance after trade
        """
        query = """
            UPDATE trades
            SET result = %s,
                profit_loss = %s,
                exit_price = COALESCE(%s, exit_price),
                account_balance_after = COALESCE(%s, account_balance_after),
                updated_at = NOW()
            WHERE trade_id = %s
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (result, profit_loss, exit_price, balance_after, trade_id))
                    conn.commit()
                    logger.debug(f"Updated trade {trade_id}: {result}, P/L: {profit_loss}")
        except Exception as e:
            logger.error(f"Error updating trade result: {e}")

    def get_recent_trades(self, limit: int = 100, asset: str = None,
                         trading_mode: str = None) -> List[Dict]:
        """
        Get recent trades

        Args:
            limit: Maximum number of trades to return
            asset: Filter by asset (optional)
            trading_mode: Filter by trading mode (optional)

        Returns:
            List of trade dictionaries
        """
        query = "SELECT * FROM trades WHERE 1=1"
        params = []

        if asset:
            query += " AND asset = %s"
            params.append(asset)

        if trading_mode:
            query += " AND trading_mode = %s"
            params.append(trading_mode)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching recent trades: {e}")
            return []

    def get_statistics(self, days: int = 30, trading_mode: str = None) -> Dict:
        """
        Get trading statistics for the last N days

        Args:
            days: Number of days to analyze
            trading_mode: Filter by trading mode (optional)

        Returns:
            Dictionary with statistics
        """
        query = """
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
                CAST(SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS DECIMAL) /
                    NULLIF(COUNT(*), 0) as win_rate,
                SUM(profit_loss) as total_pnl,
                AVG(profit_loss) as avg_pnl,
                MAX(profit_loss) as best_trade,
                MIN(profit_loss) as worst_trade,
                AVG(ai_signal_confidence) as avg_confidence,
                AVG(ai_consensus_score) as avg_consensus
            FROM trades
            WHERE timestamp >= NOW() - INTERVAL '%s days'
        """
        params = [days]

        if trading_mode:
            query += " AND trading_mode = %s"
            params.append(trading_mode)

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            return {}

    def get_daily_performance(self, days: int = 30) -> List[Dict]:
        """
        Get daily performance metrics using continuous aggregate

        Args:
            days: Number of days to retrieve

        Returns:
            List of daily performance dictionaries
        """
        query = """
            SELECT
                bucket::date as date,
                trading_mode,
                trade_count,
                wins,
                losses,
                win_rate,
                total_pnl,
                avg_confidence
            FROM trades_daily
            WHERE bucket >= NOW() - INTERVAL '%s days'
            ORDER BY bucket DESC
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, [days])
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching daily performance: {e}")
            return []

    def insert_candle(self, candle_data: Dict[str, Any]) -> bool:
        """
        Insert candle/OHLCV data

        Args:
            candle_data: Dictionary containing candle information

        Returns:
            True if successful, False otherwise
        """
        query = """
            INSERT INTO candles (
                timestamp, asset, timeframe, open, high, low, close, volume
            ) VALUES (
                %(timestamp)s, %(asset)s, %(timeframe)s, %(open)s,
                %(high)s, %(low)s, %(close)s, %(volume)s
            )
            ON CONFLICT (timestamp, asset, timeframe) DO UPDATE
            SET open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, candle_data)
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Error inserting candle: {e}")
            return False

    def get_candles(self, asset: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """
        Get historical candles

        Args:
            asset: Asset symbol
            timeframe: Timeframe (1m, 5m, 15m, 1h, etc.)
            limit: Number of candles to retrieve

        Returns:
            List of candle dictionaries
        """
        query = """
            SELECT * FROM candles
            WHERE asset = %s AND timeframe = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (asset, timeframe, limit))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return []

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    logger.info("✓ Database connection test successful")
                    return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✓ PostgreSQL connection pool closed")


def create_connector(**kwargs) -> PostgreSQLConnector:
    """
    Create PostgreSQL connector instance

    Args:
        **kwargs: Additional arguments for connector

    Returns:
        PostgreSQLConnector instance
    """
    return PostgreSQLConnector(**kwargs)


# Example usage
if __name__ == "__main__":
    # Test connection
    pg = create_connector()

    if pg.test_connection():
        print("✅ Database connection successful!")

        # Insert test trade
        test_trade = {
            'trade_id': f'TEST_{datetime.now().timestamp()}',
            'timestamp': datetime.now(),
            'asset': 'EURUSD',
            'direction': 'CALL',
            'amount': 10.0,
            'duration': 60,
            'entry_price': 1.0850,
            'payout_rate': 0.82,
            'result': 'pending',
            'ai_signal_confidence': 75,
            'ai_consensus_score': 0.80,
            'ai_models_agree': 3,
            'ai_models_total': 4,
            'rsi_14': 65.0,
            'trend': 'BULLISH',
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_weekend': datetime.now().weekday() >= 5,
            'account_balance_before': 1000.0,
            'trading_mode': 'demo',
            'bot_version': '1.0.0'
        }

        trade_id = pg.insert_trade(test_trade)
        print(f"✅ Test trade inserted! ID: {trade_id}")

        # Get statistics
        stats = pg.get_statistics(days=7)
        print(f"📊 Stats: {stats}")

    pg.close()
