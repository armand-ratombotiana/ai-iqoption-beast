"""
Enhanced Trade Logger with Multi-Account Support
Logs trades, performance metrics, and generates weekly summaries
"""

import logging
import psycopg2
from psycopg2.extras import Json, RealDictCursor
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from contextlib import contextmanager
import json


class MultiAccountTradeLogger:
    """
    Enhanced trade logger for multi-account trading system
    Supports PostgreSQL/TimescaleDB with comprehensive tracking
    """
    
    def __init__(self, database_url: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.database_url = database_url
        self._test_connection()
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            self.logger.info("✅ Database connection successful")
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager"""
        conn = psycopg2.connect(self.database_url)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def log_trade(self, account_id: str, trade_data: Dict) -> int:
        """
        Log a trade to the database
        
        Args:
            account_id: Account identifier
            trade_data: Trade information dictionary
            
        Returns:
            Trade ID from database
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO trades (
                            account_id, trade_id, instrument, direction, amount,
                            entry_time, exit_time, expiration_seconds, result, profit,
                            payout_ratio, selected_strategy, strategy_profile, confidence,
                            signal_data, strategy_breakdown, market_conditions,
                            execution_time_ms, generation_time_ms, mode
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) RETURNING id
                    """, (
                        account_id,
                        trade_data.get('trade_id'),
                        trade_data.get('instrument'),
                        trade_data.get('direction'),
                        trade_data.get('amount'),
                        trade_data.get('entry_time', datetime.now()),
                        trade_data.get('exit_time'),
                        trade_data.get('expiration_seconds'),
                        trade_data.get('result'),
                        trade_data.get('profit'),
                        trade_data.get('payout_ratio'),
                        trade_data.get('selected_strategy'),
                        trade_data.get('strategy_profile'),
                        trade_data.get('confidence'),
                        Json(trade_data.get('signal_data', {})),
                        Json(trade_data.get('strategy_breakdown', [])),
                        Json(trade_data.get('market_conditions', {})),
                        trade_data.get('execution_time_ms'),
                        trade_data.get('generation_time_ms'),
                        trade_data.get('mode', 'demo')
                    ))
                    
                    trade_id = cur.fetchone()[0]
                    self.logger.debug(f"Trade logged: {trade_id} for account {account_id}")
                    return trade_id
                    
        except Exception as e:
            self.logger.error(f"Failed to log trade: {e}")
            return -1
    
    def update_trade_result(self, trade_id: int, result: str, profit: float, 
                          exit_time: Optional[datetime] = None):
        """Update trade result after completion"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE trades 
                        SET result = %s, profit = %s, exit_time = %s
                        WHERE id = %s
                    """, (result, profit, exit_time or datetime.now(), trade_id))
                    
            self.logger.debug(f"Trade {trade_id} updated: {result}, profit: {profit}")
        except Exception as e:
            self.logger.error(f"Failed to update trade result: {e}")
    
    def log_system_event(self, account_id: Optional[str], event_type: str,
                        severity: str, message: str, details: Optional[Dict] = None):
        """Log system event"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO system_events (
                            account_id, event_type, severity, message, details
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, (account_id, event_type, severity, message, Json(details or {})))
                    
        except Exception as e:
            self.logger.error(f"Failed to log system event: {e}")
    
    def update_account_health(self, account_id: str, is_healthy: bool,
                            connection_failures: int = 0):
        """Update account health status"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE accounts 
                        SET is_healthy = %s, 
                            connection_failures = %s,
                            last_connection = %s,
                            updated_at = %s
                        WHERE account_id = %s
                    """, (is_healthy, connection_failures, datetime.now(), 
                         datetime.now(), account_id))
                    
        except Exception as e:
            self.logger.error(f"Failed to update account health: {e}")
    
    def get_account_performance(self, account_id: str, 
                               days: int = 1) -> Optional[Dict]:
        """Get account performance for specified days"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) as total_trades,
                            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                            SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                            ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
                            ROUND(SUM(COALESCE(profit, 0)), 2) as total_pnl,
                            ROUND(AVG(confidence), 2) as avg_confidence,
                            ROUND(AVG(execution_time_ms), 0) as avg_execution_ms
                        FROM trades
                        WHERE account_id = %s
                            AND entry_time >= NOW() - INTERVAL '%s days'
                    """, (account_id, days))
                    
                    return dict(cur.fetchone())
                    
        except Exception as e:
            self.logger.error(f"Failed to get account performance: {e}")
            return None
    
    def get_strategy_performance(self, account_id: Optional[str] = None,
                                days: int = 7) -> List[Dict]:
        """Get strategy performance across accounts"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if account_id:
                        cur.execute("""
                            SELECT 
                                selected_strategy,
                                COUNT(*) as total_trades,
                                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                                SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                                ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
                                ROUND(SUM(COALESCE(profit, 0)), 2) as total_pnl,
                                ROUND(AVG(COALESCE(profit, 0)), 2) as avg_profit_per_trade,
                                ROUND(AVG(payout_ratio * 100), 2) as avg_payout_percent
                            FROM trades
                            WHERE account_id = %s
                                AND entry_time >= NOW() - INTERVAL '%s days'
                                AND selected_strategy IS NOT NULL
                            GROUP BY selected_strategy
                            ORDER BY total_pnl DESC
                        """, (account_id, days))
                    else:
                        cur.execute("""
                            SELECT 
                                selected_strategy,
                                COUNT(*) as total_trades,
                                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                                SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                                ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
                                ROUND(SUM(COALESCE(profit, 0)), 2) as total_pnl,
                                ROUND(AVG(COALESCE(profit, 0)), 2) as avg_profit_per_trade,
                                ROUND(AVG(payout_ratio * 100), 2) as avg_payout_percent,
                                COUNT(DISTINCT account_id) as accounts_using
                            FROM trades
                            WHERE entry_time >= NOW() - INTERVAL '%s days'
                                AND selected_strategy IS NOT NULL
                            GROUP BY selected_strategy
                            ORDER BY total_pnl DESC
                        """, (days,))
                    
                    return [dict(row) for row in cur.fetchall()]
                    
        except Exception as e:
            self.logger.error(f"Failed to get strategy performance: {e}")
            return []
    
    def get_recent_trades(self, account_id: Optional[str] = None,
                         limit: int = 100) -> List[Dict]:
        """Get recent trades"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if account_id:
                        cur.execute("""
                            SELECT * FROM v_recent_trades
                            WHERE account_id = %s
                            LIMIT %s
                        """, (account_id, limit))
                    else:
                        cur.execute("""
                            SELECT * FROM v_recent_trades
                            LIMIT %s
                        """, (limit,))
                    
                    return [dict(row) for row in cur.fetchall()]
                    
        except Exception as e:
            self.logger.error(f"Failed to get recent trades: {e}")
            return []
    
    def update_daily_performance(self):
        """Update daily performance snapshots"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Update account performance
                    cur.execute("SELECT update_daily_account_performance()")
                    
                    # Update strategy performance
                    cur.execute("SELECT update_daily_strategy_performance()")
                    
            self.logger.info("✅ Daily performance updated")
        except Exception as e:
            self.logger.error(f"Failed to update daily performance: {e}")
    
    def generate_weekly_summary(self, week_start: Optional[date] = None):
        """Generate weekly performance summary"""
        if week_start is None:
            # Get Monday of current week
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT generate_weekly_summary(%s)",
                        (week_start,)
                    )
                    
            self.logger.info(f"✅ Weekly summary generated for {week_start}")
        except Exception as e:
            self.logger.error(f"Failed to generate weekly summary: {e}")
    
    def get_weekly_summary(self, week_start: Optional[date] = None) -> Optional[Dict]:
        """Get weekly performance summary"""
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM weekly_performance
                        WHERE week_start = %s
                    """, (week_start,))
                    
                    result = cur.fetchone()
                    return dict(result) if result else None
                    
        except Exception as e:
            self.logger.error(f"Failed to get weekly summary: {e}")
            return None
    
    def export_trades_to_csv(self, output_file: str, account_id: Optional[str] = None,
                           days: int = 7):
        """Export trades to CSV file"""
        import csv
        
        try:
            trades = self.get_recent_trades(account_id, limit=10000)
            
            # Filter by days
            cutoff = datetime.now() - timedelta(days=days)
            trades = [
                t for t in trades 
                if t.get('entry_time') and t['entry_time'] >= cutoff
            ]
            
            if not trades:
                self.logger.warning("No trades to export")
                return
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=trades[0].keys())
                writer.writeheader()
                writer.writerows(trades)
            
            self.logger.info(f"✅ Exported {len(trades)} trades to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to export trades: {e}")
    
    def export_performance_to_json(self, output_file: str, days: int = 7):
        """Export performance summary to JSON"""
        try:
            summary = {
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'accounts': [],
                'strategies': self.get_strategy_performance(days=days)
            }
            
            # Get all accounts
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT account_id FROM accounts")
                    accounts = [row['account_id'] for row in cur.fetchall()]
            
            # Get performance for each account
            for account_id in accounts:
                perf = self.get_account_performance(account_id, days)
                if perf:
                    perf['account_id'] = account_id
                    summary['accounts'].append(perf)
            
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            self.logger.info(f"✅ Exported performance summary to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to export performance: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get overall portfolio summary"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get overall stats
                    cur.execute("""
                        SELECT 
                            COUNT(DISTINCT account_id) as total_accounts,
                            COUNT(*) as total_trades,
                            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as total_wins,
                            SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as total_losses,
                            ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as overall_win_rate,
                            ROUND(SUM(COALESCE(profit, 0)), 2) as total_pnl
                        FROM trades
                        WHERE DATE(entry_time) = CURRENT_DATE
                    """)
                    
                    overall = dict(cur.fetchone())
                    
                    # Get account breakdown
                    cur.execute("""
                        SELECT * FROM v_daily_account_performance
                        ORDER BY daily_pnl DESC
                    """)
                    
                    accounts = [dict(row) for row in cur.fetchall()]
                    
                    return {
                        'overall': overall,
                        'accounts': accounts,
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            self.logger.error(f"Failed to get portfolio summary: {e}")
            return {}
