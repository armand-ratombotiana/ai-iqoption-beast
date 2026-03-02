# Monitoring System - Quick Start Guide

Get the paper trading monitoring system up and running in minutes.

## One-Minute Setup

### Windows
```bash
setup_monitoring.bat
```

### Unix/Linux/Mac
```bash
bash setup_monitoring.sh
```

This creates directories, initializes files, and verifies installation.

---

## Basic Usage

### 1. Start Real-time Monitor
```bash
python monitor_paper_trading.py
```
- Updates every 5 seconds
- Shows live trading metrics
- Press Ctrl+C to stop

### 2. Check System Health
```bash
python health_check.py
```
- Verifies all components
- Shows any issues
- Exit code 0 = healthy

### 3. View Performance Report
```bash
python performance_dashboard.py --all
```
- Detailed analytics
- Pair performance
- Indicator accuracy

### 4. Check for Alerts
```bash
python alert_system.py --alerts
```
- Shows active alerts
- Critical issues highlighted

---

## Common Commands

```bash
# Real-time monitoring dashboard
python monitor_paper_trading.py --interval 5

# Health check every minute (Unix)
watch -n 60 python health_check.py

# Performance analysis
python performance_dashboard.py --pairs
python performance_dashboard.py --indicators

# Export trade data
python metrics_collector.py --export-csv trades.csv

# Verify logging
python logging_config.py --verify --show-files

# Run all checks
python health_check.py
python alert_system.py --check
```

---

## Directory Structure

After setup, you'll have:

```
data/              ← Trade history & metrics
logs/              ← Log files
scripts/           ← Startup scripts
```

**Key Files:**
- `data/trades.json` - All trades
- `data/trading.db` - Database
- `logs/trading.log` - Trade logs
- `logs/errors.log` - Error logs

---

## Integration with Trading Engine

Add these lines to your trading engine:

```python
from metrics_collector import MetricsCollector

collector = MetricsCollector()

# When starting a trade
collector.record_trade(trade_data)

# When trade completes
collector.update_trade_result(timestamp, result_data)

# Periodically save status
collector.save_status({
    'is_running': True,
    'connected': True,
    'active_trades': count,
    'last_trade_time': timestamp
})
```

---

## Monitoring While Trading

### Terminal 1: Real-time Monitor
```bash
python monitor_paper_trading.py
```

### Terminal 2: Health Checks
```bash
while true; do
    python health_check.py
    sleep 300  # Every 5 minutes
done
```

### Terminal 3: Performance (periodically)
```bash
python performance_dashboard.py --all > report.txt
```

---

## Alert Thresholds

Default thresholds (edit `alert_system.py` to change):

```python
'consecutive_loss_threshold': 3         # Alert after 3 losses
'daily_loss_limit': 20.0                # Alert at $20 loss
'low_confidence_threshold': 50          # Alert below 50% confidence
'high_drawdown_threshold': 50.0         # Alert above $50 drawdown
```

---

## Troubleshooting

### Monitor shows "No trades"
- Ensure trading engine is running
- Check `data/trades.json` has content
- Verify `data/status.json` has recent timestamp

### Health check fails
```bash
python health_check.py --json  # Get detailed info
```

### Database errors
```bash
# Recreate database (trades.json backup safe)
rm data/trading.db
python metrics_collector.py --show-stats
```

### Missing logs
```bash
python logging_config.py --verify
```

---

## Sample Output

### Real-time Monitor
```
TRADING METRICS
  Total Trades:              20
  Win Rate:                 55.00%
  Total Profit/Loss:       $5.50

ENGINE STATUS
  Status:                RUNNING
  Connection:          CONNECTED
  Active Trades:               2
```

### Health Check
```
[PASS] Directory structure
[PASS] Required files
[PASS] Engine status
[PASS] Trade activity
[PASS] Log files
[PASS] Database
[PASS] Alert system

Overall Status: 8/8 checks passed
✓ System is healthy and ready!
```

### Performance Report
```
PAIR PERFORMANCE:
  EURUSD-OTC: 58.33% win rate, $4.20 profit
  GBPUSD-OTC: 50.00% win rate, $1.30 profit

INDICATOR ACCURACY:
  MACD: 62.5% accuracy
  RSI: 55.0% accuracy
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `monitor_paper_trading.py` | Real-time dashboard |
| `performance_dashboard.py` | Analytics & reports |
| `alert_system.py` | Alert management |
| `health_check.py` | System verification |
| `logging_config.py` | Logging setup |
| `metrics_collector.py` | Trade tracking |

---

## For More Details

See full documentation:
- **MONITORING_SYSTEM_GUIDE.md** - Complete guide
- **MONITORING_SYSTEM_VERIFICATION.md** - Implementation details

---

## Quick Tips

1. **Run health check first** to verify setup
2. **Keep monitor running** while trading
3. **Check alerts regularly** for issues
4. **Export data weekly** for backup
5. **Review performance report** to improve

---

## Contact & Support

For issues:
1. Check `logs/errors.log` for error messages
2. Run `python health_check.py` for diagnostics
3. Review configuration in each script
4. Export data for analysis

---

**Ready to start monitoring?**

```bash
python health_check.py      # Verify setup
python monitor_paper_trading.py  # Start monitoring
```

Happy trading! 📈
