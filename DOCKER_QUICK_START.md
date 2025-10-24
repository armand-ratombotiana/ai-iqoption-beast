# 🚀 KAEL Parallel Trading Bot - Docker Quick Start Guide

## 📋 Prerequisites

1. **Docker Desktop** installed and running
2. **IQ Option Account** credentials
3. **Git Bash** or similar terminal (for Windows)

## 🔧 Setup Steps

### 1. Stop Current Build (if running)

If you have a build in progress with errors, stop it:

```bash
# Press Ctrl+C in the terminal where docker-compose is running
# Then run:
docker-compose -f docker-compose.parallel.yml down
```

### 2. Clean Previous Build (Optional)

```bash
# Remove old containers and images
docker-compose -f docker-compose.parallel.yml down -v
docker system prune -f
```

### 3. Verify Environment File

Make sure your `.env` file exists and has your credentials:

```bash
cat .env | grep IQOPTION
```

You should see:
```
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
```

### 4. Build and Start the Bot

#### Option A: Using the Management Script (Recommended)

```bash
# Make scripts executable
chmod +x docker-parallel-bot.sh monitor_parallel_bot.sh

# Build the image
./docker-parallel-bot.sh build

# Start the bot
./docker-parallel-bot.sh start

# Monitor the bot
./monitor_parallel_bot.sh
```

#### Option B: Using Docker Compose Directly

```bash
# Build and start in one command
docker-compose -f docker-compose.parallel.yml up -d --build

# View logs
docker-compose -f docker-compose.parallel.yml logs -f
```

## 📊 Monitoring

### Real-time Dashboard

```bash
./monitor_parallel_bot.sh
```

Features:
- 🏦 Account balance and P/L
- 📊 Trading statistics and win rate
- 🔄 Active instruments
- ⚡ Performance metrics
- 🏆 Top performing instruments
- 📝 Recent logs
- 🐳 Container stats

### Quick Status Check

```bash
./docker-parallel-bot.sh status
```

### View Logs

```bash
# Live logs
./docker-parallel-bot.sh logs

# Or with docker-compose
docker-compose -f docker-compose.parallel.yml logs -f
```

### API Endpoints

Once running, access:

- **Health Check**: http://localhost:5001/health
- **Statistics**: http://localhost:5001/statistics

```bash
# Check health
curl http://localhost:5001/health

# Get statistics
curl http://localhost:5001/statistics | python -m json.tool
```

## 🎮 Bot Management

### Start Bot

```bash
./docker-parallel-bot.sh start
```

### Stop Bot

```bash
./docker-parallel-bot.sh stop
```

### Restart Bot

```bash
./docker-parallel-bot.sh restart
```

### View Status

```bash
./docker-parallel-bot.sh status
```

### Clean Everything

```bash
./docker-parallel-bot.sh clean
```

## 🔍 Troubleshooting

### Build Fails with Network Errors

The optimized Dockerfile now handles network issues better. If you still have problems:

```bash
# Clean everything
docker-compose -f docker-compose.parallel.yml down -v
docker system prune -af

# Try building again
./docker-parallel-bot.sh build
```

### Container Won't Start

```bash
# Check logs
docker logs kael-parallel-trading-bot

# Check if port 5001 is available
netstat -an | grep 5001

# Restart Docker Desktop
```

### Can't Connect to API

```bash
# Wait 30-60 seconds after starting for bot to initialize
# Then check:
curl http://localhost:5001/health

# If still failing, check logs:
docker logs kael-parallel-trading-bot --tail 50
```

### Bot Not Trading

1. **Check if markets are open**:
   ```bash
   curl http://localhost:5001/statistics | grep active_instruments
   ```

2. **Check logs for errors**:
   ```bash
   docker logs kael-parallel-trading-bot | grep ERROR
   ```

3. **Verify credentials**:
   ```bash
   docker logs kael-parallel-trading-bot | grep "Connected"
   ```

## 📁 File Locations

### Logs

Logs are persisted outside the container:

```bash
# View today's logs
tail -f logs/binary_bot_$(date +%Y%m%d).log

# View trade logs
tail -f logs/binary_trades_$(date +%Y%m%d).log
```

### Configuration

- **Docker Compose**: `docker-compose.parallel.yml`
- **Dockerfile**: `Dockerfile.parallel`
- **Environment**: `.env`
- **Bot Script**: `autonomous_parallel_trading_bot.py`

## ⚙️ Configuration

Edit `.env` file to customize:

```bash
# Trading mode
TRADING_MODE=demo  # or 'live'

# Parallel trading
MAX_CONCURRENT_INSTRUMENTS=5
MAX_INSTRUMENTS_TO_MONITOR=20

# Risk management
PORTFOLIO_RISK_PERCENT=10.0
MAX_RISK_PER_INSTRUMENT=2.5

# Trade amounts
BASE_TRADE_AMOUNT=1.0
MAX_TRADE_AMOUNT=10.0

# Limits
MAX_DAILY_LOSS=50
MAX_DAILY_PROFIT=100
```

After changing `.env`, restart the bot:

```bash
./docker-parallel-bot.sh restart
```

## 🎯 Quick Commands Reference

```bash
# Build
./docker-parallel-bot.sh build

# Start
./docker-parallel-bot.sh start

# Monitor
./monitor_parallel_bot.sh

# Logs
./docker-parallel-bot.sh logs

# Status
./docker-parallel-bot.sh status

# Stop
./docker-parallel-bot.sh stop

# Restart
./docker-parallel-bot.sh restart

# Clean
./docker-parallel-bot.sh clean
```

## 🔐 Security Notes

1. **Never commit `.env` file** to version control
2. **Use demo mode** for testing
3. **Start with small amounts** in live mode
4. **Monitor regularly** using the dashboard
5. **Set appropriate risk limits** in `.env`

## 📈 Performance Tips

1. **Adjust scan interval** for faster/slower trading:
   ```bash
   INSTRUMENT_SCAN_INTERVAL=3  # seconds
   ```

2. **Increase concurrent instruments** for more opportunities:
   ```bash
   MAX_CONCURRENT_INSTRUMENTS=10
   ```

3. **Monitor resource usage**:
   ```bash
   docker stats kael-parallel-trading-bot
   ```

## 🆘 Support

If you encounter issues:

1. Check logs: `./docker-parallel-bot.sh logs`
2. Check status: `./docker-parallel-bot.sh status`
3. Restart bot: `./docker-parallel-bot.sh restart`
4. Clean and rebuild: `./docker-parallel-bot.sh clean` then `./docker-parallel-bot.sh build`

## 🎉 Success Indicators

Bot is working correctly when you see:

- ✅ "Connected. Balance: $XXX.XX" in logs
- ✅ Health API responding at http://localhost:5001/health
- ✅ Statistics showing active instruments
- ✅ Trade logs showing "INSTANT TRADE" entries
- ✅ Monitor dashboard updating every 10 seconds

---

**Happy Trading! 🚀📈**
