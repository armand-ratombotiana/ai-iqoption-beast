-- ============================================================================
-- Multi-Account Trading System Database Schema
-- Enhanced schema for tracking 5 accounts with different strategies
-- ============================================================================

-- Enable TimescaleDB extension if available
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- ACCOUNTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    strategy_profile VARCHAR(50) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    is_healthy BOOLEAN DEFAULT TRUE,
    trading_mode VARCHAR(10) DEFAULT 'demo',
    max_daily_loss DECIMAL(10, 2) DEFAULT 10.0,
    max_trade_amount DECIMAL(10, 2) DEFAULT 2.0,
    connection_failures INTEGER DEFAULT 0,
    last_connection TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TRADES TABLE (Enhanced with account_id)
-- ============================================================================
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL REFERENCES accounts(account_id),
    trade_id VARCHAR(100),
    instrument VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    expiration_seconds INTEGER,
    result VARCHAR(10),
    profit DECIMAL(10, 2),
    payout_ratio DECIMAL(5, 4),
    
    -- Strategy information
    selected_strategy VARCHAR(100),
    strategy_profile VARCHAR(50),
    confidence INTEGER,
    
    -- Signal details
    signal_data JSONB,
    strategy_breakdown JSONB,
    
    -- Market context
    market_conditions JSONB,
    
    -- Execution metrics
    execution_time_ms INTEGER,
    generation_time_ms INTEGER,
    
    -- Metadata
    mode VARCHAR(10) DEFAULT 'demo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Convert to hypertable for time-series optimization (TimescaleDB)
SELECT create_hypertable('trades', 'entry_time', if_not_exists => TRUE);

-- Create indexes for trades table
CREATE INDEX IF NOT EXISTS idx_trades_account ON trades(account_id);
CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time DESC);
CREATE INDEX IF NOT EXISTS idx_trades_instrument ON trades(instrument);
CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(selected_strategy);
CREATE INDEX IF NOT EXISTS idx_trades_result ON trades(result);
CREATE INDEX IF NOT EXISTS idx_trades_account_entry ON trades(account_id, entry_time DESC);
-- Unique index for trade_id including partitioning column (required for hypertable)
CREATE UNIQUE INDEX IF NOT EXISTS idx_trades_trade_id_unique ON trades(trade_id, entry_time);

-- ============================================================================
-- ACCOUNT PERFORMANCE TABLE (Daily snapshots)
-- ============================================================================
CREATE TABLE IF NOT EXISTS account_performance (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL REFERENCES accounts(account_id),
    date DATE NOT NULL,
    
    -- Daily metrics
    total_trades INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2),
    
    -- Financial metrics
    daily_pnl DECIMAL(10, 2) DEFAULT 0,
    total_profit DECIMAL(10, 2) DEFAULT 0,
    total_loss DECIMAL(10, 2) DEFAULT 0,
    balance_start DECIMAL(10, 2),
    balance_end DECIMAL(10, 2),
    
    -- Strategy metrics
    strategy_profile VARCHAR(50),
    avg_confidence DECIMAL(5, 2),
    avg_execution_time_ms INTEGER,
    
    -- Risk metrics
    max_drawdown DECIMAL(10, 2),
    sharpe_ratio DECIMAL(10, 4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(account_id, date),
    INDEX idx_account_perf_date (date DESC),
    INDEX idx_account_perf_account (account_id)
);

-- ============================================================================
-- STRATEGY PERFORMANCE TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL REFERENCES accounts(account_id),
    strategy_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    
    -- Performance metrics
    total_trades INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2),
    
    -- Financial metrics
    total_profit DECIMAL(10, 2) DEFAULT 0,
    total_loss DECIMAL(10, 2) DEFAULT 0,
    net_pnl DECIMAL(10, 2) DEFAULT 0,
    avg_profit_per_trade DECIMAL(10, 2),
    
    -- Trade metrics
    avg_confidence DECIMAL(5, 2),
    avg_payout_ratio DECIMAL(5, 4),
    avg_execution_time_ms INTEGER,
    
    -- Best/Worst
    best_trade DECIMAL(10, 2),
    worst_trade DECIMAL(10, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(account_id, strategy_name, date),
    INDEX idx_strategy_perf_date (date DESC),
    INDEX idx_strategy_perf_account (account_id),
    INDEX idx_strategy_perf_strategy (strategy_name)
);

-- ============================================================================
-- WEEKLY PERFORMANCE SUMMARY
-- ============================================================================
CREATE TABLE IF NOT EXISTS weekly_performance (
    id SERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    
    -- Portfolio-wide metrics
    total_accounts INTEGER,
    active_accounts INTEGER,
    total_trades INTEGER,
    total_wins INTEGER,
    total_losses INTEGER,
    overall_win_rate DECIMAL(5, 2),
    
    -- Financial metrics
    total_pnl DECIMAL(10, 2),
    total_profit DECIMAL(10, 2),
    total_loss DECIMAL(10, 2),
    best_account VARCHAR(50),
    worst_account VARCHAR(50),
    
    -- Strategy metrics
    best_strategy VARCHAR(100),
    worst_strategy VARCHAR(100),
    
    -- Account breakdown
    account_summary JSONB,
    strategy_summary JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(week_start),
    INDEX idx_weekly_perf_start (week_start DESC)
);

-- ============================================================================
-- SYSTEM EVENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    account_id VARCHAR(50) REFERENCES accounts(account_id),
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    details JSONB,
    
    INDEX idx_events_time (event_time DESC),
    INDEX idx_events_account (account_id),
    INDEX idx_events_type (event_type)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('system_events', 'event_time', if_not_exists => TRUE);

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

-- Current day performance by account
CREATE OR REPLACE VIEW v_daily_account_performance AS
SELECT 
    a.account_id,
    a.email,
    a.strategy_profile,
    a.enabled,
    a.is_healthy,
    COUNT(t.id) as total_trades,
    SUM(CASE WHEN t.result = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN t.result = 'LOSS' THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(CASE WHEN t.result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(SUM(COALESCE(t.profit, 0)), 2) as daily_pnl,
    ROUND(AVG(t.confidence), 2) as avg_confidence,
    ROUND(AVG(t.execution_time_ms), 0) as avg_execution_ms
FROM accounts a
LEFT JOIN trades t ON a.account_id = t.account_id 
    AND DATE(t.entry_time) = CURRENT_DATE
GROUP BY a.account_id, a.email, a.strategy_profile, a.enabled, a.is_healthy;

-- Strategy performance across all accounts
CREATE OR REPLACE VIEW v_strategy_performance_summary AS
SELECT 
    t.selected_strategy,
    COUNT(*) as total_trades,
    SUM(CASE WHEN t.result = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN t.result = 'LOSS' THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(CASE WHEN t.result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(SUM(COALESCE(t.profit, 0)), 2) as total_pnl,
    ROUND(AVG(COALESCE(t.profit, 0)), 2) as avg_profit_per_trade,
    ROUND(AVG(t.payout_ratio * 100), 2) as avg_payout_percent,
    COUNT(DISTINCT t.account_id) as accounts_using
FROM trades t
WHERE t.selected_strategy IS NOT NULL
GROUP BY t.selected_strategy
ORDER BY total_pnl DESC;

-- Recent trades across all accounts
CREATE OR REPLACE VIEW v_recent_trades AS
SELECT 
    t.id,
    t.account_id,
    a.email,
    a.strategy_profile,
    t.instrument,
    t.direction,
    t.amount,
    t.entry_time,
    t.exit_time,
    t.result,
    t.profit,
    t.payout_ratio,
    t.selected_strategy,
    t.confidence
FROM trades t
JOIN accounts a ON t.account_id = a.account_id
ORDER BY t.entry_time DESC
LIMIT 100;

-- ============================================================================
-- FUNCTIONS FOR AUTOMATED CALCULATIONS
-- ============================================================================

-- Function to update account performance daily
CREATE OR REPLACE FUNCTION update_daily_account_performance()
RETURNS void AS $$
BEGIN
    INSERT INTO account_performance (
        account_id, date, total_trades, wins, losses, win_rate,
        daily_pnl, total_profit, total_loss, strategy_profile,
        avg_confidence, avg_execution_time_ms
    )
    SELECT 
        a.account_id,
        CURRENT_DATE,
        COUNT(t.id),
        SUM(CASE WHEN t.result = 'WIN' THEN 1 ELSE 0 END),
        SUM(CASE WHEN t.result = 'LOSS' THEN 1 ELSE 0 END),
        ROUND(AVG(CASE WHEN t.result = 'WIN' THEN 100.0 ELSE 0.0 END), 2),
        ROUND(SUM(COALESCE(t.profit, 0)), 2),
        ROUND(SUM(CASE WHEN t.profit > 0 THEN t.profit ELSE 0 END), 2),
        ROUND(SUM(CASE WHEN t.profit < 0 THEN ABS(t.profit) ELSE 0 END), 2),
        a.strategy_profile,
        ROUND(AVG(t.confidence), 2),
        ROUND(AVG(t.execution_time_ms), 0)
    FROM accounts a
    LEFT JOIN trades t ON a.account_id = t.account_id 
        AND DATE(t.entry_time) = CURRENT_DATE
    GROUP BY a.account_id, a.strategy_profile
    ON CONFLICT (account_id, date) 
    DO UPDATE SET
        total_trades = EXCLUDED.total_trades,
        wins = EXCLUDED.wins,
        losses = EXCLUDED.losses,
        win_rate = EXCLUDED.win_rate,
        daily_pnl = EXCLUDED.daily_pnl,
        total_profit = EXCLUDED.total_profit,
        total_loss = EXCLUDED.total_loss,
        avg_confidence = EXCLUDED.avg_confidence,
        avg_execution_time_ms = EXCLUDED.avg_execution_time_ms;
END;
$$ LANGUAGE plpgsql;

-- Function to update strategy performance daily
CREATE OR REPLACE FUNCTION update_daily_strategy_performance()
RETURNS void AS $$
BEGIN
    INSERT INTO strategy_performance (
        account_id, strategy_name, date, total_trades, wins, losses,
        win_rate, total_profit, total_loss, net_pnl,
        avg_profit_per_trade, avg_confidence, avg_payout_ratio,
        avg_execution_time_ms, best_trade, worst_trade
    )
    SELECT 
        t.account_id,
        t.selected_strategy,
        CURRENT_DATE,
        COUNT(*),
        SUM(CASE WHEN t.result = 'WIN' THEN 1 ELSE 0 END),
        SUM(CASE WHEN t.result = 'LOSS' THEN 1 ELSE 0 END),
        ROUND(AVG(CASE WHEN t.result = 'WIN' THEN 100.0 ELSE 0.0 END), 2),
        ROUND(SUM(CASE WHEN t.profit > 0 THEN t.profit ELSE 0 END), 2),
        ROUND(SUM(CASE WHEN t.profit < 0 THEN ABS(t.profit) ELSE 0 END), 2),
        ROUND(SUM(COALESCE(t.profit, 0)), 2),
        ROUND(AVG(COALESCE(t.profit, 0)), 2),
        ROUND(AVG(t.confidence), 2),
        ROUND(AVG(t.payout_ratio), 4),
        ROUND(AVG(t.execution_time_ms), 0),
        MAX(t.profit),
        MIN(t.profit)
    FROM trades t
    WHERE DATE(t.entry_time) = CURRENT_DATE
        AND t.selected_strategy IS NOT NULL
    GROUP BY t.account_id, t.selected_strategy
    ON CONFLICT (account_id, strategy_name, date)
    DO UPDATE SET
        total_trades = EXCLUDED.total_trades,
        wins = EXCLUDED.wins,
        losses = EXCLUDED.losses,
        win_rate = EXCLUDED.win_rate,
        total_profit = EXCLUDED.total_profit,
        total_loss = EXCLUDED.total_loss,
        net_pnl = EXCLUDED.net_pnl,
        avg_profit_per_trade = EXCLUDED.avg_profit_per_trade,
        avg_confidence = EXCLUDED.avg_confidence,
        avg_payout_ratio = EXCLUDED.avg_payout_ratio,
        avg_execution_time_ms = EXCLUDED.avg_execution_time_ms,
        best_trade = EXCLUDED.best_trade,
        worst_trade = EXCLUDED.worst_trade;
END;
$$ LANGUAGE plpgsql;

-- Function to generate weekly summary
CREATE OR REPLACE FUNCTION generate_weekly_summary(p_week_start DATE)
RETURNS void AS $$
DECLARE
    v_week_end DATE := p_week_start + INTERVAL '6 days';
BEGIN
    INSERT INTO weekly_performance (
        week_start, week_end, total_accounts, active_accounts,
        total_trades, total_wins, total_losses, overall_win_rate,
        total_pnl, total_profit, total_loss,
        account_summary, strategy_summary
    )
    SELECT 
        p_week_start,
        v_week_end,
        COUNT(DISTINCT a.account_id),
        COUNT(DISTINCT CASE WHEN a.enabled THEN a.account_id END),
        COUNT(t.id),
        SUM(CASE WHEN t.result = 'WIN' THEN 1 ELSE 0 END),
        SUM(CASE WHEN t.result = 'LOSS' THEN 1 ELSE 0 END),
        ROUND(AVG(CASE WHEN t.result = 'WIN' THEN 100.0 ELSE 0.0 END), 2),
        ROUND(SUM(COALESCE(t.profit, 0)), 2),
        ROUND(SUM(CASE WHEN t.profit > 0 THEN t.profit ELSE 0 END), 2),
        ROUND(SUM(CASE WHEN t.profit < 0 THEN ABS(t.profit) ELSE 0 END), 2),
        (
            SELECT json_agg(account_data)
            FROM (
                SELECT 
                    a2.account_id,
                    a2.strategy_profile,
                    COUNT(t2.id) as trades,
                    SUM(COALESCE(t2.profit, 0)) as pnl
                FROM accounts a2
                LEFT JOIN trades t2 ON a2.account_id = t2.account_id
                    AND t2.entry_time BETWEEN p_week_start AND v_week_end
                GROUP BY a2.account_id, a2.strategy_profile
            ) account_data
        ),
        (
            SELECT json_agg(strategy_data)
            FROM (
                SELECT 
                    t3.selected_strategy,
                    COUNT(*) as trades,
                    SUM(COALESCE(t3.profit, 0)) as pnl,
                    ROUND(AVG(CASE WHEN t3.result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate
                FROM trades t3
                WHERE t3.entry_time BETWEEN p_week_start AND v_week_end
                    AND t3.selected_strategy IS NOT NULL
                GROUP BY t3.selected_strategy
            ) strategy_data
        )
    FROM accounts a
    LEFT JOIN trades t ON a.account_id = t.account_id
        AND t.entry_time BETWEEN p_week_start AND v_week_end
    ON CONFLICT (week_start) DO UPDATE SET
        total_trades = EXCLUDED.total_trades,
        total_wins = EXCLUDED.total_wins,
        total_losses = EXCLUDED.total_losses,
        overall_win_rate = EXCLUDED.overall_win_rate,
        total_pnl = EXCLUDED.total_pnl,
        total_profit = EXCLUDED.total_profit,
        total_loss = EXCLUDED.total_loss,
        account_summary = EXCLUDED.account_summary,
        strategy_summary = EXCLUDED.strategy_summary;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_trades_account_time ON trades(account_id, entry_time DESC);
CREATE INDEX IF NOT EXISTS idx_trades_strategy_time ON trades(selected_strategy, entry_time DESC);
CREATE INDEX IF NOT EXISTS idx_trades_result_time ON trades(result, entry_time DESC);
CREATE INDEX IF NOT EXISTS idx_account_perf_account_date ON account_performance(account_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_perf_strategy_date ON strategy_performance(strategy_name, date DESC);

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default accounts (will be managed by MultiAccountManager)
INSERT INTO accounts (account_id, email, strategy_profile, max_daily_loss, max_trade_amount)
VALUES
    ('evaluation_account', 'evaluation@kael.local', 'ultimate_evaluator', 10.0, 1.0),
    ('account_1', 'tombonirinakaej@gmail.com', 'conservative', 5.0, 1.5),
    ('account_2', 'tombokael4@gmail.com', 'moderate', 8.0, 2.0),
    ('account_3', 'ruslantombofitiavana@gmail.com', 'aggressive', 15.0, 3.0),
    ('account_4', 'tombofifalianakimi@gmail.com', 'scalping', 10.0, 2.5),
    ('account_5', 'dinokamisy@gmail.com', 'trend_following', 10.0, 2.5)
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- GRANTS (adjust as needed for your setup)
-- ============================================================================

-- Grant permissions to application user
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kael_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kael_app;
