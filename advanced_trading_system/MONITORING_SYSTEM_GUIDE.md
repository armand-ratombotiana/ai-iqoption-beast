# Paper Trading Monitoring System Guide

Comprehensive monitoring system for real-time paper trading oversight, performance analysis, and alert management.

## Overview

The monitoring system provides:
- **Real-time Monitor**: Live trading dashboard with 5-second updates
- **Performance Dashboard**: Detailed analytics and pair/indicator performance
- **Alert System**: Proactive alerts for critical trading events
- **Logging Configuration**: Structured logging with rotation
- **Metrics Collection**: Trade history and metrics persistence
- **Health Check**: System status verification

## Directory Structure

```
data/
├── trades.json           # All trade records (JSON)
├── trades.csv            # Trade history (CSV export)
├── trading.db            # SQLite database
├── metrics.json          # Current metrics snapshot
├── status.json           # Engine status
├── alerts.json           # Recent alerts
└── emergency_stop.txt    # Emergency stop flag (if triggered)

logs/
├── trading.log           # Trading activity logs
├── analysis.log          # Indicator analysis logs
├── errors.log            # Error logs
├── alerts.log            # Alert notifications
└── metrics.log           # Metrics snapshots
```

## Components

### 1. Real-time Monitor (`monitor_paper_trading.py`)

Displays live trading status with color-formatted output.

**Features:**
- Current trading metrics (win rate, profit/loss)
- Engine status and connection status
- Active trades (last 5)
- Recent completed trades (last 5)
- Updates every 5 seconds
- Terminal colors for easy visibility

**Usage:**
```bash
python monitor_paper_trading.py
python monitor_paper_trading.py --interval 10      # 10-second updates
python monitor_paper_trading.py --data-dir data    # Custom data directory
```

**Output includes:**
```
TRADING METRICS
  Total Trades:              20
  Win Rate:                 55.00%
  Wins:                      11
  Losses:                     8
  Total Profit/Loss:       $5.50

ENGINE STATUS
  Status:                RUNNING
  Connection:          CONNECTED
  Active Trades:               2
  Last Trade:        12:30:45

ACTIVE TRADES (Last 5)
  2024-01-15 12:30:45 | EURUSD-OTC | CALL | Confidence: 85%
```

### 2. Performance Dashboard (`performance_dashboard.py`)

Detailed analytics on trading performance, indicators, and pairs.

**Features:**
- Pair performance statistics
- Indicator accuracy tracking
- Best/worst performing pairs
- Drawdown analysis
- Hourly statistics
- Confidence level distribution
- CSV export

**Usage:**
```bash
python performance_dashboard.py                    # Full report
python performance_dashboard.py --pairs            # Pair analysis only
python performance_dashboard.py --indicators       # Indicator accuracy
python performance_dashboard.py --drawdown         # Drawdown analysis
python performance_dashboard.py --hourly           # Hourly breakdown
python performance_dashboard.py --all              # All analytics
python performance_dashboard.py --export output.csv  # Export to CSV
```

**Report includes:**
```
PAIR PERFORMANCE:
  EURUSD-OTC:
    Trades: 12
    Win Rate: 58.33%
    Total Profit: $4.20
    Avg Profit/Trade: $0.35

INDICATOR ACCURACY:
  MACD: 62.5% accuracy
  RSI: 55.0% accuracy
  STOCHASTIC: 60.0% accuracy

DRAWDOWN ANALYSIS:
  Max Drawdown: $8.50
  Avg Drawdown: $3.25
  Drawdown Periods: 5
```

### 3. Alert System (`alert_system.py`)

Proactive monitoring with configurable thresholds.

**Alert Types:**
- **CONSECUTIVE_LOSSES**: 3+ consecutive losses (CRITICAL)
- **DAILY_LOSS_LIMIT**: Daily loss threshold reached (WARNING/CRITICAL)
- **CONNECTION_ISSUE**: Lost connection to server (CRITICAL)
- **LOW_SIGNAL_QUALITY**: Confidence < 50% (WARNING)
- **HIGH_DRAWDOWN**: Drawdown exceeds threshold (WARNING)
- **TRADING_PAUSED**: Engine paused conditions (WARNING)
- **RECOVERY_SUCCESS**: System recovered (INFO)
- **ENGINE_ERROR**: System errors (CRITICAL)

**Features:**
- Real-time threshold monitoring
- Custom alert handlers
- Alert acknowledgment
- Alert history persistence
- Severity levels (INFO, WARNING, CRITICAL)

**Configuration:**
```python
# In alert_system.py
self.config = {
    'consecutive_loss_threshold': 3,      # Losses before alert
    'daily_loss_limit': 20.0,             # Daily loss in dollars
    'low_confidence_threshold': 50,       # % confidence minimum
    'high_drawdown_threshold': 50.0,      # Max drawdown in dollars
    'check_interval': 30,                 # Check frequency in seconds
}
```

**Usage:**
```bash
python alert_system.py --check              # Run health checks
python alert_system.py --alerts             # Show current alerts
python alert_system.py --data-dir data      # Custom data directory
```

**Alert Log Example:**
```
2024-01-15 12:35:20 - WARNING - [consecutive_losses] ALERT: 3 consecutive losses detected!
2024-01-15 12:40:15 - CRITICAL - [daily_loss_limit] ALERT: Daily loss limit 80% reached
```

### 4. Logging Configuration (`logging_config.py`)

Structured logging with rotating file handlers.

**Log Files:**
- **trading.log**: Trading activity (INFO level)
- **analysis.log**: Indicator analysis (DEBUG level)
- **errors.log**: Errors and exceptions (ERROR level)
- **alerts.log**: Alert notifications (WARNING level)
- **metrics.log**: Metrics snapshots (INFO level)

**Features:**
- Rotating file handlers (10MB files, 10 backups)
- Separate log levels per component
- Timestamps and structured format
- Automatic log cleanup

**Usage:**
```bash
python logging_config.py --verify              # Verify logging setup
python logging_config.py --show-files          # Show log file info
python logging_config.py --cleanup 7           # Remove logs > 7 days old
```

**Log Entry Examples:**
```
2024-01-15 12:30:45 - TradingEngine - INFO - TRADE | Pair: EURUSD-OTC | Signal: CALL | Confidence: 85.0% | Amount: $2.00
2024-01-15 12:31:00 - TradingEngine - INFO - RESULT | Pair: EURUSD-OTC | Result: WIN | Profit: $1.75
2024-01-15 12:35:20 - AlertLogger - WARNING - ALERT [consecutive_losses]: 3 consecutive losses detected!
```

### 5. Metrics Collection (`metrics_collector.py`)

Trade and metrics persistence with multiple formats.

**Features:**
- Trade recording and history
- Result updates (win/loss/tie)
- JSON export
- CSV export for analysis
- SQLite database storage
- Batch metrics snapshots

**Database Schema:**

Trades Table:
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    timestamp TEXT UNIQUE NOT NULL,
    pair TEXT NOT NULL,
    signal TEXT NOT NULL,            -- CALL or PUT
    confidence REAL NOT NULL,        -- 0-100
    amount REAL NOT NULL,            -- Trade amount in dollars
    duration INTEGER NOT NULL,       -- Trade duration in minutes
    entry_price REAL NOT NULL,
    payout REAL NOT NULL,            -- Expected payout percentage
    rsi REAL NOT NULL,
    macd_histogram REAL NOT NULL,
    stoch_k REAL NOT NULL,
    adx REAL NOT NULL,
    bb_position REAL NOT NULL,       -- 0-1 (Bollinger Bands)
    order_id INTEGER,
    exit_price REAL,
    profit REAL,
    result TEXT,                     -- WIN, LOSS, or TIE
    created_at TIMESTAMP
);
```

Metrics Table:
```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
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
    created_at TIMESTAMP
);
```

**Usage:**
```bash
python metrics_collector.py --show-stats       # Database statistics
python metrics_collector.py --export-csv file.csv  # Export trades
python metrics_collector.py --data-size        # Show file sizes
```

### 6. Health Check (`health_check.py`)

System status verification and diagnostics.

**Checks:**
1. Directory structure
2. Required files
3. Engine status
4. Trade activity
5. Log file accessibility
6. Database integrity
7. Alert system status
8. Emergency stop capability

**Features:**
- Color-coded results
- Comprehensive diagnostics
- JSON output option
- Exit codes (0=healthy, 1=issues)

**Usage:**
```bash
python health_check.py                         # Full health check
python health_check.py --json                  # JSON output
python health_check.py --data-dir data         # Custom data directory
```

**Health Check Output:**
```
[PASS] Directory Checks
[PASS] Required Files
[PASS] Engine Status
[PASS] Trade Activity
[PASS] Log Files
[PASS] Database
[PASS] Alert System
[PASS] Emergency Stop

Overall Status: 8/8 checks passed (100%)
✓ System is healthy and ready!
```

## Integration with Paper Trading Engine

The monitoring system integrates with the paper trading engine through shared JSON files:

### Data Files Used:
1. **data/trades.json** - Written by engine, read by monitoring
2. **data/metrics.json** - Written by monitoring, read by engine
3. **data/status.json** - Written by engine, read by monitoring
4. **data/alerts.json** - Written by alert system, read by monitoring

### Integration Points:

**Paper Trading Engine writes:**
```python
# After executing a trade
collector.record_trade(trade_data)

# After trade completes
collector.update_trade_result(timestamp, result)

# Periodically save status
collector.save_status({
    'is_running': True,
    'connected': True,
    'active_trades': count,
    'last_trade_time': timestamp
})
```

**Monitoring reads:**
```python
# Monitor reads trades and calculates metrics
trades = collector.load_trades()
metrics = monitor.calculate_metrics()

# Alert system checks status
status = load_status()
alert_system.run_checks()
```

## Quick Start

### 1. Initialize Directories
```bash
python health_check.py --verify
```

### 2. Start Real-time Monitoring
```bash
# Terminal 1 - Real-time dashboard
python monitor_paper_trading.py

# Terminal 2 - Health checks (periodic)
while true; do
    python health_check.py
    sleep 300  # Every 5 minutes
done
```

### 3. View Performance Analytics
```bash
python performance_dashboard.py --all
python performance_dashboard.py --export performance_report.csv
```

### 4. Check Alerts
```bash
python alert_system.py --alerts
python alert_system.py --check
```

### 5. Manage Logs
```bash
python logging_config.py --show-files
python logging_config.py --cleanup 7  # Keep only 7 days
```

## Configuration Examples

### Alert Thresholds
Edit `alert_system.py`:
```python
self.config = {
    'consecutive_loss_threshold': 5,        # More tolerant
    'daily_loss_limit': 50.0,               # Higher limit
    'low_confidence_threshold': 40,         # More trades
    'high_drawdown_threshold': 100.0,       # Higher threshold
}
```

### Log Rotation
Edit `logging_config.py`:
```python
# Larger log files
handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=50 * 1024 * 1024,  # 50MB
    backupCount=20                # Keep 20 files
)
```

### Monitor Update Interval
```bash
python monitor_paper_trading.py --interval 2   # 2-second updates
python monitor_paper_trading.py --interval 30  # 30-second updates
```

## Common Operations

### Export All Trade Data
```bash
python metrics_collector.py --export-csv trades_export.csv
```

### Check System Health Before Trading
```bash
python health_check.py
```

### Monitor During Live Trading
```bash
# Terminal 1: Real-time monitor
python monitor_paper_trading.py --interval 5

# Terminal 2: Periodic health checks
watch -n 60 'python health_check.py | tail -15'

# Terminal 3: Check alerts
watch -n 30 'python alert_system.py --alerts'
```

### Generate Performance Report
```bash
python performance_dashboard.py --all > performance_report.txt
python performance_dashboard.py --export trades_analysis.csv
```

## Files Created

### Scripts Created:
1. `monitor_paper_trading.py` - Real-time monitor
2. `performance_dashboard.py` - Analytics dashboard
3. `alert_system.py` - Alert management
4. `logging_config.py` - Logging configuration
5. `metrics_collector.py` - Metrics and trade tracking
6. `health_check.py` - System health verification
7. `test_monitoring_system.py` - Test suite

### Directory Structure:
```
data/
  trades.json
  trades.csv
  trading.db
  metrics.json
  status.json
  alerts.json

logs/
  trading.log
  analysis.log
  errors.log
  alerts.log
  metrics.log
```

## Troubleshooting

### Monitor shows no data
- Ensure paper trading engine is running
- Check `data/trades.json` exists and has content
- Verify `data/status.json` has recent timestamp

### Alerts not triggering
- Check `alert_system.py` thresholds match your expectations
- Run `python alert_system.py --check` manually
- Verify `data/trades.json` has recent trades

### Log files not created
- Run `python logging_config.py --verify`
- Ensure `logs/` directory has write permissions
- Check disk space availability

### Database errors
- Run `python health_check.py` to check integrity
- Delete `data/trading.db` to recreate (trades.json backup safe)
- Verify disk space for database growth

## Performance Notes

- **Monitor**: Updates every 5 seconds, minimal CPU usage
- **Database**: Optimized for ~1000+ trades before noticeable slowdown
- **Logs**: Rotate automatically, default 100MB total
- **Memory**: All components run on modest systems (<100MB)

## Security Considerations

- `data/` directory may contain sensitive trade information
- Keep `data/` and `logs/` excluded from version control
- Don't commit `.env` or credentials
- Use `.gitignore` to protect sensitive files

## Next Steps

After monitoring system is set up:
1. Run health checks to verify installation
2. Start real-time monitor before trading
3. Set up alert handlers for notifications (email, SMS)
4. Configure log retention policies
5. Schedule regular performance reports

## Support

For issues or questions:
1. Check `logs/errors.log` for error messages
2. Run `health_check.py` to verify system status
3. Review this guide's Troubleshooting section
4. Export performance data for analysis
