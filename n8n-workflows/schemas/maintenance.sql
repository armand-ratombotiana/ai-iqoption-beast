-- =====================================================
-- Database Maintenance Queries
-- =====================================================
-- Useful queries for monitoring and maintaining the system
-- =====================================================

-- =====================================================
-- MONITORING QUERIES
-- =====================================================

-- System Health Check
-- Shows overall system status
SELECT
    'System Health' as metric,
    (SELECT COUNT(*) FROM trades WHERE DATE(timestamp) = CURRENT_DATE) as today_trades,
    (SELECT COUNT(*) FROM workflow_executions WHERE status = 'running') as running_executions,
    (SELECT COUNT(*) FROM error_logs WHERE resolved = false) as unresolved_errors,
    (SELECT config_value FROM system_config WHERE config_key = 'maintenance_mode') as maintenance_mode;

-- Today's Performance
SELECT * FROM v_daily_performance WHERE date = CURRENT_DATE;

-- Last 10 Trades
SELECT * FROM v_recent_trades LIMIT 10;

-- Active Executions (should be 0 or 1)
SELECT
    execution_id,
    status,
    started_at,
    EXTRACT(EPOCH FROM (NOW() - started_at)) / 60 as minutes_running
FROM workflow_executions
WHERE status = 'running'
ORDER BY started_at DESC;

-- Recent Errors
SELECT
    timestamp,
    workflow_name,
    error_node,
    error_message,
    resolved
FROM error_logs
WHERE resolved = false
ORDER BY timestamp DESC
LIMIT 10;

-- AI Model Performance (Last 30 days)
SELECT * FROM v_ai_model_comparison;

-- Win Rate by Asset
SELECT
    asset,
    COUNT(*) as total_trades,
    SUM(CASE WHEN trade_result = 'WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(
        SUM(CASE WHEN trade_result = 'WIN' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100,
        1
    ) as win_rate_pct,
    ROUND(SUM(payout), 2) as total_profit
FROM trades
WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL '30 days'
  AND trade_result IN ('WIN', 'LOSS')
GROUP BY asset
ORDER BY total_trades DESC;

-- Hourly Trading Activity
SELECT
    EXTRACT(HOUR FROM timestamp) as hour_of_day,
    COUNT(*) as trades,
    SUM(CASE WHEN trade_result = 'WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(ai_confidence), 1) as avg_confidence
FROM trades
WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY EXTRACT(HOUR FROM timestamp)
ORDER BY hour_of_day;

-- =====================================================
-- ANALYTICS QUERIES
-- =====================================================

-- Weekly Performance Trend
SELECT
    DATE_TRUNC('week', date) as week_start,
    SUM(total_trades) as total_trades,
    ROUND(AVG(win_rate), 1) as avg_win_rate,
    ROUND(SUM(total_profit), 2) as total_profit
FROM daily_stats
WHERE date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE_TRUNC('week', date)
ORDER BY week_start DESC;

-- Confidence vs Win Rate Analysis
SELECT
    CASE
        WHEN ai_confidence >= 90 THEN '90-100%'
        WHEN ai_confidence >= 80 THEN '80-89%'
        WHEN ai_confidence >= 70 THEN '70-79%'
        ELSE '<70%'
    END as confidence_range,
    COUNT(*) as trades,
    SUM(CASE WHEN trade_result = 'WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(
        SUM(CASE WHEN trade_result = 'WIN' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100,
        1
    ) as win_rate_pct
FROM trades
WHERE trade_result IN ('WIN', 'LOSS')
  AND DATE(timestamp) >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY
    CASE
        WHEN ai_confidence >= 90 THEN '90-100%'
        WHEN ai_confidence >= 80 THEN '80-89%'
        WHEN ai_confidence >= 70 THEN '70-79%'
        ELSE '<70%'
    END
ORDER BY confidence_range DESC;

-- Best Performing Days
SELECT
    date,
    total_trades,
    wins,
    ROUND(win_rate, 1) as win_rate_pct,
    ROUND(total_profit, 2) as profit
FROM daily_stats
WHERE total_trades > 0
ORDER BY total_profit DESC
LIMIT 10;

-- Worst Performing Days
SELECT
    date,
    total_trades,
    wins,
    ROUND(win_rate, 1) as win_rate_pct,
    ROUND(total_profit, 2) as profit
FROM daily_stats
WHERE total_trades > 0
ORDER BY total_profit ASC
LIMIT 10;

-- =====================================================
-- MAINTENANCE OPERATIONS
-- =====================================================

-- Clean Up Old Executions (keeps last 1000)
SELECT cleanup_old_executions();

-- Archive Old Trades (moves trades >90 days old to archive)
SELECT archive_old_trades() as archived_count;

-- Mark Old Errors as Resolved (auto-resolve errors >30 days old)
UPDATE error_logs
SET resolved = true, resolved_at = NOW()
WHERE resolved = false
  AND timestamp < NOW() - INTERVAL '30 days';

-- Vacuum and Analyze (optimize database)
VACUUM ANALYZE trades;
VACUUM ANALYZE daily_stats;
VACUUM ANALYZE error_logs;

-- Reindex Tables (fixes fragmentation)
REINDEX TABLE trades;
REINDEX TABLE daily_stats;

-- =====================================================
-- TROUBLESHOOTING QUERIES
-- =====================================================

-- Find Stuck Executions (running >10 minutes)
SELECT
    execution_id,
    status,
    started_at,
    EXTRACT(EPOCH FROM (NOW() - started_at)) / 60 as minutes_running
FROM workflow_executions
WHERE status = 'running'
  AND started_at < NOW() - INTERVAL '10 minutes';

-- Force Complete Stuck Executions
-- CAREFUL: Only run if you're sure execution is stuck
/*
UPDATE workflow_executions
SET status = 'failed', completed_at = NOW(), notes = 'Manually marked as failed - stuck execution'
WHERE status = 'running'
  AND started_at < NOW() - INTERVAL '10 minutes';
*/

-- Find Trades Without Results (pending >1 hour)
SELECT
    trade_id,
    timestamp,
    asset,
    direction,
    ai_confidence,
    EXTRACT(EPOCH FROM (NOW() - timestamp)) / 60 as minutes_pending
FROM trades
WHERE trade_result = 'PENDING'
  AND timestamp < NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;

-- Find Duplicate Trades (same timestamp + asset)
SELECT
    timestamp,
    asset,
    direction,
    COUNT(*) as duplicate_count
FROM trades
GROUP BY timestamp, asset, direction
HAVING COUNT(*) > 1;

-- Database Size
SELECT
    pg_size_pretty(pg_database_size(current_database())) as database_size,
    pg_size_pretty(pg_total_relation_size('trades')) as trades_table_size,
    pg_size_pretty(pg_total_relation_size('error_logs')) as error_logs_table_size;

-- Table Row Counts
SELECT
    'trades' as table_name,
    COUNT(*) as row_count
FROM trades
UNION ALL
SELECT 'daily_stats', COUNT(*) FROM daily_stats
UNION ALL
SELECT 'workflow_executions', COUNT(*) FROM workflow_executions
UNION ALL
SELECT 'error_logs', COUNT(*) FROM error_logs
UNION ALL
SELECT 'ai_model_performance', COUNT(*) FROM ai_model_performance;

-- =====================================================
-- CONFIGURATION QUERIES
-- =====================================================

-- View Current Configuration
SELECT * FROM system_config ORDER BY config_key;

-- Enable Maintenance Mode
UPDATE system_config
SET config_value = 'true', updated_at = NOW()
WHERE config_key = 'maintenance_mode';

-- Disable Maintenance Mode
UPDATE system_config
SET config_value = 'false', updated_at = NOW()
WHERE config_key = 'maintenance_mode';

-- Update Max Daily Trades
UPDATE system_config
SET config_value = '150', updated_at = NOW()
WHERE config_key = 'max_daily_trades';

-- Update Max Daily Loss
UPDATE system_config
SET config_value = '500', updated_at = NOW()
WHERE config_key = 'max_daily_loss';

-- =====================================================
-- EXPORT QUERIES (for reports)
-- =====================================================

-- Export Last 30 Days for Excel/CSV
SELECT
    trade_id,
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') as trade_time,
    asset,
    direction,
    ROUND(ai_confidence, 1) as confidence,
    trade_result,
    ROUND(amount, 2) as amount,
    ROUND(payout, 2) as payout,
    duration
FROM trades
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY timestamp DESC;

-- Daily Summary for Report
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
    END as result
FROM daily_stats
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;

-- =====================================================
-- BACKUP RECOMMENDATIONS
-- =====================================================

-- To backup database:
-- pg_dump -U trading_user -d iqoption_trading -F c -f backup_$(date +%Y%m%d).dump

-- To restore from backup:
-- pg_restore -U trading_user -d iqoption_trading -c backup_20250115.dump

-- To export specific table as CSV:
-- psql -U trading_user -d iqoption_trading -c "COPY (SELECT * FROM trades WHERE date >= CURRENT_DATE - INTERVAL '30 days') TO STDOUT WITH CSV HEADER" > trades_export.csv

-- =====================================================
-- NOTES
-- =====================================================
--
-- Run these queries as needed for monitoring and maintenance.
-- Schedule regular backups (daily recommended).
-- Review error logs weekly.
-- Archive old trades monthly.
-- Monitor disk space - database can grow significantly over time.
--
-- For automated maintenance, consider setting up cron jobs:
-- 0 2 * * * psql -U trading_user -d iqoption_trading -f /path/to/maintenance.sql >> /var/log/db_maintenance.log 2>&1
--
-- =====================================================
