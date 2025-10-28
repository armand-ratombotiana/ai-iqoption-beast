# 🚀 Multi-Account Trading Bot - Quick Start

## TL;DR - Get Running in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- 5 IQ Option accounts (provided credentials)

### 1. Quick Setup

```bash
cd /path/to/KAEL

# Create .env if not exists
cp .env.example .env

# Start everything
chmod +x start_multi_account.sh
./start_multi_account.sh
```

### 2. Verify It's Working

```bash
# Check health
curl http://localhost:5001/health

# View statistics
curl http://localhost:5001/statistics | jq
```

### 3. Access Dashboards

- **Health API**: http://localhost:5001/statistics
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

---

## Account Configuration

The system runs 5 accounts simultaneously:

| Account | Email | Strategy | Max Loss/Day | Max Trade |
|---------|-------|----------|--------------|-----------|
| 1 | tombonirinakaej@gmail.com | Conservative | $5 | $1.50 |
| 2 | tombokael4@gmail.com | Moderate | $8 | $2.00 |
| 3 | ruslantombofitiavana@gmail.com | Aggressive | $15 | $3.00 |
| 4 | tombofifalianakimi@gmail.com | Scalping | $10 | $2.50 |
| 5 | dinokamisy@gmail.com | Trend Following | $10 | $2.50 |

**All passwords**: `tombokael04`

---

## Essential Commands

```bash
# View logs
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot

# Stop system
docker-compose -f docker-compose.multi-account.yml down

# Restart bot
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot

# Export last 7 days to CSV
curl "http://localhost:5001/export/csv?days=7" -o trades.csv

# Export performance report
curl "http://localhost:5001/export/json?days=7" -o performance.json
```

---

## Monitoring Endpoints

### Get Overall Statistics
```bash
curl http://localhost:5001/statistics | jq
```

### Get All Accounts Status
```bash
curl http://localhost:5001/accounts | jq
```

### Get Specific Account
```bash
curl http://localhost:5001/account/account_1 | jq
```

### Get Strategy Performance (Last 7 Days)
```bash
curl "http://localhost:5001/strategy_performance?days=7" | jq
```

### Get Recent Trades
```bash
curl "http://localhost:5001/recent_trades?limit=20" | jq
```

---

## Expected Performance

| Strategy Profile | Expected Win Rate | Trade Frequency |
|-----------------|-------------------|-----------------|
| Conservative | 70-80% | Low |
| Moderate | 65-75% | Medium |
| Aggressive | 60-70% | High |
| Scalping | 60-70% | Very High |
| Trend Following | 65-75% | Medium |

**Overall Portfolio**: 65-70% win rate target

---

## File Locations

- **Logs**: `./logs/multi_account_YYYYMMDD.log`
- **Reports**: `./reports/`
- **Database**: `./pgdata/`
- **Configuration**: `./config/accounts.json`

---

## Switching to Live Trading

⚠️ **CRITICAL**: Only switch to live after testing in demo!

1. Update `.env`:
```bash
TRADING_MODE=live
```

2. Restart:
```bash
docker-compose -f docker-compose.multi-account.yml restart multi-account-bot
```

3. Verify mode:
```bash
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep "LIVE MODE"
```

---

## Troubleshooting

### Bot Not Trading?

```bash
# Check account status
curl http://localhost:5001/accounts | jq '.accounts[] | {account_id, is_running, daily_pnl, max_daily_loss}'

# Check for errors
docker-compose -f docker-compose.multi-account.yml logs multi-account-bot | grep ERROR
```

### Database Issues?

```bash
# Check database
docker exec kael-timescaledb pg_isready -U postgres

# View database logs
docker-compose -f docker-compose.multi-account.yml logs timescaledb
```

### Reset Daily Limits?

```bash
# Reset all accounts (new trading day)
docker exec -it kael-timescaledb psql -U postgres -d kael -c "UPDATE accounts SET enabled = true;"
```

---

## Weekly Performance Review

### 1. Generate Weekly Summary
```bash
curl -X POST http://localhost:5001/generate_weekly_summary
```

### 2. View Summary
```bash
curl http://localhost:5001/weekly_summary | jq
```

### 3. Export Data
```bash
# CSV export
curl "http://localhost:5001/export/csv?days=7" -o weekly_trades.csv

# JSON export
curl "http://localhost:5001/export/json?days=7" -o weekly_performance.json
```

### 4. Analyze in Excel/Google Sheets
- Open `weekly_trades.csv`
- Create pivot tables for:
  - Win rate by account
  - Win rate by strategy
  - P&L by account
  - P&L by strategy
  - Trade count by hour

---

## Performance Evaluation Checklist

After 1 week of trading:

- [ ] Export trades to CSV
- [ ] Calculate win rate per account
- [ ] Calculate win rate per strategy
- [ ] Identify best performing strategy profile
- [ ] Identify worst performing strategy profile
- [ ] Review daily P&L trends
- [ ] Check if any daily loss limits hit
- [ ] Analyze trade timing (best hours)
- [ ] Review execution times
- [ ] Compare expected vs actual win rates

**Decision Points**:
- Win rate < 60% on any account → Investigate or disable
- Win rate > 75% on any account → Consider increasing trade size
- Consistent losses in specific hours → Adjust trading schedule
- One strategy significantly outperforms → Allocate more capital

---

## Database Queries

### Account Performance
```sql
SELECT
    account_id,
    strategy_profile,
    COUNT(*) as trades,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(SUM(COALESCE(profit, 0)), 2) as total_pnl
FROM trades
WHERE entry_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY account_id, strategy_profile
ORDER BY win_rate DESC;
```

### Strategy Performance
```sql
SELECT
    selected_strategy,
    COUNT(*) as trades,
    ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(SUM(COALESCE(profit, 0)), 2) as total_pnl
FROM trades
WHERE entry_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY selected_strategy
ORDER BY total_pnl DESC;
```

### Run Query
```bash
docker exec -it kael-timescaledb psql -U postgres -d kael -c "YOUR_QUERY_HERE"
```

---

## Next Steps

1. ✅ Run in demo mode for 1 week
2. ✅ Export and analyze weekly performance
3. ✅ Identify best performing strategies
4. ✅ Adjust configurations based on results
5. ✅ Consider switching to live mode (if confident)

---

## Support

**Full Documentation**: See `MULTI_ACCOUNT_GUIDE.md`

**Check Status**: http://localhost:5001/statistics

**View Logs**:
```bash
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot
```

---

**Remember**: Start with demo mode, collect data for at least 1 week, analyze results, then decide on live trading!

Good luck! 🚀
