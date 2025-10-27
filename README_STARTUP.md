# 🤖 KAEL Autonomous Parallel Trading Bot - Startup Guide

## ✅ Fixes Applied

1. **Fixed Syntax Errors**:
   - Added missing `setup_logging()` function
   - Added missing `BinaryOptionCalculator` class
   - Added missing `ApiClient` class with rate limiting
   - Fixed `ParallelTradingConfig` class structure
   - Added all missing configuration parameters

2. **Enhanced Features**:
   - Complete configuration with all environment variables
   - Database logging support (TradeLogger)
   - Rate-limited API client to prevent broker throttling
   - Binary option specific calculations
   - Comprehensive logging system

## 🚀 Quick Start

### Step 1: Start Docker Desktop

**IMPORTANT**: Docker Desktop must be running before proceeding!

1. Open Docker Desktop application
2. Wait for Docker to fully start (green icon in system tray)
3. Verify Docker is running:
   ```bash
   docker ps
   ```

### Step 2: Start the Trading Bot

#### Option A: Using the automated script (Recommended)
```bash
bash start_and_monitor.sh
```

#### Option B: Manual start
```bash
# Build the image
docker-compose -f docker-compose.parallel.yml build

# Start the bot
docker-compose -f docker-compose.parallel.yml up -d

# View logs
docker-compose -f docker-compose.parallel.yml logs -f
```

### Step 3: Monitor the Bot

#### Option A: Live Dashboard (Recommended)
```bash
python monitor_dashboard.py
```

#### Option B: Docker Logs
```bash
docker-compose -f docker-compose.parallel.yml logs -f parallel-trading-bot
```

#### Option C: Health API Endpoints
```bash
# Statistics
curl -s http://localhost:5001/statistics | python -m json.tool

# Recent Trades
curl -s http://localhost:5001/recent_trades?limit=20 | python -m json.tool

# Strategy Stats
curl -s http://localhost:5001/strategy_stats | python -m json.tool

# Health Check
curl http://localhost:5001/health
```

## 📊 Monitoring Endpoints

- **Health API**: http://localhost:5001
- **Statistics**: http://localhost:5001/statistics
- **Recent Trades**: http://localhost:5001/recent_trades
- **Strategy Stats**: http://localhost:5001/strategy_stats

## 🛑 Stop the Bot

```bash
docker-compose -f docker-compose.parallel.yml down
```

## 🔄 Restart the Bot

```bash
docker-compose -f docker-compose.parallel.yml restart
```

## 📁 Important Files

- `autonomous_parallel_trading_bot.py` - Main bot code (✅ FIXED)
- `docker-compose.parallel.yml` - Docker configuration
- `Dockerfile.parallel` - Docker image definition
- `.env` - Environment variables (credentials, settings)
- `start_and_monitor.sh` - Automated startup script
- `monitor_dashboard.py` - Live monitoring dashboard

## ⚙️ Configuration

Edit `.env` file to customize settings:

### Key Settings

```bash
# Trading Mode
TRADING_MODE=demo  # or 'live'

# Balance
ENABLE_FICTITIOUS_BALANCE=true
FICTITIOUS_START_BALANCE=100.0

# Parallel Trading
MAX_CONCURRENT_INSTRUMENTS=3
MAX_INSTRUMENTS_TO_MONITOR=20

# Binary Options
BASE_TRADE_AMOUNT=1.0
MAX_TRADE_AMOUNT=10.0
MIN_PAYOUT_RATIO=0.65

# Risk Management
MAX_DAILY_LOSS=50
MAX_DAILY_PROFIT=100
MAX_CONSECUTIVE_LOSSES=5

# AI Confidence
MIN_AI_CONFIDENCE=60
```

## 📝 Database Logging

The bot logs all trades to a SQLite database located at:
- `database_files/kael_trading.db` (inside container)
- `./database_files` (on host, persisted)

View database schema in `database/schema.sql`

## 🔍 Logs Location

- **Container logs**: `docker-compose -f docker-compose.parallel.yml logs`
- **File logs**: `./logs/parallel_bot_YYYYMMDD.log`
- **Database**: `./database_files/kael_trading.db`

## ⚠️ Important Notes

1. **Demo Mode**: The bot starts in DEMO mode by default. Set `TRADING_MODE=live` in `.env` for real trading.

2. **Fictitious Balance**: By default, the bot uses a fictitious $100 balance for testing. Set `ENABLE_FICTITIOUS_BALANCE=false` to use real balance.

3. **Rate Limiting**: The bot includes API rate limiting (0.3s minimum between calls) to prevent broker throttling.

4. **Binary Options**: Optimized for 1-minute binary options with payout awareness.

5. **24/7 Operation**: The bot is designed for continuous operation with auto-recovery.

## 🐛 Troubleshooting

### Bot won't start
1. Check Docker is running: `docker ps`
2. Check .env file exists and has credentials
3. Check logs: `docker-compose -f docker-compose.parallel.yml logs`

### Can't connect to API
1. Wait 30 seconds after starting for initialization
2. Check port 5001 is not in use: `netstat -an | grep 5001`
3. Check container is running: `docker-compose -f docker-compose.parallel.yml ps`

### No trades being executed
1. Check market hours (forex closes on weekends)
2. Check balance is sufficient
3. Check AI confidence threshold in .env
4. Check logs for rejection reasons

### Database errors
1. Check `./database_files` directory exists and is writable
2. Delete and recreate: `rm -rf database_files && mkdir database_files`

## 📈 Performance Tips

1. **Reduce Instruments**: Lower `MAX_CONCURRENT_INSTRUMENTS` if experiencing timing issues
2. **Adjust Confidence**: Increase `MIN_AI_CONFIDENCE` for more selective trading
3. **Monitor Resources**: Check CPU/memory usage in Docker Desktop

## 🔐 Security

- Never commit `.env` file to Git
- Use DEMO mode for testing
- Monitor balance and P&L regularly
- Set reasonable daily loss limits

## 📞 Support

- Check logs first: `docker-compose -f docker-compose.parallel.yml logs`
- View statistics: `curl http://localhost:5001/statistics`
- Monitor live: `python monitor_dashboard.py`

## ✅ Verification Checklist

- [ ] Docker Desktop is running
- [ ] .env file has valid credentials
- [ ] Container built successfully
- [ ] Bot container is running
- [ ] Health API responds (http://localhost:5001/health)
- [ ] Statistics endpoint works
- [ ] Logs show bot activity
- [ ] Dashboard displays data (monitor_dashboard.py)

---

**Ready to trade!** The bot is now fixed and ready to run. Follow the Quick Start steps above.
