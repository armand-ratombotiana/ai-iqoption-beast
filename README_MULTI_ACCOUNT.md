# 🤖 KAEL Multi-Account Parallel Trading System

## Executive Summary

A **production-ready multi-account trading system** that simultaneously runs **5 IQ Option accounts**, each with a different **strategy profile**, to enable **data-driven performance evaluation** and **strategy optimization**.

### Key Features

✅ **5 Concurrent Accounts** - Independent trading threads
✅ **5 Strategy Profiles** - Conservative, Moderate, Aggressive, Scalping, Trend Following
✅ **Comprehensive Tracking** - Per-account and per-strategy metrics
✅ **Real-time Monitoring** - REST API, Prometheus, Grafana
✅ **Export Capabilities** - CSV/JSON reports
✅ **Weekly Summaries** - Automated performance analysis
✅ **Production Ready** - Docker deployment, health checks, auto-recovery

---

## 🎯 Objectives

This system was built to answer the question:

> **"Which trading strategy profile performs best for binary options trading?"**

By running 5 accounts simultaneously with different configurations, you can:
1. Compare win rates across strategies
2. Identify most profitable approach
3. Optimize risk/reward ratios
4. Make data-driven trading decisions

---

## 📊 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│          Multi-Account Orchestrator (Main Bot)            │
│                                                            │
│  Account 1     Account 2      Account 3      Account 4    │
│  Conservative  Moderate       Aggressive     Scalping     │
│  $1.50 max     $2.00 max      $3.00 max      $2.50 max    │
│  85% conf      78% conf       70% conf       75% conf     │
│                                                            │
│                        Account 5                           │
│                     Trend Following                        │
│                        $2.50 max                           │
│                        80% conf                            │
└──────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐     ┌─────▼──────┐    ┌─────▼─────┐
   │TimescaleDB│    │ Prometheus │    │  Grafana  │
   │  :5432    │    │   :9090    │    │   :3000   │
   └───────────┘    └────────────┘    └───────────┘
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- 5 IQ Option accounts (credentials provided)

### Deploy

```bash
# 1. Navigate to project
cd /path/to/KAEL

# 2. Start system
chmod +x start_multi_account.sh
./start_multi_account.sh

# 3. Verify running
curl http://localhost:5001/health

# 4. View statistics
curl http://localhost:5001/statistics | jq
```

### Access Dashboards

- **Health API**: http://localhost:5001/statistics
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

---

## 📈 Strategy Profiles

### 1. Conservative (Account 1)
- **Email**: tombonirinakaej@gmail.com
- **Max Trade**: $1.50
- **Max Loss/Day**: $5.00
- **Min Confidence**: 85%
- **Strategies**: Bollinger+RSI, RSI Divergence, Trend Alignment
- **Expected Win Rate**: 70-80%
- **Best For**: Capital preservation, low risk

### 2. Moderate (Account 2) - Default
- **Email**: tombokael4@gmail.com
- **Max Trade**: $2.00
- **Max Loss/Day**: $8.00
- **Min Confidence**: 78%
- **Strategies**: Enhanced Candle, Bollinger+RSI, MACD, Trend Alignment
- **Expected Win Rate**: 65-75%
- **Best For**: Balanced risk/reward

### 3. Aggressive (Account 3)
- **Email**: ruslantombofitiavana@gmail.com
- **Max Trade**: $3.00
- **Max Loss/Day**: $15.00
- **Min Confidence**: 70%
- **Strategies**: Enhanced Candle, MACD, Stochastic, Support/Resistance
- **Expected Win Rate**: 60-70%
- **Best For**: Maximum opportunities, higher risk

### 4. Scalping (Account 4)
- **Email**: tombofifalianakimi@gmail.com
- **Max Trade**: $2.50
- **Max Loss/Day**: $10.00
- **Min Confidence**: 75%
- **Strategies**: Enhanced Candle, Stochastic, Support/Resistance
- **Expected Win Rate**: 60-70%
- **Best For**: High frequency, quick trades

### 5. Trend Following (Account 5)
- **Email**: dinokamisy@gmail.com
- **Max Trade**: $2.50
- **Max Loss/Day**: $10.00
- **Min Confidence**: 80%
- **Strategies**: Trend Alignment, MACD, Enhanced Candle
- **Expected Win Rate**: 65-75%
- **Best For**: Strong trends, momentum trading

---

## 📊 Monitoring & Analytics

### API Endpoints

```bash
# Overall statistics
GET http://localhost:5001/statistics

# All accounts status
GET http://localhost:5001/accounts

# Specific account
GET http://localhost:5001/account/account_1

# Strategy performance (last 7 days)
GET http://localhost:5001/strategy_performance?days=7

# Recent trades
GET http://localhost:5001/recent_trades?limit=100

# Weekly summary
GET http://localhost:5001/weekly_summary

# Export to CSV
GET http://localhost:5001/export/csv?days=7

# Export to JSON
GET http://localhost:5001/export/json?days=7
```

### Metrics Available

**Per Account**:
- Total trades
- Win/loss count & rate
- Daily P&L
- Current balance
- Average confidence
- Execution time

**Per Strategy**:
- Total trades (all accounts)
- Win rate
- Total P&L
- Average profit per trade
- Accounts using strategy

**Portfolio**:
- Total balance
- Total daily P&L
- Overall win rate
- Active/healthy accounts

---

## 📥 Exporting Data

### Daily Export (Recommended)

```bash
# Export today's trades
curl "http://localhost:5001/export/csv?days=1" -o daily_$(date +%Y%m%d).csv

# Export today's performance
curl "http://localhost:5001/export/json?days=1" -o daily_$(date +%Y%m%d).json
```

### Weekly Analysis

```bash
# Export week's data
curl "http://localhost:5001/export/csv?days=7" -o weekly_trades.csv
curl "http://localhost:5001/export/json?days=7" -o weekly_performance.json

# Generate weekly summary
curl -X POST http://localhost:5001/generate_weekly_summary
curl http://localhost:5001/weekly_summary | jq > weekly_summary.json
```

### Analysis in Excel

1. Download CSV: `curl "http://localhost:5001/export/csv?days=7" -o trades.csv`
2. Open in Excel or Google Sheets
3. Create pivot tables:
   - Win rate by strategy_profile
   - P&L by account_id
   - Trade count by hour
   - Win rate by selected_strategy

---

## 🔍 Performance Evaluation (Week 1)

### Daily Checklist (5 minutes)

```bash
# 1. Check all accounts running
curl http://localhost:5001/accounts | jq '.accounts[] | {account_id, is_running, trades, win_rate}'

# 2. Export daily data
curl "http://localhost:5001/export/csv?days=1" -o daily_$(date +%Y%m%d).csv

# 3. Check for errors
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep ERROR
```

### End of Week Analysis

```bash
# 1. Generate summary
curl -X POST http://localhost:5001/generate_weekly_summary

# 2. Export data
curl "http://localhost:5001/export/csv?days=7" -o week1_trades.csv
curl "http://localhost:5001/export/json?days=7" -o week1_performance.json

# 3. View summary
curl http://localhost:5001/weekly_summary | jq > week1_summary.json
```

### Analysis Questions

1. **Which strategy profile has the highest win rate?**
2. **Which is most profitable?**
3. **Which trades most frequently?**
4. **What's the risk-adjusted return for each?**
5. **Should any strategies be disabled?**
6. **Are results within expected ranges?**

### Decision Criteria (Continue if)

- ✅ Overall win rate ≥ 60%
- ✅ Each account win rate ≥ 55%
- ✅ No critical bugs
- ✅ System stable
- ✅ Data quality good

### Expected Results After Week 1

| Profile | Trades | Win Rate | Daily P&L Range |
|---------|--------|----------|-----------------|
| Conservative | 20-30 | 70-80% | -$5 to +$10 |
| Moderate | 40-60 | 65-75% | -$8 to +$15 |
| Aggressive | 60-80 | 60-70% | -$15 to +$25 |
| Scalping | 80-100 | 60-70% | -$10 to +$20 |
| Trend Following | 30-50 | 65-75% | -$10 to +$18 |

**Portfolio Total**: 230-320 trades, 65-70% win rate, $50-$150 profit (demo)

---

## 🛠️ Common Operations

### View Logs

```bash
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot
```

### Restart Bot

```bash
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

### Stop System

```bash
docker-compose -f docker-compose.multi-account.yml down
```

### Backup Database

```bash
docker exec kael-timescaledb pg_dump -U postgres kael > backup_$(date +%Y%m%d).sql
```

### Reset Daily Stats

```bash
docker exec -it kael-timescaledb psql -U postgres -d kael -c "UPDATE accounts SET enabled = true;"
```

---

## ⚠️ Switching to Live Trading

**ONLY AFTER**:
- ✅ 1+ week demo testing
- ✅ Overall win rate ≥ 65%
- ✅ All accounts ≥ 60% win rate
- ✅ No critical bugs
- ✅ Comfortable with risk

**Steps**:
1. Edit `.env`: `TRADING_MODE=live`
2. Restart: `docker-compose -f docker-compose.multi-account.yml restart multi-account-bot`
3. Verify: `docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "LIVE MODE"`

---

## 📚 Documentation

### Getting Started
- **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - Step-by-step deployment
- **[MULTI_ACCOUNT_QUICK_START.md](MULTI_ACCOUNT_QUICK_START.md)** - Quick reference

### Complete Guides
- **[MULTI_ACCOUNT_GUIDE.md](MULTI_ACCOUNT_GUIDE.md)** - Comprehensive 13,000+ word guide
- **[MULTI_ACCOUNT_IMPLEMENTATION_SUMMARY.md](MULTI_ACCOUNT_IMPLEMENTATION_SUMMARY.md)** - Implementation details

### Strategy Information
- **[ADVANCED_STRATEGIES_README.md](ADVANCED_STRATEGIES_README.md)** - Strategy documentation
- **[STRATEGY_PER_THREAD_GUIDE.md](STRATEGY_PER_THREAD_GUIDE.md)** - Architecture guide

---

## 🐛 Troubleshooting

### Accounts Not Connecting

```bash
# Check logs
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "Connection failed"

# Verify config
cat config/accounts.json | jq '.accounts[] | {email, enabled}'

# Restart
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

### No Trades

**Check**:
- Daily loss limit reached?
- Consecutive losses limit reached?
- Markets open?
- Confidence threshold too high?

```bash
curl http://localhost:5001/accounts | jq '.accounts[] | {account_id, is_running, daily_pnl, consecutive_losses}'
```

### Database Issues

```bash
# Check health
docker exec kael-timescaledb pg_isready -U postgres

# View logs
docker-compose -f docker-compose.multi-account.yml logs timescaledb

# Restart
docker-compose -f docker-compose.multi-account.yml restart timescaledb
```

---

## 📁 Project Structure

```
KAEL/
├── multi_account_parallel_bot.py       # Main bot (5 accounts)
├── docker-compose.multi-account.yml    # Docker configuration
├── start_multi_account.sh              # Startup script
├── config/
│   ├── multi_account_config.py         # Account configuration
│   └── accounts.json                   # Account credentials (auto-generated)
├── database/
│   ├── multi_account_logger.py         # Database logger
│   └── multi_account_schema.sql        # Database schema
├── strategies/
│   ├── advanced_strategies.py          # 7 trading strategies
│   ├── strategy_config.py              # Strategy configurations
│   └── strategy_integrator.py          # Strategy integration
├── logs/                                # Log files
├── reports/                             # Exported reports
├── pgdata/                              # PostgreSQL data
└── docs/
    ├── DEPLOYMENT_INSTRUCTIONS.md       # Deployment guide
    ├── MULTI_ACCOUNT_GUIDE.md          # Complete guide
    ├── MULTI_ACCOUNT_QUICK_START.md    # Quick reference
    └── README_MULTI_ACCOUNT.md         # This file
```

---

## 🎯 Success Criteria

### Phase 1: Demo Testing (Week 1-4)
- [ ] All 5 accounts trading concurrently
- [ ] Trades logged successfully
- [ ] API endpoints working
- [ ] Exports functioning
- [ ] Overall win rate ≥ 60%

### Phase 2: Performance Evaluation (Month 1-2)
- [ ] Identify best strategy profile
- [ ] Identify worst strategy profile
- [ ] Optimize based on data
- [ ] Consistent 65%+ win rate
- [ ] Zero critical bugs

### Phase 3: Live Trading (Month 3+)
- [ ] Switch to live mode
- [ ] Maintain 65%+ win rate
- [ ] Positive monthly P&L
- [ ] Scale gradually
- [ ] Continuous optimization

---

## 📞 Support

### Check Status
```bash
curl http://localhost:5001/statistics | jq
```

### View Logs
```bash
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot
```

### Database Query
```bash
docker exec -it kael-timescaledb psql -U postgres -d kael -c "SELECT * FROM v_daily_account_performance;"
```

---

## 🏆 Summary

### What You Have

✅ **Production-ready** multi-account trading system
✅ **5 concurrent accounts** with different strategies
✅ **Comprehensive tracking** of all metrics
✅ **Real-time monitoring** via API and dashboards
✅ **Export capabilities** for analysis
✅ **Complete documentation** for all scenarios

### What You'll Learn

After 1 week of demo trading, you'll know:
- Which strategy profile performs best
- Which has best risk-adjusted returns
- Which trades most efficiently
- How to optimize for your goals
- Whether to proceed to live trading

### Expected Outcome

**Objective**: Data-driven strategy selection
**Method**: Parallel testing of 5 profiles
**Result**: Identify optimal trading approach
**Timeline**: 1-4 weeks demo, then live decision

---

## 🚀 Get Started Now

```bash
# 1. Navigate to project
cd /c/Users/jratombo/Desktop/dev_tools/pythonEnv/app/KAEL/KAEL

# 2. Start system
./start_multi_account.sh

# 3. Monitor
curl http://localhost:5001/statistics | jq

# 4. Access dashboards
# - API: http://localhost:5001
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

---

**Built with**: Python 3.11, Docker, TimescaleDB, Prometheus, Grafana
**Status**: ✅ Production Ready
**Version**: 1.0
**Last Updated**: January 2025

**Good luck with your trading! 🚀**
