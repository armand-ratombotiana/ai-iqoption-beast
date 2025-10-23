# KAEL Trading System - Production Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: Minimum 512MB, Recommended 1GB
- **Disk Space**: 500MB minimum
- **Network**: Stable internet connection

### Required Accounts
- **IQOption Account**: Demo or Real account
- **API Keys** (Optional):
  - OpenAI API key (for GPT models)
  - Anthropic API key (for Claude models)
  - DeepSeek API key (for DeepSeek models)

---

## 📦 Installation

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd advanced_trading_system
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "from iqoptionapi.stable_api import IQ_Option; print('✅ IQOption API installed')"
python -c "import numpy; print('✅ NumPy installed')"
python -c "import anthropic; print('✅ Anthropic SDK installed')"
```

---

## ⚙️ Configuration

### Step 1: Create Environment File
```bash
cp .env.example .env
```

### Step 2: Edit Configuration
Open `.env` and configure:

```bash
# Required: IQOption Credentials
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
ACCOUNT_TYPE=demo  # Start with demo!

# AI Models (Free AI enabled by default)
USE_FREE_AI=true
FREE_AI_TYPE=rule-based

# Optional: Paid AI Models
USE_OPENAI=false
OPENAI_API_KEY=sk-your-key-here

USE_CLAUDE=false
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Trading Parameters
BASE_AMOUNT=2.0
MIN_CONFIDENCE=65
MAX_DAILY_LOSS=50.0

# Risk Management
MAX_CONSECUTIVE_LOSSES=3
MIN_ACCOUNT_BALANCE=50.0
```

### Step 3: Validate Configuration
```bash
python -c "from config.settings import TradingConfig; TradingConfig.validate(); print('✅ Configuration valid')"
```

---

## 🧪 Testing

### Quick Test
```bash
# Test data ingestion
python tests/test_data_ingestion.py

# Test all components
python tests/integration/test_all_components_real.py
```

### Comprehensive Test Suite
```bash
# Run all tests
python run_comprehensive_tests.py
```

### Expected Output
```
╔══════════════════════════════════════════════════════════════════════════════╗
║              KAEL TRADING SYSTEM - COMPREHENSIVE TEST SUITE                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

✅ Environment credentials found

================================================================================
Running: Data Ingestion Layer Tests
================================================================================

TEST 1: Connection Manager
✅ Connection successful
✅ Connection verification passed
✅ Disconnected successfully

...

TEST SUITE SUMMARY
Total Tests: 2
Passed: 2
Failed: 0
Success Rate: 100.0%
```

---

## 🚀 Deployment

### Option 1: Local Deployment

#### Run Demo Trading
```bash
python trade.py --mode demo --trades 5
```

#### Run Continuous Trading
```bash
python trade.py --mode demo
```

### Option 2: Docker Deployment

#### Build Docker Image
```bash
docker build -t kael-trading:latest .
```

#### Run with Docker Compose
```bash
# Edit docker-compose.yml with your credentials
docker-compose up -d
```

#### View Logs
```bash
docker-compose logs -f
```

#### Stop Container
```bash
docker-compose down
```

### Option 3: Production Deployment

#### Prerequisites
- Set `ACCOUNT_TYPE=real` in `.env`
- Test thoroughly with demo account first
- Have sufficient account balance
- Understand all risks

#### Deploy
```bash
# IMPORTANT: Only use after extensive testing!
python trade.py --mode live --trades 10 --confirm
```

---

## 📊 Monitoring

### Log Files
```bash
# View trading logs
tail -f logs/trading.log

# View specific date
cat logs/trading_20250106.log
```

### Database
```bash
# View trades database
sqlite3 data/trades_advanced.db

# Query recent trades
sqlite> SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;
```

### Health Checks
```bash
# Check system status
python -c "
from data_ingestion.connection_manager import ConnectionManager
import os

conn = ConnectionManager(
    os.getenv('IQOPTION_EMAIL'),
    os.getenv('IQOPTION_PASSWORD'),
    'demo'
)
success, msg = conn.connect()
print(f'Status: {\"✅ Healthy\" if success else \"❌ Unhealthy\"}')
print(f'Message: {msg}')
conn.disconnect()
"
```

### Performance Metrics
```bash
# View data ingestion statistics
python -c "
from data_ingestion.market_data_provider import MarketDataProvider
from data_ingestion.connection_manager import ConnectionManager
import os

conn = ConnectionManager(
    os.getenv('IQOPTION_EMAIL'),
    os.getenv('IQOPTION_PASSWORD'),
    'demo'
)
conn.connect()

provider = MarketDataProvider(conn)
provider.get_candles('EURUSD', count=50)

stats = provider.get_statistics()
print('Data Ingestion Statistics:')
for key, value in stats.items():
    print(f'  {key}: {value}')

conn.disconnect()
"
```

---

## 🔍 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to IQOption
```
❌ Connection failed: Connection refused
```

**Solutions**:
1. Check credentials in `.env`
2. Verify internet connection
3. Check IQOption server status
4. Try different network (VPN might help)

```bash
# Test connection
python -c "
from iqoptionapi.stable_api import IQ_Option
import os

api = IQ_Option(os.getenv('IQOPTION_EMAIL'), os.getenv('IQOPTION_PASSWORD'))
check, reason = api.connect()
print(f'Connected: {check}')
print(f'Reason: {reason}')
"
```

### Data Quality Issues

**Problem**: Low quality market data
```
⚠️  Data quality issues detected
```

**Solutions**:
1. Check market hours (forex trades 24/5)
2. Try different trading pairs
3. Increase candle count
4. Clear cache

```bash
# Clear cache and retry
python -c "
from data_ingestion.market_data_provider import MarketDataProvider
from data_ingestion.connection_manager import ConnectionManager
import os

conn = ConnectionManager(
    os.getenv('IQOPTION_EMAIL'),
    os.getenv('IQOPTION_PASSWORD'),
    'demo'
)
conn.connect()

provider = MarketDataProvider(conn)
provider.clear_cache()
print('✅ Cache cleared')

conn.disconnect()
"
```

### AI Model Issues

**Problem**: AI models not working
```
❌ AI models not available
```

**Solutions**:
1. Check API keys in `.env`
2. Verify API key validity
3. Use Free AI (no API key required)

```bash
# Test AI models
python -c "
from config.settings import TradingConfig

print('AI Models Status:')
print(f'  Free AI: {\"✅\" if TradingConfig.USE_FREE_AI else \"❌\"}')
print(f'  OpenAI: {\"✅\" if TradingConfig.USE_OPENAI else \"❌\"}')
print(f'  Claude: {\"✅\" if TradingConfig.USE_CLAUDE else \"❌\"}')
print(f'  DeepSeek: {\"✅\" if TradingConfig.USE_DEEPSEEK else \"❌\"}')
"
```

### Performance Issues

**Problem**: Slow data retrieval
```
⚠️  High latency detected
```

**Solutions**:
1. Enable caching
2. Reduce candle count
3. Check network speed
4. Use local database

```bash
# Enable caching
# Edit .env:
ENABLE_CACHING=true
CACHE_TTL=300
```

---

## 📚 Additional Resources

### Documentation
- [API Reference](docs/API_REFERENCE.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Risk Management Guide](docs/RISK_MANAGEMENT.md)

### Support
- GitHub Issues: [Create Issue](https://github.com/your-repo/issues)
- Documentation: [Full Docs](docs/)
- Logs: `logs/trading.log`

### Best Practices
1. **Always start with demo account**
2. **Test thoroughly before live trading**
3. **Monitor logs regularly**
4. **Set appropriate risk limits**
5. **Keep credentials secure**
6. **Backup database regularly**
7. **Update dependencies periodically**

---

## ⚠️ Important Warnings

### Before Live Trading
- [ ] Tested with demo account (minimum 50 trades)
- [ ] Verified win rate is acceptable
- [ ] Understood all risk parameters
- [ ] Set appropriate position sizes
- [ ] Configured stop-loss limits
- [ ] Have emergency stop plan
- [ ] Backed up configuration

### Risk Disclaimer
**Binary options trading involves significant risk. You can lose your entire investment. This software is provided for educational purposes. Always:**
- Start with demo accounts
- Never risk more than you can afford to lose
- Understand regulations in your jurisdiction
- This is not financial advice
- Past performance does not guarantee future results

---

## 📞 Emergency Procedures

### Stop Trading Immediately
```bash
# If running in terminal
Ctrl+C

# If running in Docker
docker-compose down

# If running as service
systemctl stop kael-trading
```

### Check Current Positions
```bash
python -c "
from iqoptionapi.stable_api import IQ_Option
import os

api = IQ_Option(os.getenv('IQOPTION_EMAIL'), os.getenv('IQOPTION_PASSWORD'))
api.connect()
api.change_balance('PRACTICE')  # or 'REAL'

positions = api.get_positions()
print(f'Open Positions: {len(positions)}')
for pos in positions:
    print(f'  {pos}')

api.close()
"
```

### Reset System
```bash
# Clear cache
rm -rf data/cache/*

# Reset database (CAUTION: Deletes trade history)
rm data/trades_advanced.db

# Reset logs
rm logs/*.log

# Restart
python trade.py --mode demo --trades 1
```

---

**Last Updated**: January 2025  
**Version**: 2.0 (Production Ready)  
**Status**: ✅ Tested and Verified
