-- ============================================================================
-- KAEL Trading System - PostgreSQL + TimescaleDB Schema
-- ============================================================================
-- This script initializes the database schema for the trading system
-- Features: Time-series optimization, partitioning, indexes, constraints

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- Table: trades
-- Stores all executed trades with full details
-- ============================================================================
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    trade_id VARCHAR(100) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Trade Details
    asset VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('CALL', 'PUT')),
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    duration INT NOT NULL CHECK (duration > 0),

    -- Prices
    entry_price DECIMAL(12, 6),
    exit_price DECIMAL(12, 6),
    payout_rate DECIMAL(5, 4),

    -- Result
    result VARCHAR(10) CHECK (result IN ('win', 'loss', 'tie', 'pending')),
    profit_loss DECIMAL(10, 2),

    -- AI Signal Data
    ai_signal_confidence INT CHECK (ai_signal_confidence BETWEEN 0 AND 100),
    ai_consensus_score DECIMAL(5, 4),
    ai_models_agree INT,
    ai_models_total INT,

    -- Technical Indicators (at time of trade)
    rsi_14 DECIMAL(5, 2),
    macd_value DECIMAL(10, 6),
    macd_signal DECIMAL(10, 6),
    bollinger_upper DECIMAL(12, 6),
    bollinger_lower DECIMAL(12, 6),
    ema_20 DECIMAL(12, 6),
    ema_50 DECIMAL(12, 6),
    volume BIGINT,

    -- Market Context
    trend VARCHAR(20),
    volatility DECIMAL(10, 6),
    support_level DECIMAL(12, 6),
    resistance_level DECIMAL(12, 6),

    -- Time Context
    hour_of_day INT CHECK (hour_of_day BETWEEN 0 AND 23),
    day_of_week INT CHECK (day_of_week BETWEEN 0 AND 6),
    is_weekend BOOLEAN DEFAULT FALSE,

    -- Risk Management
    account_balance_before DECIMAL(12, 2),
    account_balance_after DECIMAL(12, 2),
    position_size_ratio DECIMAL(5, 4),
    kelly_fraction DECIMAL(5, 4),
    martingale_level INT DEFAULT 0,

    -- Metadata
    trading_mode VARCHAR(20) DEFAULT 'demo',
    bot_version VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('trades', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ============================================================================
-- Table: candles
-- Stores historical candle/OHLCV data
-- ============================================================================
CREATE TABLE IF NOT EXISTS candles (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    asset VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,  -- 1m, 5m, 15m, 1h, 4h, 1d

    open DECIMAL(12, 6) NOT NULL,
    high DECIMAL(12, 6) NOT NULL,
    low DECIMAL(12, 6) NOT NULL,
    close DECIMAL(12, 6) NOT NULL,
    volume BIGINT DEFAULT 0,

    -- Technical indicators (calculated)
    rsi_14 DECIMAL(5, 2),
    macd DECIMAL(10, 6),
    macd_signal DECIMAL(10, 6),
    macd_histogram DECIMAL(10, 6),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (timestamp, asset, timeframe)
);

-- Convert to hypertable
SELECT create_hypertable('candles', 'timestamp',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- Table: ai_predictions
-- Stores AI model predictions for analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_predictions (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trade_id VARCHAR(100) REFERENCES trades(trade_id),

    model_name VARCHAR(50) NOT NULL,
    prediction VARCHAR(10) NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    reasoning TEXT,

    -- Model performance
    was_correct BOOLEAN,
    execution_time_ms INT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Table: performance_metrics
-- Aggregated performance metrics
-- ============================================================================
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    period VARCHAR(20) NOT NULL,  -- hourly, daily, weekly, monthly

    -- Trading Stats
    total_trades INT DEFAULT 0,
    winning_trades INT DEFAULT 0,
    losing_trades INT DEFAULT 0,
    win_rate DECIMAL(5, 4),

    -- Financial Stats
    total_profit DECIMAL(12, 2),
    total_loss DECIMAL(12, 2),
    net_profit DECIMAL(12, 2),
    roi DECIMAL(8, 4),

    -- AI Stats
    avg_ai_confidence DECIMAL(5, 4),
    avg_consensus_score DECIMAL(5, 4),

    -- Risk Metrics
    max_drawdown DECIMAL(12, 2),
    sharpe_ratio DECIMAL(8, 4),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(timestamp, period)
);

-- Convert to hypertable
SELECT create_hypertable('performance_metrics', 'timestamp',
    chunk_time_interval => INTERVAL '30 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- Indexes for performance
-- ============================================================================

-- Trades indexes
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_asset ON trades (asset);
CREATE INDEX IF NOT EXISTS idx_trades_result ON trades (result);
CREATE INDEX IF NOT EXISTS idx_trades_trading_mode ON trades (trading_mode);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp_asset ON trades (timestamp DESC, asset);

-- Candles indexes
CREATE INDEX IF NOT EXISTS idx_candles_asset_timeframe ON candles (asset, timeframe, timestamp DESC);

-- AI predictions indexes
CREATE INDEX IF NOT EXISTS idx_ai_predictions_trade_id ON ai_predictions (trade_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_model ON ai_predictions (model_name);

-- ============================================================================
-- Continuous Aggregates (TimescaleDB feature)
-- Pre-calculated aggregations for faster queries
-- ============================================================================

-- Hourly aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS trades_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    asset,
    trading_mode,
    COUNT(*) as trade_count,
    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
    AVG(ai_signal_confidence) as avg_confidence,
    SUM(profit_loss) as total_pnl,
    AVG(amount) as avg_trade_size
FROM trades
GROUP BY bucket, asset, trading_mode
WITH NO DATA;

-- Daily aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS trades_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', timestamp) AS bucket,
    trading_mode,
    COUNT(*) as trade_count,
    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
    CAST(SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS DECIMAL) / NULLIF(COUNT(*), 0) as win_rate,
    SUM(profit_loss) as total_pnl,
    AVG(ai_signal_confidence) as avg_confidence,
    MAX(profit_loss) as best_trade,
    MIN(profit_loss) as worst_trade
FROM trades
GROUP BY bucket, trading_mode
WITH NO DATA;

-- Refresh policies for continuous aggregates
SELECT add_continuous_aggregate_policy('trades_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

SELECT add_continuous_aggregate_policy('trades_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ============================================================================
-- Retention Policies (auto-delete old data)
-- ============================================================================

-- Keep raw trade data for 1 year
SELECT add_retention_policy('trades', INTERVAL '1 year', if_not_exists => TRUE);

-- Keep candle data for 90 days
SELECT add_retention_policy('candles', INTERVAL '90 days', if_not_exists => TRUE);

-- Keep AI predictions for 6 months
-- (Note: AI predictions is not a hypertable, so we'd need a different approach)

-- ============================================================================
-- Functions
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_trades_updated_at BEFORE UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate win rate
CREATE OR REPLACE FUNCTION get_win_rate(
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
)
RETURNS DECIMAL AS $$
DECLARE
    win_rate DECIMAL;
BEGIN
    SELECT
        CAST(SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS DECIMAL) /
        NULLIF(COUNT(*), 0)
    INTO win_rate
    FROM trades
    WHERE timestamp BETWEEN start_time AND end_time
      AND result IN ('win', 'loss');

    RETURN COALESCE(win_rate, 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Initial Data / Seed
-- ============================================================================

-- Insert sample data (optional - for testing)
-- Commented out for production

-- ============================================================================
-- Grants
-- ============================================================================

-- Grant permissions to trading_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO trading_user;

-- ============================================================================
-- Completion
-- ============================================================================

-- Verify setup
DO $$
BEGIN
    RAISE NOTICE '✅ Database schema initialized successfully!';
    RAISE NOTICE '   - Tables: trades, candles, ai_predictions, performance_metrics';
    RAISE NOTICE '   - Hypertables enabled with TimescaleDB';
    RAISE NOTICE '   - Continuous aggregates configured';
    RAISE NOTICE '   - Retention policies set';
    RAISE NOTICE '   - Indexes created';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Ready to start trading!';
END $$;
