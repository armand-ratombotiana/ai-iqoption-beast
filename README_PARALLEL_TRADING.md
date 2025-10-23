# 🚀 Parallel Multi-Instrument Trading System

## Overview

Trade **multiple instruments simultaneously** with advanced portfolio risk management, independent signal generation, and real-time performance tracking.

---

## ✨ Key Features

### 🎯 Multi-Instrument Trading
- **Up to 10 concurrent instruments** trading simultaneously
- Independent AI signal generation per instrument
- Dynamic instrument selection based on market conditions
- Per-instrument performance tracking and statistics

### 💼 Portfolio Risk Management
- **Portfolio-wide risk allocation** (default: 10% of balance)
- **Per-instrument risk limits** (default: 2.5% per instrument)
- Correlation-aware position sizing
- Real-time balance monitoring and rebalancing
- Automatic risk release after trade completion

### 📊 Advanced Controls
- Per-instrument hourly trade limits
- Portfolio-wide daily/hourly limits
- Concurrent position limits
- Minimum time between trades per instrument
- Daily profit/loss limits

### 📈 Performance Tracking
- Individual instrument statistics
- Portfolio-level metrics
- Win rate per instrument
- Profit/loss tracking
- Best/worst performing instruments

---

## 🚀 Quick Start

### 1. Setup Configuration

```bash
# Copy the example configuration
cp .env.parallel.example .env

# Edit with your credentials and preferences
nano .env
```

**Minimum required settings:**
```bash
TRADING_MODE=demo
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
MAX_CONCURRENT_INSTRUMENTS=8
```

### 2. Run the Bot

```bash
# Direct execution
python3 autonomous_parallel_trading_bot.py

# Or use the test script
bash run_parallel_test.sh
```

### 3. Monitor Performance

```bash
# Get real-time statistics
curl http://localhost:5001/statistics

# Health check
curl http://localhost:5001/health

# Stop the bot
curl -X POST http://localhost:5001/stop
```

---

## ⚙️ Configuration Presets

### Conservative (Low Risk)
```bash
MAX_CONCURRENT_INSTRUMENTS=3
PORTFOLIO_RISK_PERCENT=5.0
MAX_RISK_PER_INSTRUMENT=1.5
MIN_AI_CONFIDENCE=80
MAX_TRADES_PER_HOUR=20
```

### Balanced (Recommended)
```bash
MAX_CONCURRENT_INSTRUMENTS=5
PORTFOLIO_RISK_PERCENT=10.0
MAX_RISK_PER_INSTRUMENT=2.5
MIN_AI_CONFIDENCE=70
MAX_TRADES_PER_HOUR=50
```

### Aggressive (High Volume)
```bash
MAX_CONCURRENT_INSTRUMENTS=10
PORTFOLIO_RISK_PERCENT=15.0
MAX_RISK_PER_INSTRUMENT=3.0
MIN_AI_CONFIDENCE=65
MAX_TRADES_PER_HOUR=100
```

---

## 📊 How It Works

### Trading Cycle (Every 30 seconds)

```
1. SCAN PHASE
   ├── Check portfolio constraints
   ├── Get available instruments
   └── Filter by market hours

2. ANALYSIS PHASE (Parallel)
   ├── Generate AI signals per instrument
   ├── Calculate position sizes
   └── Check per-instrument rules

3. EXECUTION PHASE (Concurrent)
   ├── Execute trades simultaneously
   ├── Allocate portfolio risk
   └── Track active positions

4. MONITORING PHASE
   ├── Wait for trade results
   ├── Update statistics
   └── Release risk allocation
```

### Risk Management Example

```
Portfolio Balance: $1000
├── Portfolio Risk Budget: $100 (10%)
│   ├── EURUSD: $25 (2.5%) - ACTIVE
│   ├── GBPUSD: $25 (2.5%) - ACTIVE
│   ├── USDJPY: $25 (2.5%) - ACTIVE
│   ├── AUDUSD: $25 (2.5%) - ACTIVE
│   └── Available: $0 (0%)
└── Reserved: $900 (90%)
```

---

## 📈 Statistics API

### Get Current Statistics

```bash
curl http://localhost:5001/statistics
```

**Response:**
```json
{
  "status": "running",
  "mode": "demo",
  "balance": 1050.25,
  "daily_profit": 75.50,
  "daily_loss": 25.25,
  "daily_net": 50.25,
  "trades_today": 45,
  "wins_today": 28,
  "losses_today": 17,
  "win_rate": 62.22,
  "active_instruments": ["EURUSD", "GBPUSD", "USDJPY"],
  "active_count": 3,
  "total_risk_allocated": 75.00,
  "instruments_traded": 8,
  "instrument_stats": [
    {
      "instrument": "EURUSD",
      "total_trades": 12,
      "wins": 8,
      "losses": 4,
      "win_rate": 66.67,
      "profit": 15.50,
      "consecutive_wins": 2,
      "is_trading": true
    }
  ]
}
```

---

## 📝 Files Created

```
autonomous_parallel_trading_bot.py    # Main parallel trading bot
PARALLEL_TRADING_GUIDE.md            # Comprehensive guide
.env.parallel.example                # Configuration template
run_parallel_test.sh                 # Test script
README_PARALLEL_TRADING.md           # This file
```

---

## 🎛️ Key Configuration Options

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| `MAX_CONCURRENT_INSTRUMENTS` | Max simultaneous trades | 5 | 1-10 |
| `MAX_INSTRUMENTS_TO_MONITOR` | Total instruments to scan | 20 | 10-50 |
| `PORTFOLIO_RISK_PERCENT` | Total portfolio risk % | 10.0 | 5-20 |
| `MAX_RISK_PER_INSTRUMENT` | Risk per instrument % | 2.5 | 1-5 |
| `MIN_AI_CONFIDENCE` | Min confidence to trade | 65 | 60-90 |
| `INSTRUMENT_SCAN_INTERVAL` | Seconds between scans | 30 | 20-60 |
| `MAX_TRADES_PER_HOUR` | Total hourly limit | 50 | 10-200 |

---

## 📋 Comparison: Single vs Parallel Trading

| Feature | Single Instrument | Parallel (5 Instruments) |
|---------|------------------|--------------------------|
| **Trades/Hour** | ~10 | ~50 |
| **Diversification** | None | High |
| **Risk Spread** | Concentrated | Distributed |
| **Opportunities** | Limited | 5x More |
| **Complexity** | Low | Medium |
| **CPU Usage** | Low | Medium |
| **Profit Potential** | Limited | Higher |

---

## 🔍 Monitoring & Logs

### Log Files

```bash
# Main log with all activities
tail -f logs/parallel_bot_20250123.log

# Trade-specific log
tail -f logs/parallel_trades_20250123.log
```

### Real-Time Monitoring

```bash
# Watch statistics every 5 seconds
watch -n 5 'curl -s http://localhost:5001/statistics | python3 -m json.tool'
```

---

## ⚠️ Important Notes

### Risk Management
1. **Never allocate more than 10-15%** of balance to active trades
2. **Keep per-instrument risk at 1-3%** of balance
3. **Set realistic daily loss limits** (5-10% of balance)
4. **Always start in DEMO mode** to test configuration

### Performance Tips
1. Start with **3-5 concurrent instruments**
2. Monitor the **first hour closely**
3. Increase concurrent instruments **gradually**
4. Adjust scan interval based on **system resources**

### Common Issues

**Issue**: Portfolio risk limit reached quickly
- **Solution**: Increase `PORTFOLIO_RISK_PERCENT` or decrease `MAX_RISK_PER_INSTRUMENT`

**Issue**: Not enough trading opportunities
- **Solution**: Increase `MAX_INSTRUMENTS_TO_MONITOR` or lower `MIN_AI_CONFIDENCE`

**Issue**: Too many trades, can't keep up
- **Solution**: Increase `INSTRUMENT_SCAN_INTERVAL` or decrease `MAX_CONCURRENT_INSTRUMENTS`

---

## 🎯 Best Practices

1. ✅ **Always test in DEMO mode first**
2. ✅ **Start with conservative settings**
3. ✅ **Monitor the first 30 minutes closely**
4. ✅ **Set realistic daily loss limits**
5. ✅ **Use the health API for monitoring**
6. ✅ **Review logs daily**
7. ✅ **Adjust based on results**
8. ✅ **Never risk more than you can afford to lose**

---

## 📚 Documentation

- **[PARALLEL_TRADING_GUIDE.md](PARALLEL_TRADING_GUIDE.md)** - Comprehensive guide with strategies
- **[.env.parallel.example](.env.parallel.example)** - Configuration template with all options
- **[autonomous_parallel_trading_bot.py](autonomous_parallel_trading_bot.py)** - Main bot source code

---

## 🚦 Quick Reference

### Start Trading
```bash
python3 autonomous_parallel_trading_bot.py
```

### Run Test
```bash
bash run_parallel_test.sh
```

### Check Status
```bash
curl http://localhost:5001/statistics
```

### Stop Bot
```bash
curl -X POST http://localhost:5001/stop
```

---

## 🆚 When to Use Parallel Trading

### ✅ Use Parallel Trading When:
- You want to **diversify across multiple instruments**
- You have a **larger balance** ($500+)
- You want to **maximize trading opportunities**
- You can **monitor multiple positions**
- You want **higher profit potential**

### ❌ Use Single Instrument When:
- You're **just starting out**
- You have a **smaller balance** (<$200)
- You prefer **simplicity**
- You want to **focus on one market**
- You're **learning the system**

---

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review statistics via health API
3. Verify `.env` configuration
4. Ensure credentials are correct
5. Check that markets are open

---

## 🎉 Example Session Output

```
🤖 PARALLEL MULTI-INSTRUMENT TRADING BOT INITIALIZED
📊 Max Concurrent Instruments: 5
🔌 Connecting to IQ Option...
✅ Connected. Balance: $1000.00
🔍 Scanning 15 instruments...
📊 Found 12 available instruments

🎯 TRADE [EURUSD]: CALL $2.50 @ 75%
🎯 TRADE [GBPUSD]: PUT $2.25 @ 72%
🎯 TRADE [USDJPY]: CALL $2.00 @ 68%

✅ [EURUSD] Order placed: 12345
✅ [GBPUSD] Order placed: 12346
✅ [USDJPY] Order placed: 12347

📈 RESULT [EURUSD]: WIN
   P/L: +$1.87
   Balance: $1001.87

📈 RESULT [GBPUSD]: WIN
   P/L: +$1.68
   Balance: $1003.55

📈 RESULT [USDJPY]: LOSS
   P/L: -$2.00
   Balance: $1001.55

Daily P/L: +$1.55
Win Rate: 66.67%
Active Instruments: 0/3
```

---

**Happy Parallel Trading! 🚀**

*Remember: Always start in DEMO mode and never risk more than you can afford to lose.*
