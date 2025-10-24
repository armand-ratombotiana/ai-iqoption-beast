# ⚡ Quick Start - Parallel Trading Bot

## 🚀 Start in 3 Steps

### 1. Ensure `.env` is configured

```bash
# Check if .env exists
cat .env | grep IQOPTION_EMAIL
```

### 2. Build & Start (Linux/Mac)

```bash
./start_parallel_bot.sh
```

### 2. Build & Start (Windows)

```cmd
start_parallel_bot.bat
```

### 3. Monitor

```bash
# Follow logs
docker-compose -f docker-compose.parallel.yml logs -f

# Check health
curl http://localhost:5001/health

# Get statistics
curl http://localhost:5001/statistics
```

---

## 📋 Essential Commands

```bash
# Build image
docker-compose -f docker-compose.parallel.yml build

# Start bot (detached)
docker-compose -f docker-compose.parallel.yml up -d

# View logs (follow)
docker-compose -f docker-compose.parallel.yml logs -f parallel-trading-bot

# Stop bot
docker-compose -f docker-compose.parallel.yml down

# Restart bot
docker-compose -f docker-compose.parallel.yml restart parallel-trading-bot

# Check status
docker ps | grep kael-parallel

# View resource usage
docker stats kael-parallel-trading-bot
```

---

## 🏥 Health Monitoring

```bash
# Health check
curl http://localhost:5001/health

# Full statistics (formatted)
curl http://localhost:5001/statistics | python -m json.tool

# Stop via API
curl -X POST http://localhost:5001/stop
```

---

## 📊 View Logs

```bash
# Real-time logs
docker-compose -f docker-compose.parallel.yml logs -f

# Last 100 lines
docker-compose -f docker-compose.parallel.yml logs --tail=100

# Today's trade log
tail -f logs/parallel_trades_optimized_$(date +%Y%m%d).log

# Search for wins
grep "WIN" logs/parallel_trades_optimized_*.log

# Search for specific instrument
grep "EURUSD" logs/parallel_trades_optimized_*.log
```

---

## ⚙️ Configuration

Edit `.env` file:

```bash
# Trading mode
TRADING_MODE=demo  # or 'live' for real money

# Parallel settings
MAX_CONCURRENT_INSTRUMENTS=5
INSTRUMENT_SCAN_INTERVAL=3

# Risk management
MAX_DAILY_LOSS=50
MAX_DAILY_PROFIT=100
```

After changing `.env`, restart:

```bash
docker-compose -f docker-compose.parallel.yml restart
```

---

## 🐛 Troubleshooting

### Bot won't start

```bash
# Check logs
docker-compose -f docker-compose.parallel.yml logs

# Verify credentials
docker exec -it kael-parallel-trading-bot env | grep IQOPTION

# Rebuild
docker-compose -f docker-compose.parallel.yml build --no-cache
docker-compose -f docker-compose.parallel.yml up -d
```

### No trades executing

1. Check if markets are open
2. Verify balance: `curl http://localhost:5001/statistics | grep balance`
3. Check risk limits in `.env`
4. Review logs for errors

### High CPU/Memory

```bash
# Check resources
docker stats kael-parallel-trading-bot

# Reduce load in .env
MAX_CONCURRENT_INSTRUMENTS=3
MAX_WORKER_THREADS=10
INSTRUMENT_SCAN_INTERVAL=5
```

Then restart:

```bash
docker-compose -f docker-compose.parallel.yml restart
```

---

## 🔄 Update Bot

```bash
# Stop bot
docker-compose -f docker-compose.parallel.yml down

# Pull latest code (if using git)
git pull

# Rebuild
docker-compose -f docker-compose.parallel.yml build --no-cache

# Start
docker-compose -f docker-compose.parallel.yml up -d
```

---

## 🛑 Stop & Clean Up

```bash
# Stop bot (keeps logs)
docker-compose -f docker-compose.parallel.yml down

# Stop and remove volumes (deletes logs)
docker-compose -f docker-compose.parallel.yml down -v

# Remove all Docker resources
docker system prune -a
```

---

## 📈 Performance Tips

### Aggressive Trading

```bash
# In .env
MAX_CONCURRENT_INSTRUMENTS=10
INSTRUMENT_SCAN_INTERVAL=2
MAX_WORKER_THREADS=20
```

### Conservative Trading

```bash
# In .env
MAX_CONCURRENT_INSTRUMENTS=3
INSTRUMENT_SCAN_INTERVAL=5
MAX_WORKER_THREADS=10
MIN_AI_CONFIDENCE=75
```

---

## 🔒 Security

- Never commit `.env` to git
- Use demo mode for testing
- Set appropriate risk limits
- Monitor regularly
- Keep credentials secure

---

## 📞 Quick Help

```bash
# Is bot running?
docker ps | grep kael-parallel

# What's the status?
curl http://localhost:5001/statistics

# Any errors?
docker-compose -f docker-compose.parallel.yml logs --tail=50 | grep ERROR

# How much profit/loss today?
curl http://localhost:5001/statistics | grep daily_net
```

---

**🎯 That's it! Your bot is now running 24/7 with optimized instant execution.**
