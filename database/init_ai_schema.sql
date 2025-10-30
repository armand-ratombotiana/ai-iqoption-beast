-- ============================================================================
-- KAEL AI DATA COLLECTION SCHEMA
-- Comprehensive database schema for AI model training data
-- ============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- TRADES AI TABLE - Enhanced trade data for ML training
-- ============================================================================
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

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('trades_ai', 'entry_time', if_not_exists => TRUE);

-- ============================================================================
-- MARKET SNAPSHOTS - Historical market data for analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_time TIMESTAMP NOT NULL,
    instrument VARCHAR(50) NOT NULL,

    -- Price data
    current_price DECIMAL(20, 8) NOT NULL,
    price_change_1m DECIMAL(10, 8),
    price_change_5m DECIMAL(10, 8),
    price_change_15m DECIMAL(10, 8),

    -- Technical indicators
    rsi DECIMAL(10, 4),
    macd DECIMAL(20, 8),
    macd_signal DECIMAL(20, 8),
    macd_histogram DECIMAL(20, 8),
    bollinger_upper DECIMAL(20, 8),
    bollinger_middle DECIMAL(20, 8),
    bollinger_lower DECIMAL(20, 8),
    atr DECIMAL(20, 8),

    -- Volume
    volume_1m DECIMAL(20, 8),
    volume_5m DECIMAL(20, 8),
    volume_ratio DECIMAL(10, 4),

    -- Trend
    trend_direction INTEGER,
    trend_strength DECIMAL(10, 4),

    -- Market condition
    volatility DECIMAL(10, 8),
    market_condition VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('market_snapshots', 'snapshot_time', if_not_exists => TRUE);

-- ============================================================================
-- STRATEGY PERFORMANCE - Aggregated strategy metrics
-- ============================================================================
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Trade counts
    total_trades INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,

    -- Performance metrics
    win_rate DECIMAL(5, 2),
    total_profit DECIMAL(10, 2),
    avg_profit_per_trade DECIMAL(10, 2),
    sharpe_ratio DECIMAL(10, 4),
    kelly_fraction DECIMAL(10, 4),

    -- Risk metrics
    max_consecutive_losses INTEGER,
    max_drawdown DECIMAL(10, 4),
    volatility DECIMAL(10, 8),

    -- Confidence metrics
    avg_confidence DECIMAL(5, 2),
    confidence_multiplier DECIMAL(10, 4),

    created_at TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('strategy_performance', 'timestamp', if_not_exists => TRUE);

-- ============================================================================
-- FEATURE SETS - Pre-computed features for ML
-- ============================================================================
CREATE TABLE IF NOT EXISTS ml_features (
    id SERIAL PRIMARY KEY,
    feature_set_time TIMESTAMP NOT NULL,
    instrument VARCHAR(50) NOT NULL,

    -- Technical features (normalized)
    rsi_norm DECIMAL(10, 8),
    macd_norm DECIMAL(10, 8),
    macd_signal_norm DECIMAL(10, 8),
    bollinger_position DECIMAL(10, 8),
    atr_norm DECIMAL(10, 8),

    -- Momentum features
    momentum_1m DECIMAL(10, 8),
    momentum_5m DECIMAL(10, 8),
    momentum_15m DECIMAL(10, 8),

    -- Volume features
    volume_ratio DECIMAL(10, 8),
    volume_trend DECIMAL(10, 8),

    -- Trend features
    trend_direction INTEGER,
    trend_strength DECIMAL(10, 8),

    -- Time features
    hour_sin DECIMAL(10, 8),
    hour_cos DECIMAL(10, 8),
    day_sin DECIMAL(10, 8),
    day_cos DECIMAL(10, 8),

    -- Target (for supervised learning)
    target_direction INTEGER,  -- 1 for CALL, -1 for PUT, 0 for no trade
    target_confidence DECIMAL(10, 8),

    created_at TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('ml_features', 'feature_set_time', if_not_exists => TRUE);

-- ============================================================================
-- INDEXES for performance
-- ============================================================================

-- Trades AI indexes
CREATE INDEX IF NOT EXISTS idx_trades_ai_strategy ON trades_ai(strategy_name);
CREATE INDEX IF NOT EXISTS idx_trades_ai_instrument ON trades_ai(instrument);
CREATE INDEX IF NOT EXISTS idx_trades_ai_result ON trades_ai(result);
CREATE INDEX IF NOT EXISTS idx_trades_ai_entry_time ON trades_ai(entry_time DESC);

-- Market snapshots indexes
CREATE INDEX IF NOT EXISTS idx_market_snapshots_instrument ON market_snapshots(instrument);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_time ON market_snapshots(snapshot_time DESC);

-- Strategy performance indexes
CREATE INDEX IF NOT EXISTS idx_strategy_performance_name ON strategy_performance(strategy_name);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_time ON strategy_performance(timestamp DESC);

-- ML features indexes
CREATE INDEX IF NOT EXISTS idx_ml_features_instrument ON ml_features(instrument);
CREATE INDEX IF NOT EXISTS idx_ml_features_time ON ml_features(feature_set_time DESC);

-- ============================================================================
-- CONTINUOUS AGGREGATES for real-time analytics
-- ============================================================================

-- Hourly strategy performance
CREATE MATERIALIZED VIEW IF NOT EXISTS strategy_performance_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', entry_time) AS hour,
    strategy_name,
    instrument,
    COUNT(*) as trade_count,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
    AVG(CASE WHEN result = 'WIN' THEN 1.0 ELSE 0.0 END) * 100 as win_rate,
    SUM(profit) as total_profit,
    AVG(profit) as avg_profit,
    AVG(confidence) as avg_confidence,
    AVG(payout_ratio) as avg_payout
FROM trades_ai
GROUP BY hour, strategy_name, instrument;

-- Add refresh policy
SELECT add_continuous_aggregate_policy('strategy_performance_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

-- Daily market conditions
CREATE MATERIALIZED VIEW IF NOT EXISTS market_conditions_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', snapshot_time) AS day,
    instrument,
    AVG(volatility) as avg_volatility,
    AVG(rsi) as avg_rsi,
    AVG(volume_ratio) as avg_volume_ratio,
    COUNT(*) as snapshot_count
FROM market_snapshots
GROUP BY day, instrument;

SELECT add_continuous_aggregate_policy('market_conditions_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE);

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to calculate Sharpe ratio
CREATE OR REPLACE FUNCTION calculate_sharpe_ratio(
    strategy_name_param VARCHAR,
    days_param INTEGER DEFAULT 7
) RETURNS DECIMAL AS $$
DECLARE
    sharpe DECIMAL;
BEGIN
    SELECT
        CASE
            WHEN STDDEV(profit) > 0 THEN AVG(profit) / STDDEV(profit)
            ELSE 0
        END INTO sharpe
    FROM trades_ai
    WHERE strategy_name = strategy_name_param
      AND entry_time > NOW() - INTERVAL '1 day' * days_param;

    RETURN COALESCE(sharpe, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to get strategy statistics
CREATE OR REPLACE FUNCTION get_strategy_stats(
    strategy_name_param VARCHAR,
    hours_param INTEGER DEFAULT NULL
) RETURNS TABLE(
    total_trades BIGINT,
    wins BIGINT,
    losses BIGINT,
    win_rate DECIMAL,
    total_profit DECIMAL,
    avg_profit DECIMAL,
    sharpe_ratio DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END)::BIGINT,
        SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END)::BIGINT,
        AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END)::DECIMAL,
        SUM(profit)::DECIMAL,
        AVG(profit)::DECIMAL,
        calculate_sharpe_ratio(strategy_name_param, COALESCE(hours_param, 168) / 24)
    FROM trades_ai
    WHERE strategy_name = strategy_name_param
      AND (hours_param IS NULL OR entry_time > NOW() - INTERVAL '1 hour' * hours_param);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DATA RETENTION POLICIES
-- ============================================================================

-- Keep detailed trades_ai data for 90 days
SELECT add_retention_policy('trades_ai', INTERVAL '90 days', if_not_exists => TRUE);

-- Keep market snapshots for 30 days
SELECT add_retention_policy('market_snapshots', INTERVAL '30 days', if_not_exists => TRUE);

-- Keep ML features for 60 days
SELECT add_retention_policy('ml_features', INTERVAL '60 days', if_not_exists => TRUE);

-- Keep aggregated strategy performance for 1 year
SELECT add_retention_policy('strategy_performance', INTERVAL '365 days', if_not_exists => TRUE);

-- ============================================================================
-- VIEWS for easier querying
-- ============================================================================

-- Recent strategy performance view
CREATE OR REPLACE VIEW recent_strategy_performance AS
SELECT
    strategy_name,
    COUNT(*) as total_trades,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
    AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END) as win_rate,
    SUM(profit) as total_profit,
    AVG(profit) as avg_profit,
    AVG(confidence) as avg_confidence,
    AVG(payout_ratio) as avg_payout,
    MAX(entry_time) as last_trade_time
FROM trades_ai
WHERE entry_time > NOW() - INTERVAL '24 hours'
GROUP BY strategy_name
ORDER BY total_profit DESC;

-- Best trading hours view
CREATE OR REPLACE VIEW best_trading_hours AS
SELECT
    hour_of_day,
    COUNT(*) as trade_count,
    AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END) as win_rate,
    SUM(profit) as total_profit
FROM trades_ai
WHERE entry_time > NOW() - INTERVAL '7 days'
GROUP BY hour_of_day
ORDER BY win_rate DESC;

-- Market condition performance view
CREATE OR REPLACE VIEW market_condition_performance AS
SELECT
    market_condition,
    COUNT(*) as trade_count,
    AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END) as win_rate,
    SUM(profit) as total_profit
FROM trades_ai
WHERE entry_time > NOW() - INTERVAL '7 days'
  AND market_condition IS NOT NULL
GROUP BY market_condition
ORDER BY win_rate DESC;

-- ============================================================================
-- GRANTS (if using specific user)
-- ============================================================================
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kael_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kael_user;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ AI Data Collection schema initialized successfully';
    RAISE NOTICE '📊 Tables: trades_ai, market_snapshots, strategy_performance, ml_features';
    RAISE NOTICE '📈 Views: recent_strategy_performance, best_trading_hours, market_condition_performance';
    RAISE NOTICE '⚡ Continuous aggregates: strategy_performance_hourly, market_conditions_daily';
    RAISE NOTICE '🔧 Functions: calculate_sharpe_ratio(), get_strategy_stats()';
END $$;
