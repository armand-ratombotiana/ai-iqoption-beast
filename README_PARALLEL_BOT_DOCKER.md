# 🚀 KAEL Autonomous Parallel Trading Bot - Docker Deployment

## 📋 Overview

This guide covers the Docker deployment of the **Optimized 24/7 Autonomous Parallel Trading Bot** with instant execution and zero-delay technical analysis.

### ✨ Key Features

- ⚡ **INSTANT EXECUTION** - Zero-delay trade execution for accurate TA
- 🔄 **24/7 CONTINUOUS OPERATION** - Auto-recovery and reconnection
- 📊 **PARALLEL MULTI-INSTRUMENT TRADING** - Trade up to 10 instruments simultaneously
- ⏱️ **1-MINUTE BINARY OPTIONS** - Trade every minute on each instrument
- 🎯 **OPTIMIZED SCANNING** - 3-second scan intervals (configurable)
- 🧵 **MULTI-THREADED** - 15 worker threads for parallel execution
- 🏥 **HEALTH MONITORING** - Built-in health API on port 5001
- 📈 **PORTFOLIO RISK MANAGEMENT** - Advanced risk allocation across instruments

---

## 🛠️ Prerequisites

1. **Docker** and **Docker Compose** installed
2. **IQ Option Account** (demo or live)
3. **Environment Variables** configured in `.env` file

---

## 📦 Quick Start

### 1️⃣ Build the Docker Image

```bash
docker-compose -f docker-compose.parallel.yml build
```

### 2️⃣ Start the Bot (Demo Mode)

```bash
docker-compose -f docker-compose.parallel.yml up -d
```

### 3️⃣ View Logs

```bash
docker-compose -f docker-compose.parallel.yml logs -f parallel-trading-bot
```

### 4️⃣ Stop the Bot

```bash
docker-compose -f docker-compose.parallel.yml down
```

---

## ⚙️ Configuration

### Environment Variables (`.env` file)

```bash
# ============================================================================
# IQ OPTION CREDENTIALS (REQUIRED)
# ============================================================================
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password

# ============================================================================
# TRADING MODE
# ============================================================================
TRADING_MODE=demo  # Options: demo, live

# ============================================================================
# PARALLEL TRADING SETTINGS
# ============================================================================
MAX_CONCURRENT_INSTRUMENTS=5        # Max instruments trading simultaneously (1-10)
MAX_INSTRUMENTS_TO_MONITOR=20       # Total instruments to monitor (10-50)
PORTFOLIO_RISK_PERCENT=10.0         # Total portfolio risk % (5-20)
MAX_RISK_PER_INSTRUMENT=2.5         # Max risk per instrument % (1-5)
INSTRUMENT_SCAN_INTERVAL=3          # Seconds between scans (OPTIMIZED: 3s)
MAX_WORKER_THREADS=15               # Worker threads for parallel execution
MAX_TRADES_PER_INSTRUMENT_HOUR=60   # Max trades per instrument per hour

# ============================================================================
# BINARY OPTIONS SETTINGS
# ============================================================================
BASE_TRADE_AMOUNT=1.0               # Base trade amount
MAX_TRADE_AMOUNT=10.0               # Maximum trade amount
TRADING_ASSETS=EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,AUDJPY

# ============================================================================
# RISK MANAGEMENT
# ============================================================================
MAX_DAILY_LOSS=50                   # Maximum daily loss limit
MAX_DAILY_PROFIT=100                # Daily profit target
MAX_CONSECUTIVE_LOSSES=5            # Max consecutive losses before pause
MIN_BALANCE=50                      # Minimum balance to continue trading
MAX_TRADES_PER_HOUR=300             # Global hourly trade limit
MAX_TRADES_PER_DAY=7200             # Global daily trade limit

# ============================================================================
# AI SIGNAL REQUIREMENTS
# ============================================================================
MIN_AI_CONFIDENCE=65                # Minimum AI confidence to trade (50-99)

# ============================================================================
# HEALTH MONITORING
# ============================================================================
ENABLE_HEALTH_API=true
HEALTH_API_PORT=5001
```

---

## 🎯 Trading Modes

### Demo Mode (Default - Recommended for Testing)

```bash
# In .env file
TRADING_MODE=demo
```

```bash
docker-compose -f docker-compose.parallel.yml up -d
```

### Live Mode (⚠️ REAL MONEY)

```bash
# In .env file
TRADING_MODE=live
```

```bash
# Start with explicit confirmation
docker-compose -f docker-compose.parallel.yml up -d
```

**⚠️ WARNING:** Live mode trades with real money. Always test thoroughly in demo mode first!

---

## 📊 Monitoring

### Health Check Endpoint

```bash
# Check bot health
curl http://localhost:5001/health

# Get detailed statistics
curl http://localhost:5001/statistics
```

### View Real-Time Logs

```bash
# Follow logs
docker-compose -f docker-compose.parallel.yml logs -f parallel-trading-bot

# View last 100 lines
docker-compose -f docker-compose.parallel.yml logs --tail=100 parallel-trading-bot
```

### Check Container Status

```bash
# View running containers
docker ps

# View container stats (CPU, Memory)
docker stats kael-parallel-trading-bot
```

---

## 🔧 Management Commands

### Restart the Bot

```bash
docker-compose -f docker-compose.parallel.yml restart parallel-trading-bot
```

### Stop the Bot Gracefully

```bash
docker-compose -f docker-compose.parallel.yml stop parallel-trading-bot
```

### Remove Container and Volumes

```bash
docker-compose -f docker-compose.parallel.yml down -v
```

### Rebuild After Code Changes

```bash
docker-compose -f docker-compose.parallel.yml build --no-cache
docker-compose -f docker-compose.parallel.yml up -d
```

### Access Container Shell

```bash
docker exec -it kael-parallel-trading-bot /bin/bash
```

---

## 📈 Performance Optimization

### Optimized Settings (Current Configuration)

- **Scan Interval:** 3 seconds (down from 10s)
- **Execution Delay:** 0 seconds (instant execution)
- **Result Wait:** 65 seconds (down from 70s)
- **Worker Threads:** 15 (up from 10)
- **Signal Generation Timeout:** 0.5 seconds

### Adjust for Your System

Edit `docker-compose.parallel.yml`:

```yaml
environment:
  # Faster scanning (more aggressive)
  - INSTRUMENT_SCAN_INTERVAL=2
  
  # More concurrent instruments
  - MAX_CONCURRENT_INSTRUMENTS=10
  
  # More worker threads (if you have CPU cores)
  - MAX_WORKER_THREADS=20
```

---

## 📁 Log Files

Logs are persisted in the `./logs` directory:

```
logs/
├── parallel_bot_optimized_20250124.log      # Main bot log
└── parallel_trades_optimized_20250124.log   # Trade-specific log
```

### View Trade Logs

```bash
# View today's trades
tail -f logs/parallel_trades_optimized_$(date +%Y%m%d).log

# Search for wins
grep "WIN" logs/parallel_trades_optimized_*.log

# Search for specific instrument
grep "EURUSD" logs/parallel_trades_optimized_*.log
```

---

## 🐛 Troubleshooting

### Bot Won't Start

```bash
# Check logs for errors
docker-compose -f docker-compose.parallel.yml logs parallel-trading-bot

# Verify credentials
docker exec -it kael-parallel-trading-bot env | grep IQOPTION
```

### Connection Issues

```bash
# Check if bot can reach IQ Option
docker exec -it kael-parallel-trading-bot ping iqoption.com

# Restart the bot
docker-compose -f docker-compose.parallel.yml restart parallel-trading-bot
```

### High Memory Usage

```bash
# Check resource usage
docker stats kael-parallel-trading-bot

# Reduce concurrent instruments in .env
MAX_CONCURRENT_INSTRUMENTS=3
MAX_WORKER_THREADS=10
```

### No Trades Executing

1. Check if markets are open
2. Verify balance is sufficient
3. Check AI confidence threshold
4. Review risk limits

```bash
# Check statistics
curl http://localhost:5001/statistics | jq
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use demo mode** for testing
3. **Set appropriate risk limits**
4. **Monitor regularly** via health API
5. **Keep credentials secure**

---

## 📊 Statistics API

### Get Portfolio Statistics

```bash
curl http://localhost:5001/statistics | jq
```

**Response Example:**

```json
{
  "status": "running",
  "mode": "demo",
  "operation_mode": "OPTIMIZED 24/7",
  "balance": 10000.00,
  "daily_profit": 45.50,
  "daily_loss": 12.30,
  "daily_net": 33.20,
  "trades_today": 127,
  "wins_today": 73,
  "losses_today": 54,
  "win_rate": 57.48,
  "active_instruments": ["EURUSD", "GBPUSD", "USDJPY"],
  "active_count": 3,
  "instruments_traded": 16,
  "uptime_hours": 12.5,
  "avg_scan_time_ms": 245,
  "avg_execution_time_ms": 89
}
```

### Stop Bot via API

```bash
curl -X POST http://localhost:5001/stop
```

---

## 🚀 Advanced Usage

### Run with Custom Configuration

Create a custom docker-compose file:

```yaml
# docker-compose.custom.yml
version: '3.8'

services:
  parallel-trading-bot:
    extends:
      file: docker-compose.parallel.yml
      service: parallel-trading-bot
    environment:
      - MAX_CONCURRENT_INSTRUMENTS=10
      - INSTRUMENT_SCAN_INTERVAL=2
      - MAX_WORKER_THREADS=20
```

Run with custom config:

```bash
docker-compose -f docker-compose.custom.yml up -d
```

### Multiple Bot Instances

Run multiple bots with different configurations:

```bash
# Bot 1 - Conservative
docker-compose -f docker-compose.parallel.yml -p bot1 up -d

# Bot 2 - Aggressive (different port)
docker-compose -f docker-compose.parallel-aggressive.yml -p bot2 up -d
```

---

## 📞 Support

For issues or questions:

1. Check logs: `docker-compose -f docker-compose.parallel.yml logs`
2. Review configuration in `.env`
3. Check health endpoint: `curl http://localhost:5001/health`
4. Verify IQ Option credentials

---

## 📝 Notes

- **Optimized for instant execution** - Minimal delays for accurate TA
- **24/7 operation** - Auto-recovery on connection loss
- **Parallel trading** - Multiple instruments simultaneously
- **1-minute trades** - Fast-paced binary options
- **Health monitoring** - Built-in API for status checks

---

## ⚡ Quick Reference

```bash
# Build
docker-compose -f docker-compose.parallel.yml build

# Start (detached)
docker-compose -f docker-compose.parallel.yml up -d

# View logs
docker-compose -f docker-compose.parallel.yml logs -f

# Check health
curl http://localhost:5001/health

# Get statistics
curl http://localhost:5001/statistics

# Stop
docker-compose -f docker-compose.parallel.yml down

# Restart
docker-compose -f docker-compose.parallel.yml restart
```

---

**🎯 Ready to trade! The bot will start automatically and run 24/7 with optimized instant execution.**
