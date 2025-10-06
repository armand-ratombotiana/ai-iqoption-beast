# 🗄️ PostgreSQL/TimescaleDB Database Upgrade Guide

## Overview

This guide documents the complete upgrade from SQLite to PostgreSQL/TimescaleDB for AI-optimized trading data storage and ML model training.

## Why PostgreSQL/TimescaleDB?

### Previous: SQLite
- ❌ Single-threaded, limited concurrent access
- ❌ No built-in time-series optimization
- ❌ Limited analytics capabilities
- ❌ Not production-ready for high-frequency trading
- ❌ No advanced indexing for ML queries

### New: PostgreSQL + TimescaleDB
- ✅ Multi-threaded, handles concurrent reads/writes
- ✅ Hypertables optimized for time-series data (10-100x faster queries)
- ✅ Advanced materialized views for real-time analytics
- ✅ Production-grade reliability and performance
- ✅ JSONB support for flexible feature storage
- ✅ Built-in aggregation functions for ML training
- ✅ Automatic data retention policies
- ✅ Connection pooling for high throughput

---

## 📊 Database Architecture

### Core Tables

#### 1. **trades** (TimescaleDB Hypertable)
**Purpose**: Store all trading data with 50+ technical indicators for ML training

**Key Features**:
- Partitioned by time (1-day chunks) for fast queries
- 50+ technical indicator fields (RSI, MACD, BB, EMA, SMA, Stochastic, ADX, CCI, ATR, etc.)
- Market regime tracking (Bull, Bear, Sideways, High/Low Volatility)
- Pre-trade and post-trade analysis fields
- Time context (hour, day, week, month, market session)
- Pattern recognition fields (candlestick, chart, harmonic patterns)

**Example**:
```sql
SELECT * FROM trades
WHERE pair = 'EURUSD'
AND timestamp > NOW() - INTERVAL '7 days'
AND result = 'WIN'
ORDER BY timestamp DESC;
```

#### 2. **ai_predictions** (TimescaleDB Hypertable)
**Purpose**: Store every prediction from every AI model

**Key Features**:
- Links to specific models via `model_id`
- Stores confidence, reasoning, and feature importance
- Tracks prediction correctness (`was_correct`)
- Monitors cost and performance metrics

**Example**:
```sql
-- Get model accuracy over last 7 days
SELECT
    m.model_name,
    COUNT(*) as predictions,
    AVG(CASE WHEN was_correct THEN 100.0 ELSE 0.0 END) as accuracy
FROM ai_predictions p
JOIN ai_models m ON p.model_id = m.model_id
WHERE p.timestamp > NOW() - INTERVAL '7 days'
GROUP BY m.model_name
ORDER BY accuracy DESC;
```

#### 3. **ai_models**
**Purpose**: Registry of all AI models with metadata

**Example**:
```sql
INSERT INTO ai_models (model_name, model_type, provider, cost_per_request)
VALUES ('claude-3.5-haiku', 'LLM', 'Anthropic', 0.0001);
```

#### 4. **candles** (TimescaleDB Hypertable)
**Purpose**: Store OHLCV candle data for pattern analysis

**Key Features**:
- Multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Continuous aggregates for automatic rollups
- Candle characteristics (body size, wicks, direction)

#### 5. **ml_features**
**Purpose**: Pre-computed feature vectors for ML training

**Key Features**:
- JSONB feature vectors (100+ features)
- Multi-horizon labels (5min, 15min, 1h)
- Actual outcomes for supervised learning
- Training/testing split flag

**Example**:
```sql
-- Get training data for ML model
SELECT
    feature_vector,
    label_5min,
    actual_5min
FROM ml_features
WHERE is_training_data = TRUE
AND actual_5min IS NOT NULL
LIMIT 10000;
```

### Materialized Views

#### **mv_model_performance_realtime**
Real-time model performance dashboard
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_model_performance_realtime;
SELECT * FROM mv_model_performance_realtime;
```

#### **mv_winning_patterns**
Automatically discovered winning trading patterns
```sql
SELECT * FROM mv_winning_patterns
WHERE win_rate > 60
ORDER BY avg_profit DESC;
```

---

## 🚀 Installation & Setup

### 1. Install PostgreSQL and TimescaleDB

#### Ubuntu/Debian:
```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install PostgreSQL
sudo apt-get update
sudo apt-get install -y postgresql-15 postgresql-contrib-15

# Add TimescaleDB repository
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -

# Install TimescaleDB
sudo apt-get update
sudo apt-get install -y timescaledb-2-postgresql-15

# Tune PostgreSQL for TimescaleDB
sudo timescaledb-tune --quiet --yes

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### macOS (Homebrew):
```bash
brew install postgresql@15
brew install timescaledb

# Initialize and start
brew services start postgresql@15
```

#### Docker (Easiest):
```bash
docker run -d --name timescaledb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=trading_db \
  -e POSTGRES_USER=trading_user \
  timescale/timescaledb:latest-pg15
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE trading_db;
CREATE USER trading_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE trading_db TO trading_user;

# Enable TimescaleDB extension
\c trading_db
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

\q
```

### 3. Set Environment Variables

Create `.env` file or export:
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=trading_db
export POSTGRES_USER=trading_user
export POSTGRES_PASSWORD=your_password
```

### 4. Initialize Database Schema

```bash
cd /app/app/KAEL/KAEL/advanced_trading_system/database

# Run schema initialization
python migration_tools.py --init-only --schema advanced_db_schema.sql
```

**Output**:
```
================================================================================
INITIALIZING POSTGRESQL DATABASE
================================================================================
Executing 150+ SQL statements...

✓ Database schema initialized successfully
```

---

## 📦 Migration from SQLite

### Full Migration

```bash
cd /app/app/KAEL/KAEL/advanced_trading_system/database

# Migrate all data from SQLite to PostgreSQL
python migration_tools.py --sqlite ../../data/trading.db
```

**Output**:
```
================================================================================
DATABASE MIGRATION: SQLite → PostgreSQL/TimescaleDB
================================================================================

[1/3] Migrating AI models...
  ✓ Created 8 default AI models

[2/3] Migrating trades...
  Found 523 trades to migrate...
  Progress: 523/523 trades
  ✓ Migrated 523 trades

[3/3] Migrating AI predictions...
  ⚠ ai_predictions table not found in SQLite, skipping...

================================================================================
MIGRATION COMPLETE
================================================================================
✓ Trades migrated: 523
✓ AI predictions migrated: 0
```

### Custom Migration

```python
from database.postgres_connector import create_connector
from database.migration_tools import DatabaseMigrator

# Create connector
pg = create_connector()

# Initialize migrator
migrator = DatabaseMigrator(
    sqlite_path='../../data/trading.db',
    postgres_connector=pg
)

# Run migration
migrator.migrate_all()

pg.close()
```

---

## 💾 Using PostgreSQL in Your Code

### Basic Connection

```python
from database.postgres_connector import create_connector

# Create connector (uses environment variables)
pg = create_connector()

# Execute query
results = pg.execute_query("SELECT * FROM trades LIMIT 10;")

for row in results:
    print(f"Trade: {row['pair']} at {row['timestamp']}")

# Close when done
pg.close()
```

### Insert Trade

```python
from datetime import datetime

trade_data = {
    'timestamp': datetime.now(),
    'pair': 'EURUSD',
    'direction': 'CALL',
    'amount': 10.0,
    'duration': 60,
    'result': 'PENDING',
    'entry_price': 1.0850,
    'ai_signal_confidence': 75,
    'ai_model_agreement': 0.8,
    'ai_models_count': 5,
    'rsi_14': 65.5,
    'macd_value': 0.0012,
    'bb_upper': 1.0870,
    'bb_middle': 1.0850,
    'bb_lower': 1.0830,
    'trend': 'BULLISH',
    'volatility': 'MEDIUM',
    'market_regime': 'BULL',
    'regime_confidence': 80.0,
    'hour_of_day': datetime.now().hour,
    'day_of_week': datetime.now().weekday(),
    'market_session': 'LONDON',
    'strategy_version': 'v2.0',
    'model_version': 'v2.0',
    'notes': 'High confidence trade'
}

trade_id = pg.insert_trade(trade_data)
print(f"Trade inserted with ID: {trade_id}")
```

### Update Trade Result

```python
# After trade closes
pg.update_trade_result(
    trade_id=123,
    result='WIN',
    profit=8.50,
    exit_price=1.0865
)
```

### Insert AI Prediction

```python
prediction_data = {
    'timestamp': datetime.now(),
    'trade_id': 123,
    'model_id': 1,  # Get from ai_models table
    'signal': 'CALL',
    'confidence': 75.5,
    'reasoning': 'Strong bullish momentum with RSI confirmation',
    'feature_importance': {
        'rsi_14': 0.35,
        'macd_histogram': 0.25,
        'trend_alignment': 0.20
    },
    'inference_time_ms': 250,
    'tokens_used': 500,
    'cost': 0.0001
}

prediction_id = pg.insert_ai_prediction(prediction_data)
```

---

## 🧪 Feature Engineering for ML

### Extract Features

```python
from database.feature_engineering import create_feature_engineer

# Create feature engineer
fe = create_feature_engineer(pg)

# Extract features from market data
market_data = {
    'price': 1.0850,
    'rsi_14': 65.5,
    'macd_value': 0.0012,
    'bb_upper': 1.0870,
    'bb_middle': 1.0850,
    'bb_lower': 1.0830,
    'trend': 'BULLISH',
    'volatility': 'MEDIUM',
    'market_regime': 'BULL'
}

features = fe.extract_features(market_data)
# Returns 100+ features including derived metrics

# Store features
feature_id = fe.store_features(
    pair='EURUSD',
    timestamp=datetime.now(),
    features=features,
    labels={'label_5min': 'CALL'},
    is_training_data=True
)
```

### Backfill Features for Existing Trades

```python
# Automatically extract features for all existing trades
fe.backfill_features(limit=1000)
```

**Output**:
```
Backfilling features for up to 1000 trades...
Found 523 trades to backfill
  Progress: 100/523
  Progress: 200/523
  ...
✓ Backfilled 523 feature records
```

---

## 📤 Export Training Data

### Export to NumPy Arrays

```python
from database.ml_data_exporter import MLDataExporter

exporter = MLDataExporter(pg)

# Export as NumPy arrays
X, y = exporter.export_to_numpy(
    pair='EURUSD',
    limit=10000,
    timeframe='5min',
    output_dir='./ml_data'
)

print(f"X shape: {X.shape}")  # (10000, 100)
print(f"y shape: {y.shape}")  # (10000,)
```

### Export to CSV

```python
exporter.export_to_csv(
    pair='EURUSD',
    limit=10000,
    timeframe='5min',
    output_file='./ml_data/training_data.csv'
)
```

### Export to TensorFlow Dataset

```python
train_dataset, val_dataset = exporter.export_to_tensorflow_dataset(
    pair='EURUSD',
    limit=10000,
    timeframe='5min',
    batch_size=32,
    validation_split=0.2
)

# Use in TensorFlow training
# model.fit(train_dataset, validation_data=val_dataset, epochs=10)
```

### Export to PyTorch Dataset

```python
dataset = exporter.export_to_pytorch_dataset(
    pair='EURUSD',
    limit=10000,
    timeframe='5min',
    output_dir='./ml_data'
)

# Use in PyTorch training
# from torch.utils.data import DataLoader
# loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Create Train/Val/Test Splits

```python
exporter.create_training_splits(
    pair='EURUSD',
    timeframe='5min',
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    output_dir='./ml_data'
)
```

**Output**:
```
Creating train/val/test splits...

✓ Created splits in ./ml_data:
  Train: 7000 samples (70.0%)
  Val: 1500 samples (15.0%)
  Test: 1500 samples (15.0%)
```

---

## 📊 Analytics and Insights

### Get Model Performance

```python
# Get performance for specific model
perf = pg.get_model_performance(model_id=1, days=7)

print(f"Accuracy: {perf['accuracy']}%")
print(f"Total predictions: {perf['total_predictions']}")
print(f"Avg confidence: {perf['avg_confidence']}%")
```

### Find Winning Patterns

```python
patterns = pg.get_winning_patterns(
    min_occurrences=5,
    min_win_rate=60.0
)

for pattern in patterns:
    print(f"Pattern: {pattern['trend']} + {pattern['market_regime']} @ hour {pattern['hour_of_day']}")
    print(f"  Win rate: {pattern['win_rate']}%")
    print(f"  Avg profit: ${pattern['avg_profit']}")
```

### Get Dataset Statistics

```python
stats = exporter.export_statistics(pair='EURUSD', timeframe='5min')
```

**Output**:
```
============================================================
DATASET STATISTICS
============================================================
Total samples: 10523
Labeled samples: 8945
  CALL: 4623 (51.7%)
  PUT: 4322 (48.3%)
Class balance: 0.93
Number of features: 102
============================================================
```

---

## 🔧 Advanced Queries

### Time-Series Aggregation

```sql
-- Hourly win rate
SELECT
    time_bucket('1 hour', timestamp) AS hour,
    COUNT(*) as trades,
    AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END) as win_rate,
    SUM(profit) as total_profit
FROM trades
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY hour
ORDER BY hour DESC;
```

### Model Comparison

```sql
-- Compare model performance by market regime
SELECT
    m.model_name,
    t.market_regime,
    COUNT(*) as predictions,
    AVG(CASE WHEN t.prediction_correct THEN 100.0 ELSE 0.0 END) as accuracy
FROM trades t
JOIN ai_predictions p ON t.trade_id = p.trade_id
JOIN ai_models m ON p.model_id = m.model_id
WHERE t.timestamp > NOW() - INTERVAL '30 days'
GROUP BY m.model_name, t.market_regime
ORDER BY m.model_name, accuracy DESC;
```

### Feature Importance Analysis

```sql
-- Aggregate feature importance across all models
SELECT
    jsonb_object_keys(feature_importance) as feature,
    AVG((feature_importance->>jsonb_object_keys(feature_importance))::float) as avg_importance
FROM ai_predictions
WHERE feature_importance IS NOT NULL
AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY feature
ORDER BY avg_importance DESC
LIMIT 20;
```

---

## 🎯 Performance Optimization

### Refresh Materialized Views

```python
# Refresh for latest data
pg.refresh_materialized_views()
```

**Run this**:
- After large data imports
- Before generating reports
- Periodically (e.g., hourly cron job)

### Indexes

All critical indexes are created automatically:
- Time-based queries (hypertable chunks)
- Pair + timestamp lookups
- Result filtering
- Pattern searches
- ML training queries

### Query Optimization

Use `EXPLAIN ANALYZE` to optimize slow queries:
```sql
EXPLAIN ANALYZE
SELECT * FROM trades
WHERE pair = 'EURUSD'
AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;
```

---

## 🗄️ Data Retention

Automatic retention policies are configured:

- **candles**: 90 days (raw), aggregated data kept longer
- **ai_predictions**: 180 days
- **trades**: Kept indefinitely (manually archive old data)

To manually add retention:
```sql
SELECT add_retention_policy('trades', INTERVAL '2 years');
```

---

## 📈 CLI Tools

### Migration Tool

```bash
cd /app/app/KAEL/KAEL/advanced_trading_system/database

# Full migration
python migration_tools.py --sqlite ../../data/trading.db

# Schema initialization only
python migration_tools.py --init-only
```

### Data Export Tool

```bash
# Export to NumPy
python ml_data_exporter.py --format numpy --pair EURUSD --timeframe 5min

# Export to CSV
python ml_data_exporter.py --format csv --limit 20000

# Export all formats
python ml_data_exporter.py --format all --timeframe 15min
```

---

## 🔐 Security Best Practices

### 1. Use Strong Passwords
```bash
# Generate strong password
openssl rand -base64 32
```

### 2. Restrict Network Access
```bash
# PostgreSQL config: /etc/postgresql/15/main/pg_hba.conf
# Only allow local connections
host    trading_db    trading_user    127.0.0.1/32    md5
```

### 3. Use SSL/TLS
```python
pg = create_connector({
    'host': 'db.example.com',
    'sslmode': 'require',
    'sslrootcert': '/path/to/ca.crt'
})
```

### 4. Environment Variables
Never hardcode credentials. Always use `.env`:
```bash
# .env (add to .gitignore)
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=super_secret_password_123
```

---

## 🐛 Troubleshooting

### Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if stopped
sudo systemctl start postgresql
```

### Permission Denied
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading_user;
```

### Slow Queries
```sql
-- Check slow queries
SELECT * FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### TimescaleDB Not Installed
```sql
-- Verify extension
SELECT * FROM pg_extension WHERE extname = 'timescaledb';

-- If not installed
CREATE EXTENSION timescaledb CASCADE;
```

---

## 📚 Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

## 🎉 Next Steps

1. ✅ Install PostgreSQL + TimescaleDB
2. ✅ Initialize database schema
3. ✅ Migrate existing SQLite data
4. ✅ Update trading system to use PostgreSQL
5. ✅ Start collecting features for ML training
6. ✅ Export training data and train models
7. 🚀 Deploy to production!

---

**Database upgrade complete! You now have an enterprise-grade, AI-optimized trading database.** 🎯
