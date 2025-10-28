# 🚀 Multi-Strategy Trading System - Quick Reference

## 📋 Quick Commands

### Setup & Installation
```bash
# One-time setup
./setup_multi_strategy.sh

# Manual setup
pip install -r requirements.txt psycopg2-binary
docker-compose up -d timescaledb
docker exec -i kael-timescaledb psql -U postgres -d kael < database/multi_account_schema.sql
```

### Running the System
```bash
# Standard mode
python multi_strategy_orchestrator.py

# Docker mode
docker-compose -f docker-compose.parallel.yml up -d

# View logs
tail -f logs/multi_strategy_$(date +%Y%m%d).log
docker-compose logs -f parallel-trading-bot
```

### Monitoring
```bash
# Real-time logs
tail -f logs/multi_strategy_*.log

# Filter by account
tail -f logs/multi_strategy_*.log | grep "account_1"

# Filter by strategy
tail -f logs/multi_strategy_*.log | grep "conservative"

# System status
python -c "from config.multi_account_config import get_account_manager; print(get_account_manager().get_summary())"
```

---

## 📊 Database Queries

```sql
-- Daily performance
SELECT * FROM v_daily_account_performance;

-- Strategy comparison
SELECT * FROM v_strategy_performance_summary;

-- Recent trades
SELECT * FROM v_recent_trades LIMIT 50;

-- Weekly summary
SELECT * FROM weekly_performance ORDER BY week_start DESC LIMIT 4;

-- System events
SELECT * FROM system_events ORDER BY event_time DESC LIMIT 20;
```

---

## 🎯 Account Configuration

| Account | Email | Strategy | Confidence | Max Trade | Max Loss |
|---------|-------|----------|------------|-----------|----------|
| 1 | tombonirinakaej@gmail.com | Conservative | 85% | $1.50 | $5.00 |
| 2 | tombokael4@gmail.com | Moderate | 78% | $2.00 | $8.00 |
| 3 | ruslantombofitiavana@gmail.com | Aggressive | 70% | $3.00 | $15.00 |
| 4 | tombofifalianakimi@gmail.com | Scalping | 75% | $2.50 | $10.00 |
| 5 | dinokamisy@gmail.com | Trend Following | 80% | $2.50 | $10.00 |

---

## 📈 Performance Analysis

```python
from database.multi_account_logger import MultiAccountTradeLogger
import os

logger = MultiAccountTradeLogger(os.getenv('DATABASE_URL'))

# Portfolio summary
summary = logger.get_portfolio_summary()
print(f"Trades: {summary['overall']['total_trades']}")
print(f"Win Rate: {summary['overall']['overall_win_rate']}%")
print(f"P&L: ${summary['overall']['total_pnl']:.2f}")

# Strategy performance
strategies = logger.get_strategy_performance(days=7)
for s in strategies:
    print(f"{s['selected_strategy']}: {s['win_rate']}% | ${s['total_pnl']:.2f}")

# Export reports
logger.export_trades_to_csv('reports/trades.csv', days=7)
logger.export_performance_to_json('reports/performance.json', days=7)
logger.generate_weekly_summary()
```

---

## 🔧 Configuration Files

### `.env`
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kael
TRADING_MODE=demo
USE_ADVANCED_STRATEGIES=true
STRATEGY_RISK_PROFILE=moderate
LOG_LEVEL=INFO
```

### `config/accounts.json`
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

---

## 🛠️ Troubleshooting

### Database Issues
```bash
# Check database
docker ps | grep timescaledb
psql -U postgres -h localhost -d kael -c "SELECT 1"

# Restart database
docker-compose restart timescaledb

# Reinitialize schema
docker exec -i kael-timescaledb psql -U postgres -d kael < database/multi_account_schema.sql
```

### Connection Issues
```bash
# Test account connection
python -c "
from config.multi_account_config import get_account_manager
manager = get_account_manager()
for acc in manager.get_all_accounts():
    print(f'{acc.account_id}: Enabled={acc.enabled}, Healthy={acc.is_healthy}')
"

# Reset account health
python -c "
from config.multi_account_config import get_account_manager
manager = get_account_manager()
manager.enable_account('account_1')
"
```

### Strategy Issues
```bash
# Check TA-Lib
pip list | grep TA-Lib

# Test strategy
python -c "
from strategies.strategy_integrator import create_integrator
integrator = create_integrator('moderate')
print('Strategy integrator initialized successfully')
"
```

---

## 📊 Key Metrics

### Target Performance
- **Win Rate**: 65-70% overall
- **Profit Factor**: > 1.5
- **Sharpe Ratio**: > 1.0
- **Max Drawdown**: < 20%

### Strategy-Specific Targets
- **Conservative**: 70-75% win rate
- **Moderate**: 65-70% win rate
- **Aggressive**: 60-65% win rate
- **Scalping**: 65-70% win rate
- **Trend Following**: 65-75% win rate

---

## 🎯 Daily Checklist

### Morning
- [ ] Check system is running
- [ ] Review overnight performance
- [ ] Check account health
- [ ] Verify database connectivity

### During Trading
- [ ] Monitor logs for errors
- [ ] Check trade execution
- [ ] Verify strategy signals
- [ ] Monitor P&L

### Evening
- [ ] Review daily performance
- [ ] Export daily reports
- [ ] Check for system events
- [ ] Backup database

---

## 🚨 Emergency Commands

```bash
# Stop all trading immediately
docker-compose down

# Or kill process
pkill -f multi_strategy_orchestrator

# Disable all accounts
python -c "
from config.multi_account_config import get_account_manager
manager = get_account_manager()
for acc in manager.get_all_accounts():
    manager.disable_account(acc.account_id)
"

# Check last trades
psql -U postgres -d kael -c "SELECT * FROM v_recent_trades LIMIT 10;"
```

---

## 📱 Access Points

- **Logs**: `logs/multi_strategy_*.log`
- **Database**: `postgresql://localhost:5432/kael`
- **Grafana**: `http://localhost:3000` (admin/admin)
- **Prometheus**: `http://localhost:9090`
- **Health API**: `http://localhost:5001/health`

---

## 📚 Documentation

- **Setup Guide**: `MULTI_STRATEGY_SETUP_GUIDE.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Advanced Strategies**: `ADVANCED_STRATEGIES_README.md`
- **Database Schema**: `database/multi_account_schema.sql`

---

## ⚡ Pro Tips

1. **Always start with demo mode**
2. **Monitor first 24 hours closely**
3. **Export reports daily**
4. **Backup database weekly**
5. **Review strategy performance weekly**
6. **Adjust parameters based on data**
7. **Keep logs for at least 30 days**
8. **Test changes in demo first**

---

## 🎓 Learning Resources

### Week 1: Validation
- Run in demo mode
- Monitor all 5 accounts
- Verify data logging
- Check for errors

### Week 2-4: Optimization
- Analyze performance data
- Identify best strategy
- Adjust parameters
- Optimize thresholds

### Month 2+: Production
- Consider live trading
- Scale successful strategies
- Maintain discipline
- Regular reviews

---

**Quick Start**: `./setup_multi_strategy.sh && python multi_strategy_orchestrator.py`

**Emergency Stop**: `docker-compose down` or `Ctrl+C`

**Get Help**: Check `MULTI_STRATEGY_SETUP_GUIDE.md`
