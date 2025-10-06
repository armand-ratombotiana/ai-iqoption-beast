-- ============================================================================
-- ADVANCED TRADING DATABASE SCHEMA FOR AI MODEL TRAINING
-- PostgreSQL/TimescaleDB Optimized
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- 1. CORE TABLES
-- ============================================================================

-- Main trades table (TimescaleDB hypertable for time-series)
CREATE TABLE IF NOT EXISTS trades (
    trade_id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Trade Details
    pair VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK(direction IN ('CALL', 'PUT')),
    amount DECIMAL(10,2) NOT NULL,
    duration INTEGER NOT NULL,
    result VARCHAR(10) CHECK(result IN ('WIN', 'LOSS', 'PENDING', 'CANCELLED')),
    profit DECIMAL(10,2),

    -- Entry & Exit
    entry_price DECIMAL(20,8),
    exit_price DECIMAL(20,8),
    price_change DECIMAL(20,8),
    price_change_percent DECIMAL(10,4),

    -- AI Consensus
    ai_signal_confidence INTEGER,
    ai_model_agreement DECIMAL(5,2),
    ai_models_count INTEGER,
    consensus_method VARCHAR(50),

    -- Pre-Trade Technical Indicators (50+ fields for ML training)
    rsi_14 DECIMAL(10,4),
    rsi_7 DECIMAL(10,4),
    rsi_21 DECIMAL(10,4),
    macd_value DECIMAL(20,8),
    macd_signal DECIMAL(20,8),
    macd_histogram DECIMAL(20,8),
    bb_upper DECIMAL(20,8),
    bb_middle DECIMAL(20,8),
    bb_lower DECIMAL(20,8),
    bb_position DECIMAL(5,4),
    bb_width DECIMAL(20,8),
    ema_12 DECIMAL(20,8),
    ema_26 DECIMAL(20,8),
    ema_50 DECIMAL(20,8),
    ema_200 DECIMAL(20,8),
    sma_20 DECIMAL(20,8),
    sma_50 DECIMAL(20,8),
    sma_100 DECIMAL(20,8),
    sma_200 DECIMAL(20,8),
    atr_14 DECIMAL(20,8),
    atr_20 DECIMAL(20,8),
    stochastic_k DECIMAL(10,4),
    stochastic_d DECIMAL(10,4),
    stochastic_slow_k DECIMAL(10,4),
    stochastic_slow_d DECIMAL(10,4),
    adx DECIMAL(10,4),
    adx_di_plus DECIMAL(10,4),
    adx_di_minus DECIMAL(10,4),
    cci_14 DECIMAL(10,4),
    cci_20 DECIMAL(10,4),
    williams_r_14 DECIMAL(10,4),
    roc_12 DECIMAL(10,4),
    roc_25 DECIMAL(10,4),
    momentum_10 DECIMAL(20,8),
    momentum_20 DECIMAL(20,8),

    -- Volume Indicators
    volume BIGINT,
    volume_ma_20 DECIMAL(20,2),
    volume_ma_50 DECIMAL(20,2),
    volume_ratio DECIMAL(10,4),
    obv BIGINT,
    mfi DECIMAL(10,4),

    -- Market Analysis
    trend VARCHAR(20),
    trend_strength DECIMAL(5,2),
    volatility VARCHAR(20),
    volatility_value DECIMAL(10,4),
    support_level DECIMAL(20,8),
    resistance_level DECIMAL(20,8),
    support_distance DECIMAL(10,4),
    resistance_distance DECIMAL(10,4),

    -- Patterns
    candlestick_pattern VARCHAR(50),
    chart_pattern VARCHAR(50),
    harmonic_pattern VARCHAR(50),

    -- Time Context
    hour_of_day INTEGER,
    day_of_week INTEGER,
    day_of_month INTEGER,
    week_of_year INTEGER,
    month INTEGER,
    quarter INTEGER,
    is_market_open BOOLEAN,
    market_session VARCHAR(20),
    time_to_market_close INTEGER,

    -- Market Regime (ML predicted)
    market_regime VARCHAR(30),
    regime_confidence DECIMAL(5,2),
    regime_change_probability DECIMAL(5,2),

    -- Post-Trade Analysis
    highest_price DECIMAL(20,8),
    lowest_price DECIMAL(20,8),
    price_range DECIMAL(20,8),
    actual_direction VARCHAR(10),
    prediction_correct BOOLEAN,

    -- Post-Trade Indicators
    rsi_14_post DECIMAL(10,4),
    macd_value_post DECIMAL(20,8),
    trend_post VARCHAR(20),
    volatility_post DECIMAL(10,4),

    -- Risk Metrics
    risk_reward_ratio DECIMAL(10,4),
    max_adverse_excursion DECIMAL(10,4),
    max_favorable_excursion DECIMAL(10,4),
    drawdown_at_entry DECIMAL(10,4),

    -- External Factors
    news_sentiment DECIMAL(5,2),
    economic_calendar_event BOOLEAN,
    correlation_spy DECIMAL(5,4),
    correlation_vix DECIMAL(5,4),

    -- Metadata
    strategy_version VARCHAR(20),
    model_version VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (timestamp, trade_id)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('trades', 'timestamp', if_not_exists => TRUE, chunk_time_interval => interval '1 day');

-- Create indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_result ON trades(result) WHERE result IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_trades_regime ON trades(market_regime, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_pattern ON trades(candlestick_pattern) WHERE candlestick_pattern IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_trades_hour ON trades(hour_of_day, day_of_week);
CREATE INDEX IF NOT EXISTS idx_trades_ml_training ON trades(result, prediction_correct) WHERE result IN ('WIN', 'LOSS');

-- ============================================================================
-- 2. AI MODEL TABLES
-- ============================================================================

-- AI Model Registry
CREATE TABLE IF NOT EXISTS ai_models (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) UNIQUE NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- LLM, ML, DL, Ensemble
    provider VARCHAR(50),
    version VARCHAR(20),
    cost_per_request DECIMAL(10,6),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Model Predictions (every prediction from every model)
CREATE TABLE IF NOT EXISTS ai_predictions (
    prediction_id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trade_id BIGINT NOT NULL,
    model_id INTEGER REFERENCES ai_models(model_id),

    signal VARCHAR(10) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    reasoning TEXT,

    -- Feature importance (JSON for flexibility)
    feature_importance JSONB,

    -- Prediction metadata
    inference_time_ms INTEGER,
    tokens_used INTEGER,
    cost DECIMAL(10,6),

    was_correct BOOLEAN,
    contribution_to_consensus DECIMAL(5,4),

    PRIMARY KEY (timestamp, prediction_id)
);

SELECT create_hypertable('ai_predictions', 'timestamp', if_not_exists => TRUE);
CREATE INDEX idx_predictions_model ON ai_predictions(model_id, timestamp DESC);
CREATE INDEX idx_predictions_trade ON ai_predictions(trade_id);

-- AI Model Performance Tracking (aggregated stats)
CREATE TABLE IF NOT EXISTS ai_model_performance (
    performance_id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES ai_models(model_id),
    timestamp TIMESTAMPTZ NOT NULL,
    time_window VARCHAR(20), -- hourly, daily, weekly

    -- Performance Metrics
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy DECIMAL(5,2),
    precision_score DECIMAL(5,2),
    recall DECIMAL(5,2),
    f1_score DECIMAL(5,2),

    -- By Market Condition
    accuracy_bull DECIMAL(5,2),
    accuracy_bear DECIMAL(5,2),
    accuracy_sideways DECIMAL(5,2),
    accuracy_high_vol DECIMAL(5,2),
    accuracy_low_vol DECIMAL(5,2),

    -- Financial Metrics
    total_profit DECIMAL(10,2),
    avg_profit DECIMAL(10,2),
    sharpe_ratio DECIMAL(10,4),
    win_rate DECIMAL(5,2),

    -- Confidence Calibration
    avg_confidence DECIMAL(5,2),
    confidence_accuracy_gap DECIMAL(5,2),

    -- Model Weight
    current_weight DECIMAL(5,2),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_model_perf_time ON ai_model_performance(model_id, timestamp DESC);

-- ============================================================================
-- 3. MARKET DATA TABLES (For Training)
-- ============================================================================

-- Candle Data (OHLCV) - TimescaleDB
CREATE TABLE IF NOT EXISTS candles (
    candle_id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    pair VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- 1m, 5m, 15m, 1h, 4h, 1d

    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume BIGINT,

    -- Derived metrics
    body_size DECIMAL(20,8),
    wick_upper DECIMAL(20,8),
    wick_lower DECIMAL(20,8),
    is_bullish BOOLEAN,

    PRIMARY KEY (timestamp, pair, timeframe)
);

SELECT create_hypertable('candles', 'timestamp', if_not_exists => TRUE);
CREATE INDEX idx_candles_pair_tf ON candles(pair, timeframe, timestamp DESC);

-- Continuous aggregates for faster queries
CREATE MATERIALIZED VIEW IF NOT EXISTS candles_5m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', timestamp) AS bucket,
    pair,
    first(open, timestamp) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, timestamp) AS close,
    sum(volume) AS volume
FROM candles
WHERE timeframe = '1m'
GROUP BY bucket, pair;

-- Market Regime History (for pattern learning)
CREATE TABLE IF NOT EXISTS market_regimes (
    regime_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    pair VARCHAR(20) NOT NULL,

    regime_type VARCHAR(30) NOT NULL,
    confidence DECIMAL(5,2),
    duration_minutes INTEGER,

    -- Transition probabilities (ML predicted)
    prob_to_bull DECIMAL(5,4),
    prob_to_bear DECIMAL(5,4),
    prob_to_sideways DECIMAL(5,4),
    prob_to_high_vol DECIMAL(5,4),

    -- Characteristics
    avg_volatility DECIMAL(10,4),
    avg_volume BIGINT,
    dominant_pattern VARCHAR(50)
);

CREATE INDEX idx_regimes_time ON market_regimes(timestamp DESC);
CREATE INDEX idx_regimes_pair ON market_regimes(pair, timestamp DESC);

-- ============================================================================
-- 4. FEATURE STORE (For ML Training)
-- ============================================================================

-- Pre-computed features for fast ML training
CREATE TABLE IF NOT EXISTS ml_features (
    feature_id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    pair VARCHAR(20) NOT NULL,

    -- Feature vector (100+ features)
    feature_vector JSONB NOT NULL,

    -- Labels for supervised learning
    label_5min VARCHAR(10), -- CALL, PUT, NEUTRAL
    label_15min VARCHAR(10),
    label_1h VARCHAR(10),

    -- Actual outcomes (for training)
    actual_5min VARCHAR(10),
    actual_15min VARCHAR(10),
    actual_1h VARCHAR(10),

    -- Feature metadata
    feature_version INTEGER,
    is_training_data BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_ml_features_time ON ml_features(timestamp DESC);
CREATE INDEX idx_ml_features_pair ON ml_features(pair, timestamp DESC);
CREATE INDEX idx_ml_features_label ON ml_features(label_5min) WHERE is_training_data = TRUE;

-- Feature importance tracking
CREATE TABLE IF NOT EXISTS feature_importance (
    feature_name VARCHAR(100) PRIMARY KEY,
    importance_score DECIMAL(10,6),
    model_type VARCHAR(50),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. PERFORMANCE & ANALYTICS TABLES
-- ============================================================================

-- Daily Performance Summary
CREATE TABLE IF NOT EXISTS daily_performance (
    date DATE PRIMARY KEY,

    total_trades INTEGER,
    wins INTEGER,
    losses INTEGER,
    win_rate DECIMAL(5,2),

    total_profit DECIMAL(10,2),
    total_loss DECIMAL(10,2),
    net_profit DECIMAL(10,2),

    avg_profit DECIMAL(10,2),
    max_profit DECIMAL(10,2),
    max_loss DECIMAL(10,2),

    sharpe_ratio DECIMAL(10,4),
    sortino_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,2),
    max_drawdown_pct DECIMAL(5,2),

    best_pair VARCHAR(20),
    best_hour INTEGER,
    best_regime VARCHAR(30),

    notes TEXT
);

-- Pattern Performance (winning patterns)
CREATE TABLE IF NOT EXISTS pattern_performance (
    pattern_id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_conditions JSONB NOT NULL,

    occurrences INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),

    avg_profit DECIMAL(10,2),
    total_profit DECIMAL(10,2),

    confidence_level DECIMAL(5,2),
    last_seen TIMESTAMPTZ,

    UNIQUE(pattern_type, pattern_conditions)
);

-- Backtesting Results
CREATE TABLE IF NOT EXISTS backtest_results (
    backtest_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    strategy_name VARCHAR(100),
    strategy_params JSONB,

    date_from DATE,
    date_to DATE,
    total_trades INTEGER,

    win_rate DECIMAL(5,2),
    total_profit DECIMAL(10,2),
    sharpe_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,2),

    detailed_results JSONB
);

-- ============================================================================
-- 6. TRIGGERS & FUNCTIONS
-- ============================================================================

-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trades_updated_at BEFORE UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-calculate trade metrics
CREATE OR REPLACE FUNCTION calculate_trade_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate price change
    IF NEW.exit_price IS NOT NULL AND NEW.entry_price IS NOT NULL THEN
        NEW.price_change = NEW.exit_price - NEW.entry_price;
        NEW.price_change_percent = (NEW.price_change / NEW.entry_price) * 100;

        -- Determine if prediction was correct
        NEW.actual_direction = CASE
            WHEN NEW.price_change > 0 THEN 'CALL'
            WHEN NEW.price_change < 0 THEN 'PUT'
            ELSE 'NEUTRAL'
        END;

        NEW.prediction_correct = (NEW.direction = NEW.actual_direction);
    END IF;

    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_metrics BEFORE INSERT OR UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION calculate_trade_metrics();

-- ============================================================================
-- 7. MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- Real-time model performance view
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_model_performance_realtime AS
SELECT
    m.model_name,
    m.model_type,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN p.was_correct = TRUE THEN 1 ELSE 0 END) as correct,
    ROUND(AVG(CASE WHEN p.was_correct = TRUE THEN 100.0 ELSE 0.0 END), 2) as accuracy,
    ROUND(AVG(p.confidence), 2) as avg_confidence,
    SUM(p.cost) as total_cost
FROM ai_models m
JOIN ai_predictions p ON m.model_id = p.model_id
WHERE p.timestamp > NOW() - INTERVAL '7 days'
GROUP BY m.model_id, m.model_name, m.model_type;

CREATE UNIQUE INDEX ON mv_model_performance_realtime(model_name);

-- Winning patterns view
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_winning_patterns AS
SELECT
    trend,
    market_regime,
    hour_of_day,
    COUNT(*) as trades,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(AVG(profit), 2) as avg_profit
FROM trades
WHERE result IN ('WIN', 'LOSS')
    AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY trend, market_regime, hour_of_day
HAVING COUNT(*) >= 5;

-- Refresh policy for materialized views
SELECT add_continuous_aggregate_policy('candles_5m',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE);

-- ============================================================================
-- 8. DATA RETENTION POLICIES
-- ============================================================================

-- Keep raw candles for 90 days, aggregated for 1 year
SELECT add_retention_policy('candles', INTERVAL '90 days', if_not_exists => TRUE);

-- Keep predictions for 180 days
SELECT add_retention_policy('ai_predictions', INTERVAL '180 days', if_not_exists => TRUE);

-- ============================================================================
-- 9. OPTIMIZATION
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE trades;
ANALYZE ai_predictions;
ANALYZE candles;

-- Vacuum to reclaim storage
VACUUM ANALYZE;
