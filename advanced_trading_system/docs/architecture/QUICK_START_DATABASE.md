# 🚀 Quick Start: Database Upgrade

## 5-Minute Setup Guide

### Option 1: Docker (Easiest - Recommended)

```bash
# 1. Start TimescaleDB with Docker
docker run -d --name trading-db \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=trading123 \
  -e POSTGRES_DB=trading_db \
  -e POSTGRES_USER=trading_user \
  timescale/timescaledb:latest-pg15

# 2. Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=trading_db
export POSTGRES_USER=trading_user
export POSTGRES_PASSWORD=trading123

# 3. Initialize database schema
cd /app/app/KAEL/KAEL/advanced_trading_system/database
python migration_tools.py --init-only

# 4. Migrate existing SQLite data (optional)
python migration_tools.py --sqlite ../../data/trading.db

# Done! ✅
```

### Option 2: Local Installation (Ubuntu/Debian)

```bash
# 1. Install PostgreSQL + TimescaleDB
sudo apt-get update
sudo apt-get install -y postgresql-15 postgresql-contrib-15

# Add TimescaleDB
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y timescaledb-2-postgresql-15

# Tune and restart
sudo timescaledb-tune --quiet --yes
sudo systemctl restart postgresql

# 2. Create database
sudo -u postgres psql -c "CREATE DATABASE trading_db;"
sudo -u postgres psql -c "CREATE USER trading_user WITH ENCRYPTED PASSWORD 'trading123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE trading_db TO trading_user;"

# 3. Enable TimescaleDB extension
sudo -u postgres psql -d trading_db -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"

# 4. Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=trading_db
export POSTGRES_USER=trading_user
export POSTGRES_PASSWORD=trading123

# 5. Initialize schema
cd /app/app/KAEL/KAEL/advanced_trading_system/database
python migration_tools.py --init-only

# Done! ✅
```

---

## 📝 Test Connection

```python
from database.postgres_connector import create_connector

# Test connection
pg = create_connector()

# Insert test trade
from datetime import datetime

test_trade = {
    'timestamp': datetime.now(),
    'pair': 'EURUSD',
    'direction': 'CALL',
    'amount': 10.0,
    'duration': 60,
    'entry_price': 1.0850,
    'ai_signal_confidence': 75,
    'rsi_14': 65.0,
    'trend': 'BULLISH',
    'hour_of_day': datetime.now().hour,
    'day_of_week': datetime.now().weekday()
}

trade_id = pg.insert_trade(test_trade)
print(f"✅ Test trade inserted! ID: {trade_id}")

# Query it back
trades = pg.get_recent_trades(limit=1)
print(f"✅ Retrieved {len(trades)} trades")

pg.close()
```

**Expected Output**:
```
✓ PostgreSQL connection pool initialized (localhost:5432)
✅ Test trade inserted! ID: 1
✅ Retrieved 1 trades
✓ PostgreSQL connection pool closed
```

---

## 🎯 Common Tasks

### Export Training Data

```bash
cd database

# Export to NumPy (most common)
python ml_data_exporter.py --format numpy --timeframe 5min

# Export to CSV
python ml_data_exporter.py --format csv

# Export all formats
python ml_data_exporter.py --format all
```

### View Analytics

```python
from database.postgres_connector import create_connector
from database.analytics_engine import TradingAnalytics
from database.visualization import PerformanceVisualizer

pg = create_connector()
analytics = TradingAnalytics(pg)
viz = PerformanceVisualizer()

# Get stats
stats = analytics.get_trading_statistics(days=30)

# Create dashboard
dashboard = viz.create_performance_dashboard(stats)
print(dashboard)

pg.close()
```

### Backfill Features for ML

```python
from database.postgres_connector import create_connector
from database.feature_engineering import create_feature_engineer

pg = create_connector()
fe = create_feature_engineer(pg)

# Backfill features for existing trades
fe.backfill_features(limit=1000)

pg.close()
```

---

## 🐛 Troubleshooting

### "Connection refused"
```bash
# Check if PostgreSQL is running
docker ps  # (if using Docker)
# or
sudo systemctl status postgresql
```

### "Extension timescaledb does not exist"
```sql
-- Connect to database
psql -U trading_user -d trading_db

-- Enable extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

\q
```

### "Permission denied"
```sql
-- Grant all permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading_user;
```

---

## 📚 Next Steps

1. ✅ Database is set up
2. ✅ Test connection works
3. 🔄 Run trading system: `python scripts/run_enhanced_trading.py`
4. 📊 Collect data and train ML models
5. 🚀 Deploy to production

---

## 🔗 Full Documentation

- [DATABASE_UPGRADE_GUIDE.md](./database/DATABASE_UPGRADE_GUIDE.md) - Complete database documentation
- [DATABASE_AND_AI_COMPLETE_UPGRADE.md](./DATABASE_AND_AI_COMPLETE_UPGRADE.md) - Full upgrade summary

---

**Setup Time**: 5 minutes ⏱️
**Difficulty**: Easy 🟢
**Cost**: $0 (free PostgreSQL + TimescaleDB) 💰
