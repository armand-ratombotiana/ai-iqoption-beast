-- ============================================================================
-- KAEL Trading System - Comprehensive Database Schema
-- Following PROJECT_FOCUS_GUIDELINES: "Log everything"
-- ============================================================================

-- Main Trades Table
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT UNIQUE NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Instrument & Direction
    instrument TEXT NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('CALL', 'PUT')),

    -- Trade Details
    amount REAL NOT NULL,
    duration INTEGER NOT NULL,  -- seconds
    payout_ratio REAL NOT NULL,

    -- Timing
    entry_time DATETIME NOT NULL,
    expiration_time DATETIME NOT NULL,
    execution_time_ms INTEGER,  -- milliseconds from signal to execution

    -- Results
    result TEXT CHECK(result IN ('WIN', 'LOSS', 'DRAW', 'PENDING', 'FAILED')),
    profit REAL DEFAULT 0.0,
    exit_time DATETIME,

    -- Market Data at Entry
    entry_price REAL,
    exit_price REAL,
    price_change REAL,

    -- System Info
    mode TEXT NOT NULL CHECK(mode IN ('demo', 'live')),
    balance_before REAL,
    balance_after REAL,

    -- Metadata
    notes TEXT,
    -- Strategy info
    selected_strategy TEXT,
    strategy_breakdown TEXT, -- JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI Predictions Table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Model Info
    model_name TEXT NOT NULL,
    model_version TEXT,

    -- Prediction
    direction TEXT NOT NULL CHECK(direction IN ('CALL', 'PUT', 'NEUTRAL')),
    confidence REAL NOT NULL,  -- 0-100
    signal_strength REAL,

    -- Reasoning
    primary_indicator TEXT,
    indicators_used TEXT,  -- JSON array
    reasoning TEXT,

    -- Consensus
    is_consensus BOOLEAN DEFAULT FALSE,
    consensus_weight REAL DEFAULT 1.0,

    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);

-- Market Context Table
CREATE TABLE IF NOT EXISTS market_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Candlestick Data (last 5 candles)
    candles_1m TEXT,  -- JSON: [{open, high, low, close, volume}]
    candles_5m TEXT,
    candles_15m TEXT,

    -- Technical Indicators
    rsi_14 REAL,
    rsi_7 REAL,
    macd_value REAL,
    macd_signal REAL,
    macd_histogram REAL,

    -- Bollinger Bands
    bb_upper REAL,
    bb_middle REAL,
    bb_lower REAL,
    bb_width REAL,

    -- Volatility
    atr_14 REAL,
    historical_volatility REAL,

    -- Volume
    volume_current REAL,
    volume_avg_20 REAL,
    volume_ratio REAL,

    -- Trend
    ema_9 REAL,
    ema_21 REAL,
    ema_50 REAL,
    trend_direction TEXT CHECK(trend_direction IN ('UP', 'DOWN', 'SIDEWAYS')),
    trend_strength REAL,

    -- Support/Resistance
    support_level REAL,
    resistance_level REAL,
    distance_to_support REAL,
    distance_to_resistance REAL,

    -- Market Session
    session TEXT CHECK(session IN ('ASIAN', 'EUROPEAN', 'US', 'OVERLAP')),
    is_high_impact_news BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Time Period
    period_type TEXT NOT NULL CHECK(period_type IN ('HOURLY', 'DAILY', 'WEEKLY', 'MONTHLY')),
    period_start DATETIME NOT NULL,
    period_end DATETIME NOT NULL,

    -- Trade Counts
    total_trades INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,

    -- Win Rate
    win_rate REAL,  -- percentage

    -- Profit/Loss
    gross_profit REAL DEFAULT 0.0,
    gross_loss REAL DEFAULT 0.0,
    net_profit REAL DEFAULT 0.0,

    -- Per Instrument
    instrument TEXT,

    -- Risk Metrics
    max_drawdown REAL,
    sharpe_ratio REAL,
    profit_factor REAL,

    -- AI Performance
    avg_ai_confidence REAL,
    confidence_accuracy_correlation REAL
);

-- System Events Table (for monitoring)
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    event_type TEXT NOT NULL CHECK(event_type IN
        ('CONNECTION', 'DISCONNECTION', 'ERROR', 'WARNING', 'RECONNECT', 'RATE_LIMIT', 'STARTUP', 'SHUTDOWN')),

    severity TEXT CHECK(severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),

    message TEXT NOT NULL,
    details TEXT,  -- JSON

    -- System State
    balance REAL,
    active_trades INTEGER,
    uptime_seconds INTEGER
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_instrument ON trades(instrument);
CREATE INDEX IF NOT EXISTS idx_trades_result ON trades(result);
CREATE INDEX IF NOT EXISTS idx_trades_trade_id ON trades(trade_id);

CREATE INDEX IF NOT EXISTS idx_ai_predictions_trade_id ON ai_predictions(trade_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_model ON ai_predictions(model_name);

CREATE INDEX IF NOT EXISTS idx_market_context_trade_id ON market_context(trade_id);

CREATE INDEX IF NOT EXISTS idx_performance_period ON performance_metrics(period_type, period_start);
CREATE INDEX IF NOT EXISTS idx_performance_instrument ON performance_metrics(instrument);

CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);

-- Triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_trades_timestamp
AFTER UPDATE ON trades
BEGIN
    UPDATE trades SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- Views for Easy Querying
-- ============================================================================

-- Recent Trades View
-- Replaceable recent trades view (includes selected strategy)
DROP VIEW IF EXISTS v_recent_trades;
CREATE VIEW v_recent_trades AS
SELECT
    t.trade_id,
    t.timestamp,
    t.instrument,
    t.direction,
    t.amount,
    t.payout_ratio,
    t.result,
    t.profit,
    t.execution_time_ms,
    t.selected_strategy,
    t.strategy_breakdown,
    (SELECT AVG(confidence) FROM ai_predictions WHERE trade_id = t.trade_id) as avg_ai_confidence,
    (SELECT COUNT(*) FROM ai_predictions WHERE trade_id = t.trade_id) as model_count
FROM trades t
ORDER BY t.timestamp DESC
LIMIT 100;

-- Instrument Performance View
CREATE VIEW IF NOT EXISTS v_instrument_performance AS
SELECT
    instrument,
    COUNT(*) as total_trades,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
    ROUND(100.0 * SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(profit), 2) as net_profit,
    ROUND(AVG(profit), 2) as avg_profit_per_trade,
    ROUND(AVG(payout_ratio), 2) as avg_payout_ratio
FROM trades
WHERE result IN ('WIN', 'LOSS')
GROUP BY instrument
ORDER BY net_profit DESC;

-- AI Model Performance View
CREATE VIEW IF NOT EXISTS v_ai_model_performance AS
SELECT
    ap.model_name,
    COUNT(DISTINCT ap.trade_id) as predictions_made,
    AVG(ap.confidence) as avg_confidence,
    COUNT(DISTINCT CASE WHEN t.result = 'WIN' AND ap.direction = t.direction THEN t.trade_id END) as correct_predictions,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN t.result = 'WIN' AND ap.direction = t.direction THEN t.trade_id END) /
          COUNT(DISTINCT ap.trade_id), 2) as accuracy
FROM ai_predictions ap
JOIN trades t ON ap.trade_id = t.trade_id
WHERE t.result IN ('WIN', 'LOSS')
GROUP BY ap.model_name
ORDER BY accuracy DESC;

-- ============================================================================
-- End of Schema
-- ============================================================================
