#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AI MODEL DATA COLLECTOR
Comprehensive data collection system for training custom IQOption AI model

Features:
✅ Complete trade lifecycle tracking
✅ Market condition snapshots
✅ Strategy performance metrics
✅ Time-series data structuring
✅ Feature engineering for ML
✅ Weekly analysis preparation
✅ Data integrity validation
"""

import psycopg2
import psycopg2.extras
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from pathlib import Path


class AIDataCollector:
    """Collects and structures data for AI model training"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.conn = None
        self.initialize_schema()

    def initialize_schema(self):
        """Initialize comprehensive database schema for AI training"""
        try:
            self.conn = psycopg2.connect(self.database_url, connect_timeout=10)
            cursor = self.conn.cursor()

            # Enhanced trades table with AI features
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades_ai (
                    id SERIAL PRIMARY KEY,
                    trade_id VARCHAR(100) UNIQUE NOT NULL,
                    account_id VARCHAR(100) DEFAULT 'default',
                    strategy_name VARCHAR(100) NOT NULL,

                    -- Trade execution
                    instrument VARCHAR(50) NOT NULL,
                    direction VARCHAR(10) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    entry_time TIMESTAMP NOT NULL,
                    exit_time TIMESTAMP,
                    duration_seconds INTEGER,

                    -- Prices
                    entry_price DECIMAL(20, 8),
                    exit_price DECIMAL(20, 8),
                    price_movement DECIMAL(20, 8),

                    -- Execution metrics
                    entry_delay_ms INTEGER,
                    execution_quality VARCHAR(20),

                    -- Trade parameters
                    confidence DECIMAL(5, 2),
                    payout_ratio DECIMAL(5, 4),
                    expected_profit DECIMAL(10, 2),

                    -- Outcome
                    result VARCHAR(10),
                    profit DECIMAL(10, 2),

                    -- Market conditions at entry
                    volatility DECIMAL(10, 8),
                    trend_strength DECIMAL(10, 4),
                    trend_direction INTEGER,
                    rsi DECIMAL(10, 4),
                    macd DECIMAL(20, 8),
                    macd_signal DECIMAL(20, 8),
                    bollinger_position DECIMAL(10, 4),

                    -- Momentum indicators
                    momentum_1m DECIMAL(10, 8),
                    momentum_5m DECIMAL(10, 8),
                    volume_ratio DECIMAL(10, 4),

                    -- Binary-specific
                    seconds_to_minute INTEGER,
                    candle_completion DECIMAL(5, 4),
                    entry_timing_quality VARCHAR(20),

                    -- Market classification
                    market_condition VARCHAR(50),

                    -- Session info
                    trading_session VARCHAR(50),
                    day_of_week INTEGER,
                    hour_of_day INTEGER,

                    -- Performance tracking
                    win_streak INTEGER DEFAULT 0,
                    loss_streak INTEGER DEFAULT 0,
                    session_pnl DECIMAL(10, 2) DEFAULT 0,

                    -- Feature vector for AI
                    feature_vector JSONB,

                    -- Metadata
                    mode VARCHAR(20),
                    bot_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_trades_ai_entry_time ON trades_ai(entry_time);
                CREATE INDEX IF NOT EXISTS idx_trades_ai_strategy ON trades_ai(strategy_name);
                CREATE INDEX IF NOT EXISTS idx_trades_ai_instrument ON trades_ai(instrument);
                CREATE INDEX IF NOT EXISTS idx_trades_ai_result ON trades_ai(result);
                CREATE INDEX IF NOT EXISTS idx_trades_ai_market_condition ON trades_ai(market_condition);
            """)

            # Market snapshots table (for detailed time-series analysis)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_snapshots (
                    id SERIAL PRIMARY KEY,
                    snapshot_time TIMESTAMP NOT NULL,
                    instrument VARCHAR(50) NOT NULL,

                    -- OHLCV
                    open DECIMAL(20, 8),
                    high DECIMAL(20, 8),
                    low DECIMAL(20, 8),
                    close DECIMAL(20, 8),
                    volume DECIMAL(20, 2),

                    -- Technical indicators
                    rsi_14 DECIMAL(10, 4),
                    macd DECIMAL(20, 8),
                    macd_signal DECIMAL(20, 8),
                    macd_histogram DECIMAL(20, 8),
                    bb_upper DECIMAL(20, 8),
                    bb_middle DECIMAL(20, 8),
                    bb_lower DECIMAL(20, 8),

                    -- Trend indicators
                    ema_8 DECIMAL(20, 8),
                    ema_21 DECIMAL(20, 8),
                    ema_50 DECIMAL(20, 8),
                    adx DECIMAL(10, 4),

                    -- Volatility
                    atr_14 DECIMAL(20, 8),
                    std_dev_20 DECIMAL(20, 8),

                    -- Momentum
                    roc_1 DECIMAL(10, 8),
                    roc_5 DECIMAL(10, 8),

                    -- Market microstructure
                    spread DECIMAL(20, 8),
                    liquidity_score DECIMAL(10, 4),

                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_snapshots_time ON market_snapshots(snapshot_time);
                CREATE INDEX IF NOT EXISTS idx_snapshots_instrument ON market_snapshots(instrument);
            """)

            # Strategy performance tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    id SERIAL PRIMARY KEY,
                    strategy_name VARCHAR(100) NOT NULL,
                    measurement_time TIMESTAMP NOT NULL,

                    -- Performance metrics
                    total_trades INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    win_rate DECIMAL(10, 4),

                    -- Financial metrics
                    total_pnl DECIMAL(10, 2),
                    avg_profit_per_trade DECIMAL(10, 2),
                    max_profit DECIMAL(10, 2),
                    max_loss DECIMAL(10, 2),

                    -- Risk metrics
                    sharpe_ratio DECIMAL(10, 4),
                    sortino_ratio DECIMAL(10, 4),
                    max_drawdown DECIMAL(10, 4),
                    kelly_fraction DECIMAL(10, 4),

                    -- Consistency metrics
                    avg_confidence DECIMAL(10, 4),
                    confidence_calibration DECIMAL(10, 4),

                    -- Streak tracking
                    current_streak INTEGER,
                    max_win_streak INTEGER,
                    max_loss_streak INTEGER,

                    -- Time-based performance
                    trades_per_hour DECIMAL(10, 4),
                    best_hour INTEGER,
                    worst_hour INTEGER,

                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_strategy_perf_time ON strategy_performance(measurement_time);
                CREATE INDEX IF NOT EXISTS idx_strategy_perf_name ON strategy_performance(strategy_name);
            """)

            # Session analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_analytics (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) UNIQUE NOT NULL,
                    session_start TIMESTAMP NOT NULL,
                    session_end TIMESTAMP,

                    -- Session metrics
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    session_pnl DECIMAL(10, 2),

                    -- Market conditions
                    avg_volatility DECIMAL(10, 8),
                    predominant_market_condition VARCHAR(50),

                    -- Performance by strategy
                    strategy_breakdown JSONB,

                    -- Time analysis
                    most_active_hour INTEGER,
                    peak_performance_time VARCHAR(50),

                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Weekly analysis summary
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weekly_analysis (
                    id SERIAL PRIMARY KEY,
                    week_start DATE NOT NULL,
                    week_end DATE NOT NULL,

                    -- Overall performance
                    total_trades INTEGER,
                    win_rate DECIMAL(10, 4),
                    total_pnl DECIMAL(10, 2),

                    -- Best performers
                    best_strategy VARCHAR(100),
                    best_strategy_win_rate DECIMAL(10, 4),
                    best_instrument VARCHAR(50),

                    -- Market insights
                    most_common_condition VARCHAR(50),
                    avg_volatility DECIMAL(10, 8),

                    -- Recommendations
                    recommended_strategies JSONB,
                    ai_training_readiness BOOLEAN DEFAULT FALSE,

                    -- Data quality
                    data_completeness DECIMAL(5, 4),
                    missing_data_count INTEGER,

                    analysis_complete BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            self.conn.commit()
            cursor.close()

            print("✅ AI Data Collection schema initialized")

        except Exception as e:
            print(f"❌ Schema initialization error: {e}")
            if self.conn:
                self.conn.rollback()

    def log_trade_ai(self, trade_data: Dict):
        """Log comprehensive trade data for AI training"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO trades_ai (
                    trade_id, strategy_name, instrument, direction, amount,
                    entry_time, entry_price, entry_delay_ms, confidence,
                    payout_ratio, expected_profit, volatility, trend_strength,
                    trend_direction, rsi, macd, macd_signal, bollinger_position,
                    momentum_1m, momentum_5m, volume_ratio, seconds_to_minute,
                    candle_completion, entry_timing_quality, market_condition,
                    trading_session, day_of_week, hour_of_day, feature_vector, mode
                ) VALUES (
                    %(trade_id)s, %(strategy_name)s, %(instrument)s, %(direction)s,
                    %(amount)s, %(entry_time)s, %(entry_price)s, %(entry_delay_ms)s,
                    %(confidence)s, %(payout_ratio)s, %(expected_profit)s,
                    %(volatility)s, %(trend_strength)s, %(trend_direction)s,
                    %(rsi)s, %(macd)s, %(macd_signal)s, %(bollinger_position)s,
                    %(momentum_1m)s, %(momentum_5m)s, %(volume_ratio)s,
                    %(seconds_to_minute)s, %(candle_completion)s,
                    %(entry_timing_quality)s, %(market_condition)s,
                    %(trading_session)s, %(day_of_week)s, %(hour_of_day)s,
                    %(feature_vector)s, %(mode)s
                )
            """, trade_data)

            self.conn.commit()
            cursor.close()

        except Exception as e:
            print(f"❌ Error logging AI trade data: {e}")
            if self.conn:
                self.conn.rollback()

    def update_trade_result(self, trade_id: str, exit_data: Dict):
        """Update trade with exit data and outcome"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                UPDATE trades_ai SET
                    exit_time = %(exit_time)s,
                    exit_price = %(exit_price)s,
                    price_movement = %(price_movement)s,
                    result = %(result)s,
                    profit = %(profit)s,
                    duration_seconds = %(duration_seconds)s
                WHERE trade_id = %(trade_id)s
            """, {**exit_data, 'trade_id': trade_id})

            self.conn.commit()
            cursor.close()

        except Exception as e:
            print(f"❌ Error updating trade result: {e}")
            if self.conn:
                self.conn.rollback()

    def log_market_snapshot(self, snapshot_data: Dict):
        """Log detailed market snapshot for time-series analysis"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO market_snapshots (
                    snapshot_time, instrument, open, high, low, close, volume,
                    rsi_14, macd, macd_signal, macd_histogram,
                    bb_upper, bb_middle, bb_lower,
                    ema_8, ema_21, ema_50, adx, atr_14, std_dev_20,
                    roc_1, roc_5, spread, liquidity_score
                ) VALUES (
                    %(snapshot_time)s, %(instrument)s, %(open)s, %(high)s,
                    %(low)s, %(close)s, %(volume)s, %(rsi_14)s, %(macd)s,
                    %(macd_signal)s, %(macd_histogram)s, %(bb_upper)s,
                    %(bb_middle)s, %(bb_lower)s, %(ema_8)s, %(ema_21)s,
                    %(ema_50)s, %(adx)s, %(atr_14)s, %(std_dev_20)s,
                    %(roc_1)s, %(roc_5)s, %(spread)s, %(liquidity_score)s
                )
            """, snapshot_data)

            self.conn.commit()
            cursor.close()

        except Exception as e:
            print(f"❌ Error logging market snapshot: {e}")
            if self.conn:
                self.conn.rollback()

    def log_strategy_performance(self, strategy_name: str, metrics: Dict):
        """Log strategy performance metrics"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO strategy_performance (
                    strategy_name, measurement_time, total_trades, wins, losses,
                    win_rate, total_pnl, avg_profit_per_trade, max_profit, max_loss,
                    sharpe_ratio, sortino_ratio, max_drawdown, kelly_fraction,
                    avg_confidence, confidence_calibration, current_streak,
                    max_win_streak, max_loss_streak, trades_per_hour
                ) VALUES (
                    %(strategy_name)s, NOW(), %(total_trades)s, %(wins)s,
                    %(losses)s, %(win_rate)s, %(total_pnl)s,
                    %(avg_profit_per_trade)s, %(max_profit)s, %(max_loss)s,
                    %(sharpe_ratio)s, %(sortino_ratio)s, %(max_drawdown)s,
                    %(kelly_fraction)s, %(avg_confidence)s,
                    %(confidence_calibration)s, %(current_streak)s,
                    %(max_win_streak)s, %(max_loss_streak)s, %(trades_per_hour)s
                )
            """, {**metrics, 'strategy_name': strategy_name})

            self.conn.commit()
            cursor.close()

        except Exception as e:
            print(f"❌ Error logging strategy performance: {e}")
            if self.conn:
                self.conn.rollback()

    def generate_weekly_analysis(self) -> Dict:
        """Generate comprehensive weekly analysis for strategy selection and AI training"""
        try:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Get week boundaries
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            # Overall performance
            cursor.execute("""
                SELECT
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                    AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) as win_rate,
                    SUM(profit) as total_pnl,
                    AVG(volatility) as avg_volatility
                FROM trades_ai
                WHERE entry_time BETWEEN %s AND %s
            """, (start_date, end_date))

            overall = cursor.fetchone()

            # Best performing strategy
            cursor.execute("""
                SELECT
                    strategy_name,
                    COUNT(*) as trades,
                    AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) as win_rate,
                    SUM(profit) as total_pnl
                FROM trades_ai
                WHERE entry_time BETWEEN %s AND %s
                GROUP BY strategy_name
                ORDER BY win_rate DESC, total_pnl DESC
                LIMIT 1
            """, (start_date, end_date))

            best_strategy = cursor.fetchone()

            # Most profitable instrument
            cursor.execute("""
                SELECT
                    instrument,
                    COUNT(*) as trades,
                    SUM(profit) as total_pnl
                FROM trades_ai
                WHERE entry_time BETWEEN %s AND %s
                GROUP BY instrument
                ORDER BY total_pnl DESC
                LIMIT 1
            """, (start_date, end_date))

            best_instrument = cursor.fetchone()

            # Most common market condition
            cursor.execute("""
                SELECT
                    market_condition,
                    COUNT(*) as occurrences
                FROM trades_ai
                WHERE entry_time BETWEEN %s AND %s
                GROUP BY market_condition
                ORDER BY occurrences DESC
                LIMIT 1
            """, (start_date, end_date))

            common_condition = cursor.fetchone()

            # Recommended strategies (win rate > 60% and > 10 trades)
            cursor.execute("""
                SELECT
                    strategy_name,
                    COUNT(*) as trades,
                    AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) as win_rate,
                    SUM(profit) as total_pnl
                FROM trades_ai
                WHERE entry_time BETWEEN %s AND %s
                GROUP BY strategy_name
                HAVING COUNT(*) >= 10 AND AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) >= 0.60
                ORDER BY win_rate DESC, total_pnl DESC
            """, (start_date, end_date))

            recommended = cursor.fetchall()

            # Data completeness check
            cursor.execute("""
                SELECT
                    COUNT(*) as total_records,
                    SUM(CASE WHEN exit_price IS NULL THEN 1 ELSE 0 END) as missing_exit,
                    SUM(CASE WHEN result IS NULL THEN 1 ELSE 0 END) as missing_result
                FROM trades_ai
                WHERE entry_time BETWEEN %s AND %s
            """, (start_date, end_date))

            data_quality = cursor.fetchone()

            # Calculate data completeness
            if data_quality['total_records'] > 0:
                completeness = 1.0 - (
                    (data_quality['missing_exit'] + data_quality['missing_result']) /
                    (data_quality['total_records'] * 2)
                )
            else:
                completeness = 0.0

            # Save to database
            cursor.execute("""
                INSERT INTO weekly_analysis (
                    week_start, week_end, total_trades, win_rate, total_pnl,
                    best_strategy, best_strategy_win_rate, best_instrument,
                    most_common_condition, avg_volatility, recommended_strategies,
                    ai_training_readiness, data_completeness,
                    missing_data_count, analysis_complete
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE
                )
            """, (
                start_date.date(), end_date.date(),
                overall['total_trades'], overall['win_rate'], overall['total_pnl'],
                best_strategy['strategy_name'] if best_strategy else None,
                best_strategy['win_rate'] if best_strategy else None,
                best_instrument['instrument'] if best_instrument else None,
                common_condition['market_condition'] if common_condition else None,
                overall['avg_volatility'],
                json.dumps([dict(r) for r in recommended]),
                completeness > 0.95,
                completeness,
                data_quality['missing_exit'] + data_quality['missing_result']
            ))

            self.conn.commit()
            cursor.close()

            return {
                'week_start': start_date.isoformat(),
                'week_end': end_date.isoformat(),
                'overall_performance': dict(overall),
                'best_strategy': dict(best_strategy) if best_strategy else None,
                'best_instrument': dict(best_instrument) if best_instrument else None,
                'common_condition': dict(common_condition) if common_condition else None,
                'recommended_strategies': [dict(r) for r in recommended],
                'data_quality': {
                    'completeness': completeness,
                    'total_records': data_quality['total_records'],
                    'missing_data': data_quality['missing_exit'] + data_quality['missing_result']
                },
                'ai_training_ready': completeness > 0.95 and overall['total_trades'] >= 100
            }

        except Exception as e:
            print(f"❌ Error generating weekly analysis: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def export_training_dataset(self, output_path: str, weeks: int = 4):
        """Export structured dataset for AI model training"""
        try:
            cursor = self.conn.cursor()

            # Get data from last N weeks
            start_date = datetime.now() - timedelta(weeks=weeks)

            cursor.execute("""
                SELECT
                    trade_id, strategy_name, instrument, direction,
                    confidence, payout_ratio,
                    volatility, trend_strength, trend_direction,
                    rsi, macd, macd_signal, bollinger_position,
                    momentum_1m, momentum_5m, volume_ratio,
                    seconds_to_minute, entry_timing_quality,
                    market_condition, day_of_week, hour_of_day,
                    result, profit, feature_vector
                FROM trades_ai
                WHERE entry_time >= %s
                    AND result IS NOT NULL
                ORDER BY entry_time
            """, (start_date,))

            rows = cursor.fetchall()
            cursor.close()

            if not rows:
                print("⚠️ No data available for export")
                return False

            # Convert to DataFrame
            columns = [
                'trade_id', 'strategy_name', 'instrument', 'direction',
                'confidence', 'payout_ratio', 'volatility', 'trend_strength',
                'trend_direction', 'rsi', 'macd', 'macd_signal',
                'bollinger_position', 'momentum_1m', 'momentum_5m',
                'volume_ratio', 'seconds_to_minute', 'entry_timing_quality',
                'market_condition', 'day_of_week', 'hour_of_day',
                'result', 'profit', 'feature_vector'
            ]

            df = pd.DataFrame(rows, columns=columns)

            # Export to multiple formats
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # CSV for easy viewing
            df.to_csv(f"{output_path}.csv", index=False)

            # Parquet for efficient storage
            df.to_parquet(f"{output_path}.parquet", index=False)

            # JSON for web applications
            df.to_json(f"{output_path}.json", orient='records', indent=2)

            print(f"✅ Training dataset exported: {len(df)} records")
            print(f"   - CSV: {output_path}.csv")
            print(f"   - Parquet: {output_path}.parquet")
            print(f"   - JSON: {output_path}.json")

            return True

        except Exception as e:
            print(f"❌ Error exporting training dataset: {e}")
            return False

    def validate_data_integrity(self) -> Dict:
        """Validate data integrity and completeness"""
        try:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            validation_results = {}

            # Check for duplicate trade IDs
            cursor.execute("""
                SELECT trade_id, COUNT(*) as count
                FROM trades_ai
                GROUP BY trade_id
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            validation_results['duplicates'] = len(duplicates)

            # Check for missing exit data
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM trades_ai
                WHERE entry_time < NOW() - INTERVAL '2 minutes'
                    AND exit_time IS NULL
            """)
            missing_exit = cursor.fetchone()
            validation_results['missing_exit_data'] = missing_exit['count']

            # Check for missing result data
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM trades_ai
                WHERE exit_time IS NOT NULL
                    AND result IS NULL
            """)
            missing_result = cursor.fetchone()
            validation_results['missing_result_data'] = missing_result['count']

            # Check for invalid values
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM trades_ai
                WHERE confidence < 0 OR confidence > 1
                    OR payout_ratio < 0 OR payout_ratio > 2
                    OR rsi < 0 OR rsi > 100
            """)
            invalid_values = cursor.fetchone()
            validation_results['invalid_values'] = invalid_values['count']

            # Overall health score
            total_issues = sum(validation_results.values())
            validation_results['health_score'] = 1.0 if total_issues == 0 else max(0, 1.0 - (total_issues / 100))

            cursor.close()

            return validation_results

        except Exception as e:
            print(f"❌ Error validating data integrity: {e}")
            return {'error': str(e)}

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
