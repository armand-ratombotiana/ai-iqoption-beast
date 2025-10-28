# 🚀 Multi-Account Multi-Strategy Trading System

## Complete Setup and Deployment Guide

This system runs **5 trading accounts simultaneously**, each with a different strategy profile, providing comprehensive performance evaluation and comparison.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Running the System](#running-the-system)
5. [Monitoring & Analytics](#monitoring--analytics)
6. [Performance Evaluation](#performance-evaluation)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Multi-Strategy Orchestrator                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Account 1   │  │  Account 2   │  │  Account 3   │      │
│  │ Conservative │  │   Moderate   │  │  Aggressive  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Account 4   │  │  Account 5   │                        │
│  │   Scalping   │  │Trend Following│                        │
│  └──────────────┘  └──────────────┘                        │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│              Database (PostgreSQL/TimescaleDB)               │
│  • Trade Logging  • Performance Tracking  • Analytics       │
└─────────────────────────────────────────────────────────────┘
```

### Strategy Profiles

| Account | Email | Strategy | Min Confidence | Max Trade | Max Daily Loss |
|---------|-------|----------|----------------|-----------|----------------|
| Account 1 | tombonirinakaej@gmail.com | Conservative | 85% | $1.50 | $5.00 |
| Account 2 | tombokael4@gmail.com | Moderate | 78% | $2.00 | $8.00 |
| Account 3 | ruslantombofitiavana@gmail.com | Aggressive | 70% | $3.00 | $15.00 |
| Account 4 | tombofifalianakimi@gmail.com | Scalping | 75% | $2.50 | $10.00 |
| Account 5 | dinokamisy@gmail.com | Trend Following | 80% | $2.50 | $10.00 |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ or Docker
- Git

### 1. Clone and Setup

```bash
# Clone repository
cd KAEL

# Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary  # For database support

# Install TA-Lib (optional but recommended)
# Linux/Mac:
pip install TA-Lib

# Windows: Download wheel from https://github.com/cgohlke/talib-build/releases
pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl
```

### 2. Database Setup

#### Option A: Using Docker (Recommended)

```bash
# Start database
docker-compose up -d timescaledb

# Wait for database to be ready
sleep 10

# Initialize schema
docker exec -i kael-timescaledb psql -U postgres -d kael < database/multi_account_schema.sql
```

#### Option B: Local PostgreSQL

```bash
# Create database
createdb kael

# Initialize schema
psql -U postgres -d kael -f database/multi_account_schema.sql
```

### 3. Configure Environment

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kael

# Trading Mode
TRADING_MODE=demo  # or 'live' for real money

# Advanced Strategies
USE_ADVANCED_STRATEGIES=true
STRATEGY_RISK_PROFILE=moderate
```

### 4. Run the System

```bash
# Start multi-strategy orchestrator
python multi_strategy_orchestrator.py
```

---

## 🔧 Detailed Setup

### Step 1: Account Configuration

The system automatically creates configuration for 5 accounts on first run. To customize:

```python
# Edit config/accounts.json after first run
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
    },
    // ... other accounts
  }
}
```

### Step 2: Strategy Configuration

Each strategy profile has specific settings:

```python
# Conservative Strategy
- Min Confidence: 85%
- Min Confluence: 3 strategies must agree
- Enabled Strategies: Bollinger+RSI, RSI Divergence, Trend Alignment
- Focus: High probability, low risk

# Moderate Strategy
- Min Confidence: 78%
- Min Confluence: 2 strategies must agree
- Enabled Strategies: Candle Count, Bollinger+RSI, MACD, Trend Alignment
- Focus: Balanced risk/reward

# Aggressive Strategy
- Min Confidence: 70%
- Min Confluence: 2 strategies must agree
- Enabled Strategies: Candle Count, MACD, Stochastic, Support/Resistance
- Focus: More opportunities, higher risk

# Scalping Strategy
- Min Confidence: 75%
- Min Confluence: 2 strategies must agree
- Enabled Strategies: Candle Count, Stochastic, Support/Resistance
- Focus: Quick trades, short-term movements

# Trend Following Strategy
- Min Confidence: 80%
- Min Confluence: 2 strategies must agree
- Enabled Strategies: Trend Alignment, MACD, Candle Count
- Focus: Riding strong trends
```

### Step 3: Database Schema

The system uses comprehensive tables:

- **accounts**: Account configurations and health status
- **trades**: All trade records with full details
- **account_performance**: Daily performance snapshots
- **strategy_performance**: Per-strategy metrics
- **weekly_performance**: Weekly summaries
- **system_events**: System logs and events

---

## 🎮 Running the System

### Standard Mode

```bash
# Run with default settings
python multi_strategy_orchestrator.py
```

### Docker Mode

```bash
# Build and run everything
docker-compose -f docker-compose.parallel.yml up --build

# Run in background
docker-compose -f docker-compose.parallel.yml up -d

# View logs
docker-compose -f docker-compose.parallel.yml logs -f parallel-trading-bot

# Stop
docker-compose -f docker-compose.parallel.yml down
```

### Monitoring Logs

```bash
# Real-time logs
tail -f logs/multi_strategy_$(date +%Y%m%d).log

# Filter by account
tail -f logs/multi_strategy_$(date +%Y%m%d).log | grep "account_1"

# Filter by strategy
tail -f logs/multi_strategy_$(date +%Y%m%d).log | grep "conservative"
```

---

## 📊 Monitoring & Analytics

### Real-Time Dashboard

Access the dashboard at: `http://localhost:5001`

Features:
- Live account status
- Real-time P&L tracking
- Strategy performance comparison
- Trade history
- System health monitoring

### Grafana Dashboards

Access Grafana at: `http://localhost:3000` (admin/admin)

Pre-configured dashboards:
- Portfolio Overview
- Account Comparison
- Strategy Performance
- Risk Metrics
- System Health

### Database Queries

```sql
-- Daily performance by account
SELECT * FROM v_daily_account_performance;

-- Strategy performance summary
SELECT * FROM v_strategy_performance_summary;

-- Recent trades
SELECT * FROM v_recent_trades LIMIT 50;

-- Weekly summary
SELECT * FROM weekly_performance 
WHERE week_start >= CURRENT_DATE - INTERVAL '4 weeks'
ORDER BY week_start DESC;
```

---

## 📈 Performance Evaluation

### Automated Reports

The system generates reports automatically:

```python
from database.multi_account_logger import MultiAccountTradeLogger

logger = MultiAccountTradeLogger('postgresql://...')

# Generate weekly summary
logger.generate_weekly_summary()

# Export to CSV
logger.export_trades_to_csv('reports/trades_week.csv', days=7)

# Export to JSON
logger.export_performance_to_json('reports/performance.json', days=7)
```

### Manual Analysis

```bash
# Generate performance report
python -c "
from database.multi_account_logger import MultiAccountTradeLogger
import os

logger = MultiAccountTradeLogger(os.getenv('DATABASE_URL'))

# Get portfolio summary
summary = logger.get_portfolio_summary()
print('Portfolio Summary:')
print(f'Total Accounts: {summary[\"overall\"][\"total_accounts\"]}')
print(f'Total Trades: {summary[\"overall\"][\"total_trades\"]}')
print(f'Win Rate: {summary[\"overall\"][\"overall_win_rate\"]}%')
print(f'Total P&L: \${summary[\"overall\"][\"total_pnl\"]:.2f}')

# Account breakdown
print('\nAccount Performance:')
for acc in summary['accounts']:
    print(f'{acc[\"account_id\"]}: {acc[\"strategy_profile\"]} | '
          f'Trades: {acc[\"total_trades\"]} | '
          f'Win Rate: {acc[\"win_rate\"]}% | '
          f'P&L: \${acc[\"daily_pnl\"]:.2f}')
"
```

### Key Metrics to Track

1. **Win Rate by Strategy**
   - Target: 65-70% overall
   - Conservative: 70-75%
   - Moderate: 65-70%
   - Aggressive: 60-65%

2. **Profit Factor**
   - Total Profit / Total Loss
   - Target: > 1.5

3. **Sharpe Ratio**
   - Risk-adjusted returns
   - Target: > 1.0

4. **Max Drawdown**
   - Largest peak-to-trough decline
   - Target: < 20%

5. **Average Trade Duration**
   - Time from entry to exit
   - Target: 60-70 seconds

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check database is running
docker ps | grep timescaledb

# Test connection
psql -U postgres -h localhost -d kael -c "SELECT 1"

# Restart database
docker-compose restart timescaledb
```

#### 2. Account Connection Failed

```bash
# Check credentials in config/accounts.json
# Verify IQOption account is active
# Check network connectivity
# Review logs for specific error
```

#### 3. No Trades Executing

```bash
# Check market hours (binary options availability)
# Verify strategy confidence thresholds
# Check daily loss limits not reached
# Review signal generation logs
```

#### 4. Strategy Not Generating Signals

```bash
# Verify TA-Lib is installed
pip list | grep TA-Lib

# Check candle data availability
# Review strategy configuration
# Lower confidence threshold temporarily for testing
```

### Debug Mode

```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python multi_strategy_orchestrator.py
```

### Health Checks

```python
# Check system health
from config.multi_account_config import get_account_manager

manager = get_account_manager()
summary = manager.get_summary()

print(f"Healthy Accounts: {summary['healthy_accounts']}/{summary['total_accounts']}")
print(f"Enabled Accounts: {summary['enabled_accounts']}")

for acc in summary['accounts']:
    print(f"{acc['account_id']}: "
          f"Enabled={acc['enabled']}, "
          f"Healthy={acc['healthy']}, "
          f"Failures={acc['connection_failures']}")
```

---

## 📝 Git Workflow

### Automated Commits

The system can automatically commit performance data:

```bash
# Create git hooks
cat > .git/hooks/post-trade << 'EOF'
#!/bin/bash
# Auto-commit after significant trades
git add logs/ database_files/ config/accounts.json
git commit -m "feat: trading session $(date +%Y-%m-%d_%H:%M)"
EOF

chmod +x .git/hooks/post-trade
```

### Manual Commits

```bash
# Commit configuration changes
git add config/
git commit -m "feat: update account configurations"

# Commit performance reports
git add reports/
git commit -m "docs: add weekly performance report"

# Push to remote
git push origin main
```

---

## 🎯 Performance Goals

### Week 1: Validation Phase
- **Goal**: Validate system stability
- **Metrics**: 
  - All 5 accounts running without errors
  - At least 50 trades per account
  - Win rate > 55%
  - No system crashes

### Week 2-4: Optimization Phase
- **Goal**: Optimize strategy parameters
- **Metrics**:
  - Win rate > 60%
  - Profit factor > 1.3
  - Identify best-performing strategy
  - Adjust underperforming strategies

### Month 2+: Production Phase
- **Goal**: Consistent profitability
- **Metrics**:
  - Win rate > 65%
  - Profit factor > 1.5
  - Positive monthly returns
  - Sharpe ratio > 1.0

---

## 📚 Additional Resources

- [Advanced Strategies README](ADVANCED_STRATEGIES_README.md)
- [Database Schema Documentation](database/multi_account_schema.sql)
- [API Documentation](docs/API.md)
- [Strategy Configuration Guide](strategies/README.md)

---

## 🆘 Support

For issues or questions:
1. Check logs: `logs/multi_strategy_*.log`
2. Review database: `psql -U postgres -d kael`
3. Check system events: `SELECT * FROM system_events ORDER BY event_time DESC LIMIT 20;`
4. Review account health: `SELECT * FROM accounts;`

---

## ⚠️ Important Notes

1. **Start with Demo Mode**: Always test with demo accounts first
2. **Monitor Daily**: Check performance daily for first 2 weeks
3. **Respect Limits**: Never exceed configured daily loss limits
4. **Backup Data**: Regular database backups recommended
5. **Update Regularly**: Keep strategies and system updated

---

## 🚀 Next Steps

1. ✅ Complete setup following this guide
2. ✅ Run system in demo mode for 1 week
3. ✅ Analyze performance data
4. ✅ Optimize strategy parameters
5. ✅ Consider live trading (with caution)

---

**Good luck with your multi-strategy trading system!** 🎯📈
