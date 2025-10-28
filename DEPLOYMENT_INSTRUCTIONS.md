# 🚀 Multi-Account Trading System - Deployment Instructions

## Overview

This document provides step-by-step instructions to deploy and run the multi-account parallel trading system for **performance evaluation of 5 different trading strategies**.

---

## ✅ What Has Been Implemented

The complete multi-account trading system with:

1. **Multi-Account Parallel Bot** (`multi_account_parallel_bot.py`)
   - 5 concurrent IQ Option accounts
   - Each account runs a different strategy profile
   - Independent thread per account
   - Comprehensive performance tracking

2. **Strategy Profiles**
   - Conservative: High confidence, low risk (Account 1)
   - Moderate: Balanced approach (Account 2)
   - Aggressive: More opportunities, higher risk (Account 3)
   - Scalping: High frequency trading (Account 4)
   - Trend Following: Momentum-based (Account 5)

3. **Performance Tracking**
   - Per-account metrics (trades, win rate, P&L, balance)
   - Per-strategy metrics (aggregated across accounts)
   - Portfolio-wide metrics
   - Real-time Prometheus metrics
   - TimescaleDB database logging

4. **Monitoring & Analytics**
   - RESTful API (port 5001)
   - Prometheus metrics (port 9090)
   - Grafana dashboards (port 3000)
   - Weekly performance summaries
   - CSV/JSON export capabilities

5. **Documentation**
   - `MULTI_ACCOUNT_GUIDE.md` - Comprehensive 13,000+ word guide
   - `MULTI_ACCOUNT_QUICK_START.md` - Quick reference
   - `MULTI_ACCOUNT_IMPLEMENTATION_SUMMARY.md` - Implementation details
   - This file - Deployment instructions

---

## 📋 Prerequisites

### Required Software

1. **Docker Desktop**
   - Windows: Download from https://www.docker.com/products/docker-desktop
   - Verify installation: `docker --version`

2. **Docker Compose**
   - Usually included with Docker Desktop
   - Verify installation: `docker-compose --version`

### Required Accounts

You already have 5 IQ Option accounts configured:

| Account | Email | Password | Strategy Profile |
|---------|-------|----------|------------------|
| 1 | tombonirinakaej@gmail.com | tombokael04 | Conservative |
| 2 | tombokael4@gmail.com | tombokael04 | Moderate |
| 3 | ruslantombofitiavana@gmail.com | tombokael04 | Aggressive |
| 4 | tombofifalianakimi@gmail.com | tombokael04 | Scalping |
| 5 | dinokamisy@gmail.com | tombokael04 | Trend Following |

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Navigate to Project Directory

```bash
cd /c/Users/jratombo/Desktop/dev_tools/pythonEnv/app/KAEL/KAEL
```

### Step 2: Verify Files Exist

```bash
# Check critical files
ls multi_account_parallel_bot.py
ls docker-compose.multi-account.yml
ls start_multi_account.sh
ls config/multi_account_config.py
ls database/multi_account_schema.sql
```

### Step 3: Create/Verify .env File

```bash
# If .env doesn't exist, create it
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Edit .env and set
nano .env
```

**Required .env settings**:
```bash
# CRITICAL: Set to 'demo' for testing, 'live' for real money
TRADING_MODE=demo

# Advanced strategies (required)
USE_ADVANCED_STRATEGIES=true

# Database
DATABASE_URL=postgresql://postgres:postgres@timescaledb:5432/kael

# Health API
ENABLE_HEALTH_API=true
HEALTH_API_PORT=5001

# Logging
LOG_LEVEL=INFO

# Trading assets
TRADING_ASSETS=EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,AUDJPY

# Trade amounts
BASE_TRADE_AMOUNT=1.0

# Risk management
MAX_CONSECUTIVE_LOSSES=5
MIN_BALANCE=50
```

### Step 4: Make Startup Script Executable

```bash
chmod +x start_multi_account.sh
```

### Step 5: Start the System

```bash
./start_multi_account.sh
```

**OR** using Docker Compose directly:

```bash
docker-compose -f docker-compose.multi-account.yml up -d --build
```

### Step 6: Verify System is Running

```bash
# Check all containers are running
docker-compose -f docker-compose.multi-account.yml ps

# Should show:
# - kael-multi-account-bot (running)
# - kael-timescaledb (running)
# - kael-prometheus (running)
# - kael-grafana (running)
# - kael-postgres-exporter (running)
```

### Step 7: Check Health

```bash
# Check health endpoint
curl http://localhost:5001/health

# Expected response:
# {"status":"ok","timestamp":"2025-01-15T12:00:00"}

# Check statistics
curl http://localhost:5001/statistics | jq

# Check accounts
curl http://localhost:5001/accounts | jq
```

---

## 📊 Accessing Dashboards

Once the system is running, access these URLs:

### 1. Health API (Main Dashboard)
**URL**: http://localhost:5001/statistics

**What you'll see**:
- Total accounts: 5
- Active accounts: 5
- Total trades (today)
- Total P&L
- Per-account breakdown

**Key Endpoints**:
- `/statistics` - Overall stats
- `/accounts` - All account status
- `/strategy_performance?days=7` - Strategy performance
- `/recent_trades?limit=20` - Recent trades
- `/export/csv?days=7` - Export to CSV
- `/export/json?days=7` - Export to JSON

### 2. Grafana (Visual Dashboards)
**URL**: http://localhost:3000
**Login**: admin / admin

**Dashboards** (will be created):
- Portfolio Overview
- Account Performance Comparison
- Strategy Performance Analysis
- Trade Execution Metrics

### 3. Prometheus (Metrics)
**URL**: http://localhost:9090

**Available Metrics**:
- `kael_account_balance`
- `kael_account_daily_pnl`
- `kael_strategy_win_rate`
- `kael_portfolio_total_balance`
- And 20+ more...

---

## 📈 Monitoring During Operation

### View Live Logs

```bash
# View all bot logs
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot

# View specific account activity
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "account_1"

# View errors only
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep ERROR
```

### Check Account Status

```bash
# Get all accounts status
curl http://localhost:5001/accounts | jq

# Get specific account
curl http://localhost:5001/account/account_1 | jq

# Check win rates
curl http://localhost:5001/accounts | jq '.accounts[] | {account_id, win_rate, daily_pnl}'
```

### Check Strategy Performance

```bash
# Get strategy stats (last 7 days)
curl "http://localhost:5001/strategy_performance?days=7" | jq

# Filter by specific metrics
curl "http://localhost:5001/strategy_performance?days=7" | jq '.strategy_stats[] | {strategy: .selected_strategy, win_rate, total_pnl}'
```

### View Recent Trades

```bash
# Get last 20 trades
curl "http://localhost:5001/recent_trades?limit=20" | jq

# Get trades for specific account
curl "http://localhost:5001/recent_trades?limit=20" | jq '.trades[] | select(.account_id == "account_1")'
```

---

## 📥 Exporting Data for Analysis

### Daily Export (Recommended)

```bash
# Export today's trades to CSV
curl "http://localhost:5001/export/csv?days=1" -o daily_trades_$(date +%Y%m%d).csv

# Export today's performance to JSON
curl "http://localhost:5001/export/json?days=1" -o daily_performance_$(date +%Y%m%d).json
```

### Weekly Export

```bash
# Export week's trades to CSV
curl "http://localhost:5001/export/csv?days=7" -o weekly_trades.csv

# Export week's performance to JSON
curl "http://localhost:5001/export/json?days=7" -o weekly_performance.json
```

### Account-Specific Export

```bash
# Export specific account trades
curl "http://localhost:5001/export/csv?account_id=account_1&days=7" -o account1_trades.csv
```

### Analysis in Excel/Google Sheets

1. Download CSV: `curl "http://localhost:5001/export/csv?days=7" -o trades.csv`
2. Open in Excel
3. Create Pivot Tables:
   - **Win Rate by Account**: Row=account_id, Value=COUNT(result="WIN")/COUNT(*)
   - **Win Rate by Strategy**: Row=selected_strategy, Value=Win Rate
   - **P&L by Account**: Row=account_id, Value=SUM(profit)
   - **P&L by Hour**: Row=HOUR(entry_time), Value=SUM(profit)

---

## 🔍 Performance Evaluation Process

### Week 1: Data Collection Phase

**Daily Tasks** (5 minutes):
```bash
# 1. Check all accounts are running
curl http://localhost:5001/accounts | jq '.accounts[] | {account_id, is_running, trades, win_rate}'

# 2. Export daily data
curl "http://localhost:5001/export/csv?days=1" -o daily_$(date +%Y%m%d).csv

# 3. Check for errors
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep ERROR | tail -20
```

**End of Week**:
```bash
# 1. Generate weekly summary
curl -X POST http://localhost:5001/generate_weekly_summary

# 2. View summary
curl http://localhost:5001/weekly_summary | jq > week1_summary.json

# 3. Export all trades
curl "http://localhost:5001/export/csv?days=7" -o week1_all_trades.csv

# 4. Export performance
curl "http://localhost:5001/export/json?days=7" -o week1_performance.json
```

### Week 1: Analysis

Open `week1_all_trades.csv` in Excel and analyze:

1. **Win Rate by Strategy Profile**
   - Which profile has highest win rate?
   - Which is lowest?
   - Are results within expected ranges?

2. **P&L by Strategy Profile**
   - Which profile is most profitable?
   - Which has highest average profit per trade?
   - Risk-adjusted returns (P&L / trades)?

3. **Trade Frequency**
   - Which profile trades most frequently?
   - Is frequency appropriate for strategy type?
   - Any periods of no trading?

4. **Time Analysis**
   - Best performing hours?
   - Worst performing hours?
   - Consider adjusting trading schedule?

5. **Strategy Breakdown**
   - Which individual strategies perform best?
   - Any strategies consistently losing?
   - Consider disabling underperformers?

### Decision Matrix (After Week 1)

| Metric | Threshold | Action if Not Met |
|--------|-----------|-------------------|
| Overall Win Rate | ≥ 60% | Investigate, adjust confidence thresholds |
| Account Win Rate | ≥ 55% per account | Disable or reconfigure underperforming account |
| Daily Loss Limits | Never exceeded | Verify risk management working |
| Trades per Day | 30-50 total | Adjust scan intervals or confidence |
| System Uptime | > 95% | Check logs for connection issues |

**Continue to Week 2-4** if:
- ✅ Overall win rate ≥ 60%
- ✅ No critical bugs
- ✅ System stable
- ✅ Data quality good

**Stop and Reconfigure** if:
- ❌ Win rate < 55%
- ❌ Frequent crashes
- ❌ Daily loss limits exceeded
- ❌ Accounts getting locked

---

## 🔧 Common Operations

### Restart the Bot

```bash
# Restart just the trading bot
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot

# Wait 10 seconds, then check
sleep 10
curl http://localhost:5001/health
```

### Stop the System

```bash
# Stop all services
docker-compose -f docker-compose.multi-account.yml down

# Stop but keep data
docker-compose -f docker-compose.multi-account.yml stop
```

### Start the System

```bash
# Start all services
docker-compose -f docker-compose.multi-account.yml up -d

# View logs
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot
```

### View Database Data

```bash
# Connect to database
docker exec -it kael-timescaledb psql -U postgres -d kael

# Then run SQL queries:

# View all accounts
SELECT * FROM accounts;

# View recent trades
SELECT * FROM trades ORDER BY entry_time DESC LIMIT 10;

# Account performance
SELECT * FROM v_daily_account_performance;

# Strategy performance
SELECT * FROM v_strategy_performance_summary;

# Exit
\q
```

### Backup Database

```bash
# Backup database to file
docker exec kael-timescaledb pg_dump -U postgres kael > backup_$(date +%Y%m%d).sql

# To restore later:
# docker exec -i kael-timescaledb psql -U postgres -d kael < backup_20250115.sql
```

### Reset Daily Stats (New Trading Day)

```bash
# Reset all accounts for new day
docker exec -it kael-timescaledb psql -U postgres -d kael -c "
  UPDATE accounts SET enabled = true, daily_pnl = 0, total_trades = 0;
"

# Restart bot to pick up changes
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

---

## ⚠️ Switching to Live Trading

**CRITICAL**: Only switch to live mode after:
- ✅ At least 1 week of demo testing
- ✅ Overall win rate ≥ 65%
- ✅ All accounts with win rate ≥ 60%
- ✅ No critical bugs
- ✅ Comfortable with risk management
- ✅ Analyzed and understand performance

### Steps to Switch to Live

1. **Update .env**:
```bash
nano .env
# Change:
TRADING_MODE=live
```

2. **Restart Bot**:
```bash
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

3. **Verify Live Mode**:
```bash
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "LIVE MODE"
# You should see: ⚠️ LIVE MODE for each account
```

4. **Monitor Closely**:
```bash
# Check every 10 minutes for first hour
watch -n 600 'curl http://localhost:5001/statistics | jq'
```

5. **Set Stop Loss**:
```bash
# If overall loss reaches -$50, stop immediately
# Monitor: curl http://localhost:5001/statistics | jq '.total_pnl'
```

---

## 🐛 Troubleshooting

### Problem: Accounts Not Connecting

**Symptoms**: Logs show "Connection failed"

**Solution**:
```bash
# Check logs
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "Connection failed"

# Verify credentials in config
cat config/accounts.json | jq '.accounts[] | {email, enabled}'

# Restart
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

### Problem: No Trades Being Placed

**Symptoms**: Bot running but no trades

**Check**:
```bash
# Account status
curl http://localhost:5001/accounts | jq '.accounts[] | {account_id, is_running, daily_pnl, consecutive_losses}'

# Warnings in logs
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep WARNING
```

**Possible Causes**:
- Daily loss limit reached
- Consecutive losses limit reached
- No instruments open (outside trading hours)
- Confidence threshold too high

### Problem: Database Connection Errors

**Solution**:
```bash
# Check database health
docker exec kael-timescaledb pg_isready -U postgres

# View database logs
docker-compose -f docker-compose.multi-account.yml logs timescaledb

# Restart database
docker-compose -f docker-compose.multi-account.yml restart timescaledb
```

### Problem: High Memory Usage

**Check**:
```bash
docker stats kael-multi-account-bot
```

**Solution**:
- Reduce `LOG_LEVEL` to `WARNING` in .env
- Reduce trade history retention
- Restart bot daily

---

## 📚 Additional Resources

### Documentation Files
- `MULTI_ACCOUNT_GUIDE.md` - Complete guide (13,000+ words)
- `MULTI_ACCOUNT_QUICK_START.md` - Quick reference
- `MULTI_ACCOUNT_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `ADVANCED_STRATEGIES_README.md` - Strategy documentation

### Log Files
- `./logs/multi_account_YYYYMMDD.log` - Daily logs
- `./reports/` - Exported reports

### Database
- `./pgdata/` - PostgreSQL data files

### Configuration
- `config/accounts.json` - Account configuration
- `.env` - Environment variables

---

## 📞 Support

### Check System Status
```bash
curl http://localhost:5001/statistics | jq
```

### View Logs
```bash
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot
```

### Check Database
```bash
docker exec -it kael-timescaledb psql -U postgres -d kael -c "SELECT * FROM v_daily_account_performance;"
```

---

## ✅ Success Checklist

After deployment, verify:

- [ ] All 5 containers running
- [ ] Health API responds at :5001
- [ ] All 5 accounts connected
- [ ] Prometheus scraping metrics at :9090
- [ ] Grafana accessible at :3000
- [ ] At least 1 trade placed by each account
- [ ] Trades logged to database
- [ ] CSV export works
- [ ] JSON export works
- [ ] No errors in logs

---

## 🎯 Summary

You now have a **complete multi-account parallel trading system** that will:

1. **Trade**: 5 concurrent accounts with different strategies
2. **Track**: Comprehensive metrics per account and strategy
3. **Monitor**: Real-time dashboards and API
4. **Export**: CSV/JSON reports for analysis
5. **Evaluate**: Data-driven strategy performance comparison

**Next Steps**:
1. ✅ Deploy system (5 minutes)
2. ✅ Verify all accounts trading (1 hour)
3. ✅ Monitor for 1 week (demo mode)
4. ✅ Export and analyze data
5. ✅ Identify best strategy profile
6. ✅ Consider live trading (if criteria met)

**Expected Outcome**: After 1 week, you'll have comprehensive data showing which of the 5 strategy profiles performs best, allowing for data-driven optimization.

Good luck! 🚀

---

**Deployment Date**: _________
**Started by**: _________
**Mode**: Demo / Live (circle one)
**Target**: Identify best performing strategy profile
