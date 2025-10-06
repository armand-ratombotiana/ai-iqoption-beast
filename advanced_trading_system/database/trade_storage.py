"""
Trade Storage and Database Management
Stores trades with complete market context for learning and analysis
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class TradeDatabase:
    """
    SQLite database for comprehensive trade storage
    """

    def __init__(self, db_path: str = "trades.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self._create_tables()

    def _create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()

        # Main trades table with full context
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                pair TEXT NOT NULL,
                direction TEXT NOT NULL CHECK(direction IN ('CALL', 'PUT')),
                amount REAL NOT NULL,
                duration INTEGER NOT NULL,
                result TEXT CHECK(result IN ('WIN', 'LOSS', 'PENDING')),
                profit REAL,

                -- AI Consensus
                ai_signal_confidence INTEGER,
                ai_model_agreement REAL,
                ai_models_count INTEGER,
                primary_model TEXT,

                -- Pre-Trade Technical Indicators
                entry_price REAL,
                rsi_14 REAL,
                rsi_7 REAL,
                macd_value REAL,
                macd_signal REAL,
                macd_histogram REAL,
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                bb_position REAL,
                ema_12 REAL,
                ema_26 REAL,
                sma_20 REAL,
                sma_50 REAL,
                atr REAL,
                stochastic_k REAL,
                stochastic_d REAL,
                adx REAL,
                cci REAL,
                williams_r REAL,

                -- Market Analysis
                trend TEXT,
                volatility TEXT,
                volatility_value REAL,
                support_level REAL,
                resistance_level REAL,
                volume_ma REAL,
                volume_trend TEXT,

                -- Time Context
                hour_of_day INTEGER,
                day_of_week INTEGER,
                market_session TEXT,

                -- Patterns
                candlestick_pattern TEXT,
                chart_pattern TEXT,

                -- Post-Trade Analysis
                exit_price REAL,
                price_change REAL,
                price_change_percent REAL,
                highest_price REAL,
                lowest_price REAL,
                price_range REAL,
                actual_direction TEXT,
                prediction_correct BOOLEAN,

                -- Post-Trade Indicators
                rsi_14_post REAL,
                macd_value_post REAL,
                trend_post TEXT,
                volatility_post REAL,

                -- Events
                news_event TEXT,
                volatility_spike BOOLEAN,
                trend_reversal BOOLEAN,

                -- Full Context (JSON)
                pre_trade_context_json TEXT,
                post_trade_context_json TEXT,
                ai_models_votes_json TEXT,

                -- Metadata
                strategy_version TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # AI Model Performance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy REAL,
                current_weight REAL DEFAULT 1.0,
                avg_confidence REAL,
                win_rate REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Market Patterns Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                pattern_type TEXT,
                conditions_json TEXT,
                win_rate REAL,
                occurrences INTEGER DEFAULT 0,
                last_seen DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Daily Performance Summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_trades INTEGER,
                wins INTEGER,
                losses INTEGER,
                win_rate REAL,
                total_profit REAL,
                max_drawdown REAL,
                best_pair TEXT,
                best_hour INTEGER,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_result ON trades(result)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_trend ON trades(trend)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_rsi ON trades(rsi_14)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_prediction ON trades(prediction_correct)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_hour ON trades(hour_of_day)")

        self.conn.commit()

    def insert_trade(self, trade_data: Dict) -> bool:
        """Insert a new trade record"""
        try:
            cursor = self.conn.cursor()

            # Prepare column names and values
            columns = ', '.join(trade_data.keys())
            placeholders = ', '.join(['?' for _ in trade_data])
            values = tuple(trade_data.values())

            cursor.execute(
                f"INSERT INTO trades ({columns}) VALUES ({placeholders})",
                values
            )

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting trade: {e}")
            return False

    def update_trade(self, trade_id: str, updates: Dict) -> bool:
        """Update an existing trade record"""
        try:
            cursor = self.conn.cursor()

            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = tuple(updates.values()) + (trade_id,)

            cursor.execute(
                f"UPDATE trades SET {set_clause} WHERE trade_id = ?",
                values
            )

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating trade: {e}")
            return False

    def get_trade(self, trade_id: str) -> Optional[Dict]:
        """Get a specific trade by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_recent_trades(self, limit: int = 50) -> List[Dict]:
        """Get recent trades"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_trades_by_pair(self, pair: str, limit: int = 100) -> List[Dict]:
        """Get trades for a specific pair"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM trades WHERE pair = ? ORDER BY timestamp DESC LIMIT ?",
            (pair, limit)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_winning_trades(self, limit: int = 100) -> List[Dict]:
        """Get winning trades for pattern analysis"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM trades WHERE result = 'WIN' ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_trades_by_conditions(self, conditions: Dict, limit: int = 50) -> List[Dict]:
        """Find trades with similar market conditions"""
        cursor = self.conn.cursor()

        # Build WHERE clause
        where_clauses = []
        values = []

        for key, value in conditions.items():
            if isinstance(value, tuple):  # Range query
                where_clauses.append(f"{key} BETWEEN ? AND ?")
                values.extend(value)
            else:
                where_clauses.append(f"{key} = ?")
                values.append(value)

        where_sql = " AND ".join(where_clauses)
        values.append(limit)

        cursor.execute(
            f"SELECT * FROM trades WHERE {where_sql} ORDER BY timestamp DESC LIMIT ?",
            tuple(values)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self, period: str = 'all') -> Dict:
        """Get trading statistics"""
        cursor = self.conn.cursor()

        # Build date filter
        date_filter = ""
        if period == 'today':
            date_filter = "WHERE DATE(timestamp) = DATE('now')"
        elif period == 'week':
            date_filter = "WHERE timestamp >= datetime('now', '-7 days')"
        elif period == 'month':
            date_filter = "WHERE timestamp >= datetime('now', '-30 days')"

        # Overall stats
        cursor.execute(f"""
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) * 100 as win_rate,
                SUM(profit) as total_profit,
                AVG(profit) as avg_profit,
                MAX(profit) as max_profit,
                MIN(profit) as max_loss
            FROM trades
            {date_filter}
        """)

        stats = dict(cursor.fetchone())

        # Win rate by trend
        cursor.execute(f"""
            SELECT
                trend,
                COUNT(*) as trades,
                AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) * 100 as win_rate
            FROM trades
            {date_filter}
            GROUP BY trend
        """)
        stats['by_trend'] = [dict(row) for row in cursor.fetchall()]

        # Win rate by hour
        cursor.execute(f"""
            SELECT
                hour_of_day,
                COUNT(*) as trades,
                AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) * 100 as win_rate
            FROM trades
            {date_filter}
            GROUP BY hour_of_day
            ORDER BY hour_of_day
        """)
        stats['by_hour'] = [dict(row) for row in cursor.fetchall()]

        return stats

    def update_ai_model_performance(self, model_name: str, prediction_correct: bool,
                                    confidence: float, current_weight: float):
        """Update AI model performance tracking"""
        cursor = self.conn.cursor()

        # Get current stats
        cursor.execute(
            "SELECT * FROM ai_model_performance WHERE model_name = ? ORDER BY timestamp DESC LIMIT 1",
            (model_name,)
        )
        row = cursor.fetchone()

        if row:
            stats = dict(row)
            total = stats['total_predictions'] + 1
            correct = stats['correct_predictions'] + (1 if prediction_correct else 0)
            accuracy = (correct / total) * 100
        else:
            total = 1
            correct = 1 if prediction_correct else 0
            accuracy = (correct / total) * 100

        # Insert new record
        cursor.execute("""
            INSERT INTO ai_model_performance
            (model_name, timestamp, total_predictions, correct_predictions,
             accuracy, current_weight, avg_confidence, win_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model_name,
            datetime.now().isoformat(),
            total,
            correct,
            accuracy,
            current_weight,
            confidence,
            accuracy
        ))

        self.conn.commit()

    def get_model_performance(self, model_name: str) -> Optional[Dict]:
        """Get latest performance stats for a model"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM ai_model_performance WHERE model_name = ? ORDER BY timestamp DESC LIMIT 1",
            (model_name,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_models_performance(self) -> List[Dict]:
        """Get performance for all models"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT model_name,
                   MAX(timestamp) as last_update,
                   total_predictions,
                   correct_predictions,
                   accuracy,
                   current_weight
            FROM ai_model_performance
            GROUP BY model_name
            ORDER BY accuracy DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def export_to_csv(self, filepath: str, limit: int = 1000):
        """Export trades to CSV file"""
        import csv

        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM trades ORDER BY timestamp DESC LIMIT {limit}")

        rows = cursor.fetchall()
        if not rows:
            return

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(rows[0].keys())
            # Write data
            for row in rows:
                writer.writerow(row)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
