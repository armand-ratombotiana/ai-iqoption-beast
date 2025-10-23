-- =====================================================
-- IQOption AI Trading System - PostgreSQL Schema
-- =====================================================
-- Created: 2025-01-15
-- Description: Database schema for automated trading system
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: trades
-- Description: Main table for storing all trade records
-- =====================================================
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    asset VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('CALL', 'PUT', 'call', 'put', 'SKIP', 'skip', 'UNKNOWN')),
    ai_confidence NUMERIC(5, 2) DEFAULT 0 CHECK (ai_confidence >= 0 AND ai_confidence <= 100),
    trade_result VARCHAR(20) DEFAULT 'PENDING' CHECK (trade_result IN ('WIN', 'LOSS', 'PENDING', 'ERROR', 'CANCELLED')),
    payout NUMERIC(15, 2) DEFAULT 0,
    amount NUMERIC(15, 2) DEFAULT 0,
    duration INTEGER DEFAULT 0, -- in minutes
    model_votes JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_asset ON trades(asset);
CREATE INDEX IF NOT EXISTS idx_trades_result ON trades(trade_result);
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(DATE(timestamp));

-- =====================================================
-- TABLE: daily_stats
-- Description: Aggregated daily trading statistics
-- =====================================================
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    pending INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    total_profit NUMERIC(15, 2) DEFAULT 0,
    win_rate NUMERIC(5, 2) GENERATED ALWAYS AS (
        CASE
            WHEN total_trades > 0 THEN (wins::NUMERIC / total_trades * 100)
            ELSE 0
        END
    ) STORED,
    avg_confidence NUMERIC(5, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date DESC);

-- =====================================================
-- TABLE: workflow_executions
-- Description: Track workflow execution status
-- =====================================================
CREATE TABLE IF NOT EXISTS workflow_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'skipped')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_started ON workflow_executions(started_at DESC);

-- =====================================================
-- TABLE: error_logs
-- Description: Store error information for debugging
-- =====================================================
CREATE TABLE IF NOT EXISTS error_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    workflow_name VARCHAR(255),
    workflow_id VARCHAR(255),
    execution_id VARCHAR(255),
    error_node VARCHAR(255),
    error_message TEXT,
    error_description TEXT,
    stack_trace TEXT,
    input_data JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_workflow ON error_logs(workflow_name);
CREATE INDEX IF NOT EXISTS idx_error_logs_resolved ON error_logs(resolved);

-- =====================================================
-- TABLE: ai_model_performance
-- Description: Track individual AI model performance
-- =====================================================
CREATE TABLE IF NOT EXISTS ai_model_performance (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy NUMERIC(5, 2) GENERATED ALWAYS AS (
        CASE
            WHEN total_predictions > 0 THEN (correct_predictions::NUMERIC / total_predictions * 100)
            ELSE 0
        END
    ) STORED,
    avg_confidence NUMERIC(5, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, model_name)
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_ai_performance_date_model ON ai_model_performance(date DESC, model_name);

-- =====================================================
-- TABLE: system_config
-- Description: Store dynamic system configuration
-- =====================================================
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default configurations
INSERT INTO system_config (config_key, config_value, description) VALUES
    ('trading_enabled', 'true', 'Master switch for trading system'),
    ('max_daily_trades', '100', 'Maximum number of trades per day'),
    ('max_daily_loss', '1000', 'Maximum acceptable loss per day (in dollars)'),
    ('min_consensus_confidence', '70', 'Minimum confidence threshold for trades'),
    ('maintenance_mode', 'false', 'Set to true to pause all trading')
ON CONFLICT (config_key) DO NOTHING;

-- =====================================================
-- VIEWS: Useful analytical views
-- =====================================================

-- View: Recent trades with human-readable formatting
CREATE OR REPLACE VIEW v_recent_trades AS
SELECT
    trade_id,
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') as trade_time,
    asset,
    direction,
    ROUND(ai_confidence, 1) as confidence,
    trade_result,
    ROUND(payout, 2) as payout,
    ROUND(amount, 2) as amount,
    duration,
    CASE
        WHEN error_message IS NOT NULL THEN 'Yes'
        ELSE 'No'
    END as has_error
FROM trades
ORDER BY timestamp DESC
LIMIT 100;

-- View: Daily performance summary
CREATE OR REPLACE VIEW v_daily_performance AS
SELECT
    date,
    total_trades,
    wins,
    losses,
    ROUND(win_rate, 1) as win_rate_pct,
    ROUND(total_profit, 2) as profit,
    CASE
        WHEN total_profit >= 0 THEN 'Profit'
        ELSE 'Loss'
    END as day_result
FROM daily_stats
ORDER BY date DESC;

-- View: AI model comparison
CREATE OR REPLACE VIEW v_ai_model_comparison AS
SELECT
    model_name,
    SUM(total_predictions) as total_predictions,
    SUM(correct_predictions) as correct_predictions,
    ROUND(AVG(accuracy), 1) as avg_accuracy,
    ROUND(AVG(avg_confidence), 1) as avg_confidence
FROM ai_model_performance
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY model_name
ORDER BY avg_accuracy DESC;

-- =====================================================
-- FUNCTIONS: Automated maintenance and calculations
-- =====================================================

-- Function: Update timestamp on record modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS update_trades_updated_at ON trades;
CREATE TRIGGER update_trades_updated_at
    BEFORE UPDATE ON trades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_daily_stats_updated_at ON daily_stats;
CREATE TRIGGER update_daily_stats_updated_at
    BEFORE UPDATE ON daily_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Clean old workflow executions (keep last 1000)
CREATE OR REPLACE FUNCTION cleanup_old_executions()
RETURNS void AS $$
BEGIN
    DELETE FROM workflow_executions
    WHERE id NOT IN (
        SELECT id FROM workflow_executions
        ORDER BY started_at DESC
        LIMIT 1000
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Archive old trades (move trades older than 90 days to archive table)
CREATE TABLE IF NOT EXISTS trades_archive (LIKE trades INCLUDING ALL);

CREATE OR REPLACE FUNCTION archive_old_trades()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    WITH archived AS (
        INSERT INTO trades_archive
        SELECT * FROM trades
        WHERE timestamp < NOW() - INTERVAL '90 days'
        RETURNING id
    )
    SELECT COUNT(*) INTO archived_count FROM archived;

    DELETE FROM trades
    WHERE timestamp < NOW() - INTERVAL '90 days';

    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MAINTENANCE QUERIES
-- =====================================================

-- Query to check system health
COMMENT ON TABLE trades IS 'Run: SELECT COUNT(*) as total_trades, MAX(timestamp) as last_trade FROM trades;';

-- Query to check today's performance
COMMENT ON VIEW v_daily_performance IS 'Run: SELECT * FROM v_daily_performance WHERE date = CURRENT_DATE;';

-- Query to find problematic trades
COMMENT ON TABLE error_logs IS 'Run: SELECT * FROM error_logs WHERE resolved = false ORDER BY timestamp DESC;';

-- =====================================================
-- GRANTS (adjust based on your user setup)
-- =====================================================
-- Example: GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO n8n_user;
-- Example: GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO n8n_user;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Database schema created successfully!';
    RAISE NOTICE '📊 Tables created: trades, daily_stats, workflow_executions, error_logs, ai_model_performance, system_config';
    RAISE NOTICE '👁️  Views created: v_recent_trades, v_daily_performance, v_ai_model_comparison';
    RAISE NOTICE '⚙️  Functions created: update_updated_at_column, cleanup_old_executions, archive_old_trades';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Verify tables: \dt';
    RAISE NOTICE '2. Check views: \dv';
    RAISE NOTICE '3. Test connection in n8n PostgreSQL node';
END $$;
