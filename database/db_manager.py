"""
Database Manager for SQLite/PostgreSQL Operations
Handles all database connections and queries
"""

import sqlite3
import os
import logging
import threading
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_path: str = "kael_trading.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()  # Thread-safe lock for database writes

        # Create database directory if needed
        db_dir = Path(db_path).parent
        if db_dir and not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._initialize_database()

    def _initialize_database(self):
        """Create tables and indexes from schema"""
        try:
            # Read schema file
            schema_path = Path(__file__).parent / "schema.sql"
            with open(schema_path, 'r') as f:
                schema_sql = f.read()

            # Execute schema
            conn = self.get_connection()
            cursor = conn.cursor()

            # Split and execute each statement
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                    except sqlite3.Error as e:
                        # Skip if table already exists
                        if 'already exists' not in str(e):
                            self.logger.warning(f"Schema execution warning: {e}")

            conn.commit()
            self.logger.info("✅ Database initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise

    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Use row factory for dict-like access
            self.connection.row_factory = sqlite3.Row

        return self.connection

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a query with parameters (thread-safe)

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor with results
        """
        with self._lock:  # Thread-safe database writes
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """
        Fetch single row as dictionary

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Row as dict or None
        """
        cursor = self.execute_query(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Fetch all rows as list of dictionaries

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows as dicts
        """
        cursor = self.execute_query(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def insert_trade(self, trade_data: Dict[str, Any]) -> str:
        """
        Insert a new trade record

        Args:
            trade_data: Trade information dictionary

        Returns:
            trade_id of inserted record
        """
        query = """
        INSERT INTO trades (
            trade_id, instrument, direction, amount, duration,
            payout_ratio, entry_time, expiration_time, execution_time_ms,
            result, profit, entry_price, exit_price, price_change,
            mode, balance_before, balance_after, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            trade_data.get('trade_id'),
            trade_data.get('instrument'),
            trade_data.get('direction'),
            trade_data.get('amount'),
            trade_data.get('duration', 60),
            trade_data.get('payout_ratio'),
            trade_data.get('entry_time'),
            trade_data.get('expiration_time'),
            trade_data.get('execution_time_ms'),
            trade_data.get('result', 'PENDING'),
            trade_data.get('profit', 0.0),
            trade_data.get('entry_price'),
            trade_data.get('exit_price'),
            trade_data.get('price_change'),
            trade_data.get('mode', 'demo'),
            trade_data.get('balance_before'),
            trade_data.get('balance_after'),
            trade_data.get('notes')
        )

        self.execute_query(query, params)
        return trade_data['trade_id']

    def update_trade_result(self, trade_id: str, result: str, profit: float,
                           exit_price: Optional[float] = None,
                           balance_after: Optional[float] = None):
        """
        Update trade result after completion

        Args:
            trade_id: Trade identifier
            result: WIN/LOSS/DRAW
            profit: Profit or loss amount
            exit_price: Exit price (optional)
            balance_after: Balance after trade
        """
        query = """
        UPDATE trades
        SET result = ?, profit = ?, exit_time = ?, exit_price = ?,
            balance_after = ?, updated_at = CURRENT_TIMESTAMP
        WHERE trade_id = ?
        """

        params = (result, profit, datetime.now().isoformat(), exit_price, balance_after, trade_id)
        self.execute_query(query, params)

    def insert_ai_prediction(self, prediction_data: Dict[str, Any]):
        """
        Insert AI model prediction

        Args:
            prediction_data: Prediction information
        """
        query = """
        INSERT INTO ai_predictions (
            trade_id, model_name, model_version, direction, confidence,
            signal_strength, primary_indicator, indicators_used,
            reasoning, is_consensus, consensus_weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            prediction_data.get('trade_id'),
            prediction_data.get('model_name'),
            prediction_data.get('model_version', '1.0'),
            prediction_data.get('direction'),
            prediction_data.get('confidence'),
            prediction_data.get('signal_strength'),
            prediction_data.get('primary_indicator'),
            prediction_data.get('indicators_used'),
            prediction_data.get('reasoning'),
            prediction_data.get('is_consensus', False),
            prediction_data.get('consensus_weight', 1.0)
        )

        self.execute_query(query, params)

    def insert_market_context(self, context_data: Dict[str, Any]):
        """
        Insert market context data

        Args:
            context_data: Market context information
        """
        query = """
        INSERT INTO market_context (
            trade_id, candles_1m, candles_5m, candles_15m,
            rsi_14, rsi_7, macd_value, macd_signal, macd_histogram,
            bb_upper, bb_middle, bb_lower, bb_width,
            atr_14, historical_volatility,
            volume_current, volume_avg_20, volume_ratio,
            ema_9, ema_21, ema_50,
            trend_direction, trend_strength,
            support_level, resistance_level,
            distance_to_support, distance_to_resistance,
            session, is_high_impact_news
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            context_data.get('trade_id'),
            context_data.get('candles_1m'),
            context_data.get('candles_5m'),
            context_data.get('candles_15m'),
            context_data.get('rsi_14'),
            context_data.get('rsi_7'),
            context_data.get('macd_value'),
            context_data.get('macd_signal'),
            context_data.get('macd_histogram'),
            context_data.get('bb_upper'),
            context_data.get('bb_middle'),
            context_data.get('bb_lower'),
            context_data.get('bb_width'),
            context_data.get('atr_14'),
            context_data.get('historical_volatility'),
            context_data.get('volume_current'),
            context_data.get('volume_avg_20'),
            context_data.get('volume_ratio'),
            context_data.get('ema_9'),
            context_data.get('ema_21'),
            context_data.get('ema_50'),
            context_data.get('trend_direction'),
            context_data.get('trend_strength'),
            context_data.get('support_level'),
            context_data.get('resistance_level'),
            context_data.get('distance_to_support'),
            context_data.get('distance_to_resistance'),
            context_data.get('session'),
            context_data.get('is_high_impact_news', False)
        )

        self.execute_query(query, params)

    def log_system_event(self, event_type: str, message: str,
                         severity: str = 'INFO', details: Optional[str] = None):
        """
        Log system event

        Args:
            event_type: Type of event
            message: Event message
            severity: Severity level
            details: Additional details (JSON string)
        """
        query = """
        INSERT INTO system_events (event_type, severity, message, details)
        VALUES (?, ?, ?, ?)
        """

        params = (event_type, severity, message, details)
        self.execute_query(query, params)

    def get_recent_trades(self, limit: int = 100) -> List[Dict]:
        """Get recent trades"""
        query = "SELECT * FROM v_recent_trades LIMIT ?"
        return self.fetch_all(query, (limit,))

    def get_instrument_performance(self) -> List[Dict]:
        """Get performance by instrument"""
        return self.fetch_all("SELECT * FROM v_instrument_performance")

    def get_ai_model_performance(self) -> List[Dict]:
        """Get AI model performance metrics"""
        return self.fetch_all("SELECT * FROM v_ai_model_performance")

    def get_strategy_stats(self, limit: int = 1000, hours: int = None) -> List[Dict]:
        """
        Get performance statistics per strategy

        Args:
            limit: Max number of trades to analyze
            hours: Filter trades from last N hours (None = all time)

        Returns:
            List of strategy performance dicts with win rate, P&L, trade count
        """
        time_filter = ""
        params = []

        if hours:
            time_filter = "AND entry_time >= datetime('now', ?)"
            params.append(f'-{hours} hours')

        params.append(limit)

        query = f"""
        SELECT
            selected_strategy as strategy_name,
            COUNT(*) as total_trades,
            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
            ROUND(AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate,
            ROUND(SUM(profit), 2) as total_profit,
            ROUND(AVG(profit), 2) as avg_profit_per_trade,
            ROUND(MAX(profit), 2) as best_trade,
            ROUND(MIN(profit), 2) as worst_trade,
            ROUND(AVG(payout_ratio) * 100, 2) as avg_payout_percent
        FROM trades
        WHERE selected_strategy IS NOT NULL
        {time_filter}
        GROUP BY selected_strategy
        ORDER BY total_profit DESC
        LIMIT ?
        """

        return self.fetch_all(query, tuple(params))

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
