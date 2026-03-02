#!/usr/bin/env python3
"""
Metrics Collection System for Paper Trading
Tracks and exports trading metrics and trade history

Features:
- Trade history tracking (JSON)
- CSV export for analysis
- Real-time metrics updates
- Database schema for trades
- Batch metrics writing
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class TradeRecord:
    """Trade record data structure"""
    timestamp: str
    pair: str
    signal: str
    confidence: float
    amount: float
    duration: int
    entry_price: float
    payout: float
    rsi: float
    macd_histogram: float
    stoch_k: float
    adx: float
    bb_position: float
    order_id: Optional[int] = None
    exit_price: Optional[float] = None
    profit: Optional[float] = None
    result: Optional[str] = None


class MetricsCollector:
    """Collects and manages trading metrics"""

    def __init__(self, data_dir: str = "data"):
        """Initialize metrics collector"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # File paths
        self.trades_json = self.data_dir / "trades.json"
        self.trades_csv = self.data_dir / "trades.csv"
        self.db_file = self.data_dir / "trading.db"
        self.metrics_json = self.data_dir / "metrics.json"
        self.status_json = self.data_dir / "status.json"

        # In-memory cache
        self.trades_cache: List[Dict] = []
        self.metrics_cache: Dict = {}

        # Load existing data
        self._load_trades()
        self._initialize_database()

    def _load_trades(self):
        """Load trades from JSON file"""
        try:
            if self.trades_json.exists():
                with open(self.trades_json, 'r') as f:
                    self.trades_cache = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load trades: {e}")
            self.trades_cache = []

    def _initialize_database(self):
        """Initialize SQLite database for trades"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT UNIQUE NOT NULL,
                    pair TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    amount REAL NOT NULL,
                    duration INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    payout REAL NOT NULL,
                    rsi REAL NOT NULL,
                    macd_histogram REAL NOT NULL,
                    stoch_k REAL NOT NULL,
                    adx REAL NOT NULL,
                    bb_position REAL NOT NULL,
                    order_id INTEGER,
                    exit_price REAL,
                    profit REAL,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_trades INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    ties INTEGER,
                    win_rate REAL,
                    total_profit REAL,
                    daily_profit REAL,
                    daily_loss REAL,
                    consecutive_losses INTEGER,
                    max_drawdown REAL,
                    trades_per_hour REAL,
                    avg_profit_per_trade REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")

    def record_trade(self, trade_data: Dict) -> bool:
        """Record a new trade"""
        try:
            # Add to JSON
            self.trades_cache.append(trade_data)
            self._save_trades_json()

            # Add to database
            self._save_trade_to_db(trade_data)

            # Update CSV
            self._update_trades_csv()

            return True
        except Exception as e:
            print(f"Error recording trade: {e}")
            return False

    def update_trade_result(self, trade_timestamp: str, result_data: Dict) -> bool:
        """Update trade with result (filled after trade completes)"""
        try:
            # Find and update in cache
            for trade in self.trades_cache:
                if trade.get('timestamp') == trade_timestamp:
                    trade.update(result_data)
                    break

            # Save updated trades
            self._save_trades_json()
            self._update_trades_csv()
            self._update_trade_in_db(trade_timestamp, result_data)

            return True
        except Exception as e:
            print(f"Error updating trade result: {e}")
            return False

    def _save_trades_json(self):
        """Save trades to JSON file"""
        try:
            with open(self.trades_json, 'w') as f:
                json.dump(self.trades_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving trades JSON: {e}")

    def _update_trades_csv(self):
        """Export trades to CSV"""
        try:
            if not self.trades_cache:
                return

            # Get all field names from first trade
            fieldnames = list(self.trades_cache[0].keys())

            with open(self.trades_csv, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.trades_cache)

        except Exception as e:
            print(f"Error updating CSV: {e}")

    def _save_trade_to_db(self, trade_data: Dict):
        """Save trade to database"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            columns = ', '.join(trade_data.keys())
            placeholders = ', '.join('?' * len(trade_data))
            values = tuple(trade_data.values())

            cursor.execute(
                f'INSERT OR REPLACE INTO trades ({columns}) VALUES ({placeholders})',
                values
            )

            conn.commit()
            conn.close()

        except sqlite3.IntegrityError:
            # Trade already exists, update instead
            self._update_trade_in_db(
                trade_data.get('timestamp'),
                trade_data
            )
        except Exception as e:
            print(f"Error saving to database: {e}")

    def _update_trade_in_db(self, timestamp: str, update_data: Dict):
        """Update trade in database"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            # Build UPDATE statement
            set_clause = ', '.join([f'{k} = ?' for k in update_data.keys()])
            values = list(update_data.values()) + [timestamp]

            cursor.execute(
                f'UPDATE trades SET {set_clause} WHERE timestamp = ?',
                values
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error updating database: {e}")

    def save_metrics(self, metrics: Dict) -> bool:
        """Save current metrics snapshot"""
        try:
            # Add timestamp
            metrics['timestamp'] = datetime.now().isoformat()

            # Save to JSON
            with open(self.metrics_json, 'w') as f:
                json.dump(metrics, f, indent=2)

            # Save to database
            self._save_metrics_to_db(metrics)

            self.metrics_cache = metrics
            return True

        except Exception as e:
            print(f"Error saving metrics: {e}")
            return False

    def _save_metrics_to_db(self, metrics: Dict):
        """Save metrics to database"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO metrics (
                    timestamp, total_trades, wins, losses, ties,
                    win_rate, total_profit, daily_profit, daily_loss,
                    consecutive_losses, max_drawdown, trades_per_hour,
                    avg_profit_per_trade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('timestamp'),
                metrics.get('total_trades', 0),
                metrics.get('wins', 0),
                metrics.get('losses', 0),
                metrics.get('ties', 0),
                metrics.get('win_rate', 0.0),
                metrics.get('total_profit', 0.0),
                metrics.get('daily_profit', 0.0),
                metrics.get('daily_loss', 0.0),
                metrics.get('consecutive_losses', 0),
                metrics.get('max_drawdown', 0.0),
                metrics.get('trades_per_hour', 0.0),
                metrics.get('avg_profit_per_trade', 0.0),
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving metrics to database: {e}")

    def save_status(self, status: Dict) -> bool:
        """Save engine status"""
        try:
            with open(self.status_json, 'w') as f:
                json.dump(status, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving status: {e}")
            return False

    def get_trades(self) -> List[Dict]:
        """Get all trades"""
        return self.trades_cache.copy()

    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return self.metrics_cache.copy()

    def get_db_stats(self) -> Dict:
        """Get statistics from database"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            # Get trade stats
            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN result = 'TIE' THEN 1 ELSE 0 END) as ties,
                    SUM(profit) as total_profit,
                    AVG(profit) as avg_profit
                FROM trades
                WHERE result IS NOT NULL
            ''')

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'total_trades': result[0] or 0,
                    'wins': result[1] or 0,
                    'losses': result[2] or 0,
                    'ties': result[3] or 0,
                    'total_profit': round(result[4] or 0, 2),
                    'avg_profit': round(result[5] or 0, 2),
                }

        except Exception as e:
            print(f"Error getting database stats: {e}")

        return {}

    def export_trades_csv(self, output_file: Optional[str] = None) -> str:
        """Export trades to CSV file"""
        if output_file is None:
            output_file = str(self.trades_csv)
        else:
            output_file = str(Path(output_file))

        try:
            self._update_trades_csv()
            return output_file
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""

    def get_data_size(self) -> Dict[str, float]:
        """Get sizes of data files (in MB)"""
        sizes = {}

        for file_path in [self.trades_json, self.trades_csv, self.db_file]:
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                sizes[file_path.name] = round(size_mb, 2)

        return sizes


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Metrics collection for paper trading')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--show-stats', action='store_true', help='Show database statistics')
    parser.add_argument('--export-csv', help='Export trades to CSV file')
    parser.add_argument('--data-size', action='store_true', help='Show data file sizes')

    args = parser.parse_args()

    collector = MetricsCollector(data_dir=args.data_dir)

    if args.show_stats:
        print("Database Statistics:")
        print("-" * 80)
        stats = collector.get_db_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

    if args.export_csv:
        output = collector.export_trades_csv(args.export_csv)
        print(f"Trades exported to: {output}")

    if args.data_size:
        print("Data File Sizes:")
        print("-" * 80)
        sizes = collector.get_data_size()
        for name, size in sizes.items():
            print(f"  {name}: {size} MB")


if __name__ == '__main__':
    main()
