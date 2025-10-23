# 🗄️ KAEL Trading System - Database Setup

## Overview

The KAEL trading system uses **PostgreSQL + TimescaleDB** for production-grade time-series data storage with automatic aggregation, retention policies, and high-performance querying.

---

## 🚀 Quick Start (Docker - Recommended)

### Option 1: Using Docker Compose (Easiest)

```bash
# Start all services (PostgreSQL, Redis, Trading Bot)
docker-compose up -d

# View logs
docker-compose logs -f postgres

# Check if database is ready
docker-compose exec postgres pg_isready -U trading_user
```

That's it! The database is automatically initialized with the schema.

---

### Option 2: Standalone PostgreSQL Container

```bash
# Start PostgreSQL + TimescaleDB
docker run -d \
  --name kael-trading-db \
  -p 5432:5432 \
  -e POSTGRES_DB=trading_db \
  -e POSTGRES_USER=trading_user \
  -e POSTGRES_PASSWORD=trading123 \
  -v $(pwd)/database/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro \
  timescale/timescaledb:latest-pg15

# Wait for database to be ready
docker logs -f kael-trading-db
```

---

## 📋 Features

### Time-Series Optimization
- **Hypertables**: Automatic partitioning by time for fast queries
- **Continuous Aggregates**: Pre-calculated hourly/daily stats
- **Retention Policies**: Auto-delete old data (1 year for trades)
- **Compression**: Automatic data compression for old chunks

### Tables

#### 1. `trades` - Trade Execution Records
Stores all executed trades with full details:
- Trade details (asset, direction, amount, duration)
- Prices (entry, exit, payout rate)
- Result (win/loss/tie, profit/loss)
- AI signal data (confidence, consensus)
- Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Market context (trend, volatility, support/resistance)
- Risk management (balance, position size, Kelly fraction)
- Time context (hour, day, weekend flag)

**Hypertable**: ✅ (partitioned by day)
**Retention**: 1 year

#### 2. `candles` - OHLCV Data
Historical price candles for multiple timeframes:
- OHLC prices
- Volume
- Pre-calculated technical indicators
- Supports 1m, 5m, 15m, 1h, 4h, 1d timeframes

**Hypertable**: ✅ (partitioned by 7 days)
**Retention**: 90 days

#### 3. `ai_predictions` - AI Model Predictions
Individual AI model predictions for analysis:
- Model name and version
- Prediction and confidence
- Reasoning/explanation
- Correctness tracking
- Execution time

**Hypertable**: ❌
**Retention**: Manual

#### 4. `performance_metrics` - Aggregated Metrics
Pre-calculated performance metrics:
- Trading stats (win rate, total trades)
- Financial stats (profit, loss, ROI)
- AI stats (average confidence, consensus)
- Risk metrics (max drawdown, Sharpe ratio)

**Hypertable**: ✅ (partitioned by 30 days)

### Continuous Aggregates

#### `trades_hourly`
Hourly trading statistics per asset:
- Trade count
- Wins/losses
- Average confidence
- Total P/L
- Average trade size

**Refresh**: Every hour

#### `trades_daily`
Daily trading statistics:
- Win rate
- Total P/L
- Best/worst trades
- Average confidence

**Refresh**: Every day

---

## 🔧 Configuration

### Environment Variables

```bash
# Database Connection
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_db
DB_USERNAME=trading_user
DB_PASSWORD=trading123

# Connection Pool
DB_POOL_MIN=1
DB_POOL_MAX=10
```

### Update .env File

```bash
# Copy template
cp .env.production.example .env

# Edit and add database credentials
nano .env
```

---

## 💻 Python Usage

### Basic Usage

```python
from database.postgres_connector import create_connector
from datetime import datetime

# Create connector
pg = create_connector()

# Test connection
if pg.test_connection():
    print("✅ Connected!")

# Insert a trade
trade_data = {
    'trade_id': 'TRADE_12345',
    'timestamp': datetime.now(),
    'asset': 'EURUSD',
    'direction': 'CALL',
    'amount': 10.0,
    'duration': 60,
    'entry_price': 1.0850,
    'payout_rate': 0.82,
    'result': 'pending',
    'ai_signal_confidence': 75,
    'rsi_14': 65.0,
    'trend': 'BULLISH',
    'hour_of_day': datetime.now().hour,
    'day_of_week': datetime.now().weekday(),
    'account_balance_before': 1000.0,
    'trading_mode': 'demo'
}

trade_id = pg.insert_trade(trade_data)
print(f"Trade ID: {trade_id}")

# Update trade result
pg.update_trade_result(
    trade_id='TRADE_12345',
    result='win',
    profit_loss=8.20,
    exit_price=1.0860,
    balance_after=1008.20
)

# Get statistics
stats = pg.get_statistics(days=30, trading_mode='demo')
print(f"Win Rate: {stats['win_rate']:.2%}")
print(f"Total P/L: ${stats['total_pnl']:.2f}")

# Get recent trades
trades = pg.get_recent_trades(limit=10, asset='EURUSD')

# Get daily performance
daily = pg.get_daily_performance(days=7)

# Close connection
pg.close()
```

### Context Manager

```python
from database.postgres_connector import create_connector

with create_connector() as pg:
    stats = pg.get_statistics(days=7)
    print(stats)
```

---

## 📊 Queries

### Common Queries

```sql
-- Get today's trading summary
SELECT
    COUNT(*) as trades,
    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
    SUM(profit_loss) as pnl
FROM trades
WHERE DATE(timestamp) = CURRENT_DATE
  AND trading_mode = 'demo';

-- Get best performing hours
SELECT
    hour_of_day,
    COUNT(*) as trades,
    AVG(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as win_rate,
    SUM(profit_loss) as total_pnl
FROM trades
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY hour_of_day
ORDER BY win_rate DESC;

-- Get AI model performance
SELECT
    model_name,
    COUNT(*) as predictions,
    AVG(CASE WHEN was_correct THEN 1 ELSE 0 END) as accuracy,
    AVG(confidence) as avg_confidence
FROM ai_predictions
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY model_name
ORDER BY accuracy DESC;

-- Get daily performance (using continuous aggregate)
SELECT * FROM trades_daily
WHERE bucket >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY bucket DESC;
```

---

## 🧪 Testing

### Test Database Connection

```bash
# Using Python script
python3 database/postgres_connector.py

# Using psql
psql -h localhost -U trading_user -d trading_db -c "SELECT COUNT(*) FROM trades;"
```

### Create Test with pytest

```bash
# Run database tests
pytest tests/integration/test_database.py -v
```

---

## 🔍 Monitoring

### Check Database Size

```sql
SELECT
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'trading_db';
```

### Check Hypertable Info

```sql
SELECT * FROM timescaledb_information.hypertables;
```

### Check Continuous Aggregates

```sql
SELECT * FROM timescaledb_information.continuous_aggregates;
```

### Check Chunk Statistics

```sql
SELECT
    hypertable_name,
    chunk_name,
    range_start,
    range_end,
    is_compressed
FROM timescaledb_information.chunks
WHERE hypertable_name = 'trades'
ORDER BY range_start DESC
LIMIT 10;
```

---

## 🛠️ Maintenance

### Manual Refresh of Aggregates

```sql
-- Refresh hourly aggregate
CALL refresh_continuous_aggregate('trades_hourly', NULL, NULL);

-- Refresh daily aggregate
CALL refresh_continuous_aggregate('trades_daily', NULL, NULL);
```

### Compress Old Data

```sql
-- Enable compression on chunks older than 7 days
SELECT compress_chunk(i) FROM show_chunks('trades', older_than => INTERVAL '7 days') i;
```

### Backup Database

```bash
# Backup
docker exec kael-trading-db pg_dump -U trading_user trading_db > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i kael-trading-db psql -U trading_user trading_db < backup_20251023.sql
```

---

## 🐛 Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
docker ps | grep kael-trading-db

# Check logs
docker logs kael-trading-db

# Test connectivity
telnet localhost 5432
```

### Permission Denied

```sql
-- Grant all permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading_user;
```

### TimescaleDB Extension Missing

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
```

---

## 📚 Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

## 🔗 Related Files

- `init.sql` - Database schema
- `postgres_connector.py` - Python connector
- `../docker-compose.yml` - Docker setup
- `../.env` - Configuration

---

**Database Version**: PostgreSQL 15 + TimescaleDB 2.x
**Status**: Production Ready ✅
