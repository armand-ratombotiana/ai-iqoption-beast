# 🤖 Multi-Account Parallel Trading System - Complete Guide

## Overview

This system enables **simultaneous trading** across **5 separate IQ Option accounts**, each running a **different strategy profile**. This architecture provides:

- **Performance Comparison**: Evaluate which strategy profiles perform best
- **Risk Distribution**: Spread risk across multiple accounts
- **Parallel Execution**: No API rate limiting issues between accounts
- **Comprehensive Analytics**: Track performance per account and strategy
- **Automated Reporting**: Weekly summaries and exportable reports

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Account Configuration](#account-configuration)
3. [Strategy Profiles](#strategy-profiles)
4. [Getting Started](#getting-started)
5. [Monitoring & Analytics](#monitoring--analytics)
6. [Performance Evaluation](#performance-evaluation)
7. [Exporting Reports](#exporting-reports)
8. [API Endpoints](#api-endpoints)
9. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                Multi-Account Orchestrator                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐│
│  │ Account 1 │  │ Account 2 │  │ Account 3 │  │ Account 4 ││
│  │Conservative│  │ Moderate  │  │Aggressive │  │ Scalping  ││
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘│
│        │              │              │              │        │
│        └──────────────┴──────────────┴──────────────┘        │
│                            │                                  │
│                    ┌───────▼───────┐                         │
│                    │  TimescaleDB  │                         │
│                    │ Multi-Account │                         │
│                    │    Tracking   │                         │
│                    └───────┬───────┘                         │
│                            │                                  │
│        ┌───────────────────┴───────────────────┐            │
│        │                                         │            │
│  ┌─────▼─────┐                          ┌──────▼──────┐     │
│  │Prometheus │                          │   Grafana   │     │
│  │  Metrics  │                          │ Dashboards  │     │
│  └───────────┘                          └─────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **Parallel Execution**: Each account runs in its own dedicated thread
- **Independent Strategies**: Each account uses a different strategy profile
- **Centralized Logging**: All trades logged to TimescaleDB
- **Real-time Metrics**: Prometheus + Grafana monitoring
- **RESTful API**: Health monitoring and statistics endpoints
- **Export Capabilities**: CSV and JSON report generation

---

## Account Configuration

### Default Accounts

The system is pre-configured with 5 accounts:

| Account ID | Email | Strategy Profile | Max Daily Loss | Max Trade Amount |
|-----------|-------|------------------|----------------|------------------|
| account_1 | tombonirinakaej@gmail.com | Conservative | $5.00 | $1.50 |
| account_2 | tombokael4@gmail.com | Moderate | $8.00 | $2.00 |
| account_3 | ruslantombofitiavana@gmail.com | Aggressive | $15.00 | $3.00 |
| account_4 | tombofifalianakimi@gmail.com | Scalping | $10.00 | $2.50 |
| account_5 | dinokamisy@gmail.com | Trend Following | $10.00 | $2.50 |

### Account Configuration File

Accounts are managed in `config/accounts.json`:

```json
{
  "accounts": {
    "account_1": {
      "account_id": "account_1",
      "email": "tombonirinakaej@gmail.com",
      "password": "tombokael04",
      "strategy_profile": "conservative",
      "enabled": true,
      "max_daily_loss": 5.0,
      "max_trade_amount": 1.5,
      "trading_mode": "demo"
    }
  }
}
```

### Modifying Accounts

To add/modify accounts, edit `config/multi_account_config.py` and restart the system.

---

## Strategy Profiles

### 1. Conservative

**Goal**: Capital preservation with high-probability setups

**Configuration**:
- Min Confidence: 85%
- Min Confluence: 3 strategies must agree
- Enabled Strategies: `bollinger_rsi_combo`, `rsi_divergence`, `trend_alignment`
- Max Trade Amount: $1.50
- Max Daily Loss: $5.00

**Best For**:
- Starting out
- Rebuilding after losses
- Uncertain markets

**Expected Win Rate**: 70-80%

---

### 2. Moderate (Default)

**Goal**: Balanced approach between risk and opportunity

**Configuration**:
- Min Confidence: 78%
- Min Confluence: 2 strategies must agree
- Enabled Strategies: `enhanced_candle_count`, `bollinger_rsi_combo`, `macd_momentum`, `trend_alignment`
- Max Trade Amount: $2.00
- Max Daily Loss: $8.00

**Best For**:
- Normal trading
- Stable markets
- Confident in system

**Expected Win Rate**: 65-75%

---

### 3. Aggressive

**Goal**: Maximize opportunities with higher risk tolerance

**Configuration**:
- Min Confidence: 70%
- Min Confluence: 2 strategies
- Enabled Strategies: `enhanced_candle_count`, `macd_momentum`, `stochastic`, `support_resistance`
- Max Trade Amount: $3.00
- Max Daily Loss: $15.00

**Best For**:
- Strong trends
- High win rate periods
- Larger accounts (> $200)

**Expected Win Rate**: 60-70%

---

### 4. Scalping

**Goal**: Quick, frequent trades on short-term movements

**Configuration**:
- Min Confidence: 75%
- Min Confluence: 2 strategies
- Enabled Strategies: `enhanced_candle_count`, `stochastic`, `support_resistance`
- Max Trade Amount: $2.50
- Max Daily Loss: $10.00

**Best For**:
- Range-bound markets
- Quick reversals
- High-frequency trading

**Expected Win Rate**: 60-70%

---

### 5. Trend Following

**Goal**: Capture strong directional moves

**Configuration**:
- Min Confidence: 80%
- Min Confluence: 2 strategies
- Enabled Strategies: `trend_alignment`, `macd_momentum`, `enhanced_candle_count`
- Max Trade Amount: $2.50
- Max Daily Loss: $10.00

**Best For**:
- Strong trending markets
- Momentum trading
- Clear directional bias

**Expected Win Rate**: 65-75%

---

## Getting Started

### Prerequisites

1. **Docker & Docker Compose** installed
2. **5 IQ Option accounts** (credentials above)
3. **PostgreSQL/TimescaleDB** (included in Docker setup)

### Quick Start

#### 1. Clone/Navigate to Repository

```bash
cd /path/to/KAEL
```

#### 2. Create/Update `.env` File

```bash
# Copy example
cp .env.example .env

# Edit with your settings
nano .env
```

**Required Environment Variables**:

```bash
# Trading Mode (IMPORTANT!)
TRADING_MODE=demo  # or 'live' for real money

# Advanced Strategies
USE_ADVANCED_STRATEGIES=true

# Database
DATABASE_URL=postgresql://postgres:postgres@timescaledb:5432/kael

# Health API
ENABLE_HEALTH_API=true
HEALTH_API_PORT=5001

# Logging
LOG_LEVEL=INFO
```

#### 3. Start the System

```bash
# Using startup script (recommended)
chmod +x start_multi_account.sh
./start_multi_account.sh

# Or using Docker Compose directly
docker-compose -f docker-compose.multi-account.yml up -d --build
```

#### 4. Verify System is Running

```bash
# Check all services
docker-compose -f docker-compose.multi-account.yml ps

# Check bot logs
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot

# Check health
curl http://localhost:5001/health
```

#### 5. Access Dashboards

- **Health API**: http://localhost:5001
- **Statistics**: http://localhost:5001/statistics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

---

## Monitoring & Analytics

### Real-Time Monitoring

#### Health API Dashboard

The Health API provides comprehensive real-time statistics:

**GET /statistics**
```bash
curl http://localhost:5001/statistics | jq
```

Response:
```json
{
  "total_accounts": 5,
  "active_accounts": 5,
  "total_trades": 42,
  "total_pnl": 15.50,
  "total_balance": 525.00,
  "accounts": [
    {
      "account_id": "account_1",
      "email": "tombonirinakaej@gmail.com",
      "strategy_profile": "conservative",
      "trades": 8,
      "wins": 6,
      "losses": 2,
      "win_rate": 75.0,
      "daily_pnl": 3.20,
      "balance": 103.20,
      "is_running": true
    }
  ]
}
```

#### Account-Specific Stats

**GET /account/{account_id}**
```bash
curl http://localhost:5001/account/account_1 | jq
```

#### Strategy Performance

**GET /strategy_performance?days=7**
```bash
curl "http://localhost:5001/strategy_performance?days=7" | jq
```

Response:
```json
{
  "strategy_stats": [
    {
      "selected_strategy": "bollinger_rsi_combo",
      "total_trades": 15,
      "wins": 12,
      "losses": 3,
      "win_rate": 80.0,
      "total_pnl": 8.50,
      "avg_profit_per_trade": 0.57,
      "accounts_using": 2
    }
  ]
}
```

#### Recent Trades

**GET /recent_trades?limit=100**
```bash
curl "http://localhost:5001/recent_trades?limit=20" | jq
```

### Grafana Dashboards

Access Grafana at http://localhost:3000

**Pre-configured Dashboards**:

1. **Portfolio Overview**
   - Total P&L
   - Total trades
   - Overall win rate
   - Balance trends

2. **Account Performance**
   - Per-account metrics
   - Win rate comparison
   - Daily P&L charts
   - Balance evolution

3. **Strategy Performance**
   - Per-strategy win rates
   - P&L by strategy
   - Trade count comparison
   - Confidence levels

### Prometheus Metrics

Access Prometheus at http://localhost:9090

**Available Metrics**:

```
# Account metrics
kael_account_balance{account_id, strategy_profile}
kael_account_daily_pnl{account_id, strategy_profile}
kael_account_total_trades{account_id, strategy_profile}
kael_account_wins{account_id, strategy_profile}
kael_account_losses{account_id, strategy_profile}
kael_account_win_rate{account_id, strategy_profile}

# Strategy metrics
kael_strategy_total_trades{strategy}
kael_strategy_wins{strategy}
kael_strategy_total_pnl{strategy}
kael_strategy_win_rate{strategy}

# Portfolio metrics
kael_portfolio_total_balance
kael_portfolio_daily_pnl
kael_active_accounts
kael_healthy_accounts

# Performance metrics
kael_trade_execution_time_ms
kael_api_response_time_ms
```

---

## Performance Evaluation

### Daily Performance Tracking

The system automatically tracks:

1. **Per-Account Metrics**:
   - Total trades
   - Win/loss count
   - Win rate
   - Daily P&L
   - Average confidence
   - Execution time

2. **Per-Strategy Metrics**:
   - Trades executed
   - Win rate
   - Total P&L
   - Average profit per trade
   - Payout ratios

3. **Portfolio Metrics**:
   - Total trades across all accounts
   - Overall win rate
   - Total P&L
   - Best/worst performing accounts
   - Best/worst performing strategies

### Weekly Summaries

**Generate Weekly Summary**:

```bash
# Via API
curl -X POST http://localhost:5001/generate_weekly_summary

# View weekly summary
curl http://localhost:5001/weekly_summary | jq
```

**Weekly Summary Includes**:

- Total accounts active
- Total trades
- Overall win rate
- Total P&L
- Best performing account
- Worst performing account
- Best performing strategy
- Worst performing strategy
- Per-account breakdown
- Per-strategy breakdown

### Performance Analysis

#### Win Rate by Strategy Profile

Query the database:

```sql
SELECT
    a.strategy_profile,
    COUNT(t.id) as trades,
    SUM(CASE WHEN t.result = 'WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(CASE WHEN t.result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(SUM(COALESCE(t.profit, 0)), 2) as total_pnl
FROM accounts a
LEFT JOIN trades t ON a.account_id = t.account_id
WHERE t.entry_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY a.strategy_profile
ORDER BY win_rate DESC;
```

#### Best Performing Strategies

```sql
SELECT
    selected_strategy,
    COUNT(*) as trades,
    ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(SUM(COALESCE(profit, 0)), 2) as total_pnl,
    ROUND(AVG(confidence), 2) as avg_confidence
FROM trades
WHERE entry_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY selected_strategy
ORDER BY total_pnl DESC;
```

#### Account Performance Comparison

```sql
SELECT * FROM v_daily_account_performance
ORDER BY daily_pnl DESC;
```

---

## Exporting Reports

### Export Trades to CSV

#### Via API

```bash
# Export all accounts (last 7 days)
curl "http://localhost:5001/export/csv?days=7" -o trades_all.csv

# Export specific account
curl "http://localhost:5001/export/csv?account_id=account_1&days=7" -o trades_account1.csv

# Export last 30 days
curl "http://localhost:5001/export/csv?days=30" -o trades_30days.csv
```

#### Via Python

```python
from database.multi_account_logger import MultiAccountTradeLogger

logger = MultiAccountTradeLogger('postgresql://postgres:postgres@localhost:5432/kael')

# Export all trades
logger.export_trades_to_csv('reports/trades.csv', days=7)

# Export specific account
logger.export_trades_to_csv('reports/account1.csv', account_id='account_1', days=7)
```

### Export Performance to JSON

#### Via API

```bash
# Export performance summary
curl "http://localhost:5001/export/json?days=7" -o performance.json
```

#### Via Python

```python
from database.multi_account_logger import MultiAccountTradeLogger

logger = MultiAccountTradeLogger('postgresql://postgres:postgres@localhost:5432/kael')
logger.export_performance_to_json('reports/performance.json', days=7)
```

### CSV Format

```csv
id,account_id,email,strategy_profile,instrument,direction,amount,entry_time,exit_time,result,profit,payout_ratio,selected_strategy,confidence
1,account_1,tombonirinakaej@gmail.com,conservative,EURUSD-OTC,CALL,1.50,2025-01-15 10:30:00,2025-01-15 10:31:05,WIN,1.20,0.80,bollinger_rsi_combo,85
```

### JSON Format

```json
{
  "generated_at": "2025-01-15T12:00:00",
  "period_days": 7,
  "accounts": [
    {
      "account_id": "account_1",
      "total_trades": 45,
      "wins": 32,
      "losses": 13,
      "win_rate": 71.11,
      "total_pnl": 12.50,
      "avg_confidence": 82.5
    }
  ],
  "strategies": [
    {
      "selected_strategy": "bollinger_rsi_combo",
      "total_trades": 28,
      "wins": 22,
      "win_rate": 78.57,
      "total_pnl": 15.30,
      "accounts_using": 2
    }
  ]
}
```

---

## API Endpoints

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/statistics` | GET | Overall statistics |
| `/accounts` | GET | All accounts status |
| `/account/<account_id>` | GET | Specific account details |

### Performance

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/strategy_performance?days=7` | GET | Strategy performance stats |
| `/recent_trades?limit=100` | GET | Recent trades |
| `/weekly_summary` | GET | Weekly performance summary |

### Export

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/export/csv?days=7` | GET | Export trades to CSV |
| `/export/csv?account_id=account_1&days=7` | GET | Export account trades to CSV |
| `/export/json?days=7` | GET | Export performance to JSON |

### Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/stop` | POST | Stop trading bot |
| `/metrics` | GET | Prometheus metrics |

### Example API Usage

#### Get Overall Statistics

```bash
curl http://localhost:5001/statistics | jq '.accounts[] | {account_id, win_rate, daily_pnl}'
```

#### Get Strategy Performance

```bash
curl "http://localhost:5001/strategy_performance?days=7" | jq '.strategy_stats[] | {strategy: .selected_strategy, win_rate, total_pnl}'
```

#### Export This Week's Trades

```bash
curl "http://localhost:5001/export/csv?days=7" -o weekly_trades.csv
```

---

## Troubleshooting

### Common Issues

#### 1. Accounts Not Connecting

**Problem**: One or more accounts fail to connect

**Solution**:
```bash
# Check logs
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "Connection failed"

# Verify credentials in config/accounts.json
cat config/accounts.json | jq '.accounts[] | {email, enabled}'

# Restart specific account (edit config and restart)
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

#### 2. Database Connection Issues

**Problem**: Cannot connect to TimescaleDB

**Solution**:
```bash
# Check database is running
docker-compose -f docker-compose.multi-account.yml ps timescaledb

# Check database health
docker exec kael-timescaledb pg_isready -U postgres

# View database logs
docker-compose -f docker-compose.multi-account.yml logs timescaledb

# Restart database
docker-compose -f docker-compose.multi-account.yml restart timescaledb
```

#### 3. No Trades Being Placed

**Problem**: Bot is running but not placing trades

**Possible Causes**:
- Daily loss limit reached
- Consecutive losses limit reached
- No instruments open
- Confidence threshold too high

**Check**:
```bash
# View account status
curl http://localhost:5001/accounts | jq

# Check logs for warnings
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "WARNING"

# View recent trades
curl "http://localhost:5001/recent_trades?limit=10" | jq
```

#### 4. High API Rate Limiting

**Problem**: Seeing many API rate limit errors

**Solution**:
```bash
# Increase API minimum interval in .env
API_MIN_INTERVAL=0.5  # Default is 0.3

# Restart bot
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

### Log Locations

- **Bot Logs**: `./logs/multi_account_YYYYMMDD.log`
- **Docker Logs**: `docker-compose -f docker-compose.multi-account.yml logs`
- **Database Logs**: `docker-compose -f docker-compose.multi-account.yml logs timescaledb`

### Useful Commands

```bash
# View all running containers
docker-compose -f docker-compose.multi-account.yml ps

# Restart bot only
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot

# Stop everything
docker-compose -f docker-compose.multi-account.yml down

# Start everything
docker-compose -f docker-compose.multi-account.yml up -d

# View logs (all services)
docker-compose -f docker-compose.multi-account.yml logs -f

# View bot logs only
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot

# Execute SQL query
docker exec -it kael-timescaledb psql -U postgres -d kael -c "SELECT * FROM accounts;"

# Backup database
docker exec kael-timescaledb pg_dump -U postgres kael > backup_$(date +%Y%m%d).sql

# Reset daily stats (new day)
docker exec -it kael-timescaledb psql -U postgres -d kael -c "UPDATE accounts SET daily_pnl = 0, total_trades = 0;"
```

---

## Best Practices

### 1. Start with Demo Mode

Always test with `TRADING_MODE=demo` first:

```bash
# In .env
TRADING_MODE=demo
```

### 2. Monitor Daily Loss Limits

Each account has its own daily loss limit. Monitor carefully:

```bash
curl http://localhost:5001/accounts | jq '.accounts[] | {account_id, daily_pnl, max_daily_loss: .max_daily_loss}'
```

### 3. Review Performance Weekly

Generate and review weekly summaries:

```bash
# Generate summary
curl -X POST http://localhost:5001/generate_weekly_summary

# View summary
curl http://localhost:5001/weekly_summary | jq
```

### 4. Export Data Regularly

Backup your trading data:

```bash
# Export trades
curl "http://localhost:5001/export/csv?days=30" -o backup_trades_$(date +%Y%m%d).csv

# Export performance
curl "http://localhost:5001/export/json?days=30" -o backup_perf_$(date +%Y%m%d).json
```

### 5. Monitor System Resources

```bash
# Check resource usage
docker stats kael-multi-account-bot

# Check disk space
df -h ./pgdata
```

---

## Summary

The Multi-Account Parallel Trading System provides:

✅ **5 concurrent accounts** with different strategy profiles
✅ **Comprehensive performance tracking** per account and strategy
✅ **Real-time monitoring** via API, Prometheus, and Grafana
✅ **Weekly performance summaries** for evaluation
✅ **CSV/JSON export** for detailed analysis
✅ **Independent risk management** per account
✅ **Automated daily performance updates**

**Expected Results**:
- 65-75% overall win rate (varies by strategy profile)
- Identify best performing strategy profiles
- Data-driven strategy optimization
- Comprehensive performance history

---

## Support

For issues or questions:
1. Check logs: `./logs/multi_account_YYYYMMDD.log`
2. Review API: `http://localhost:5001/statistics`
3. Check database: `docker exec -it kael-timescaledb psql -U postgres -d kael`
4. View Grafana dashboards: `http://localhost:3000`

---

**Remember**: This is a trading system. Always start in DEMO mode, monitor performance carefully, and only switch to live trading once you're confident in the system's performance.

Good luck! 🚀
