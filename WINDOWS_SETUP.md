# 🪟 KAEL Parallel Trading Bot - Windows Setup Guide

## 🚀 Quick Start for Windows Users

### Prerequisites

1. ✅ **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
2. ✅ **Git for Windows** (optional, for monitoring) - [Download here](https://git-scm.com/download/win)
3. ✅ **IQ Option Account** with credentials

### Step 1: Stop Any Running Builds

If you have a build in progress with errors:

**Option A: Using Command Prompt/PowerShell**
```cmd
docker-compose -f docker-compose.parallel.yml down
```

**Option B: Using Docker Desktop**
- Open Docker Desktop
- Go to Containers tab
- Stop and remove `kael-parallel-trading-bot` if it exists

### Step 2: Clean Previous Builds (Optional but Recommended)

```cmd
docker-compose -f docker-compose.parallel.yml down -v
docker system prune -f
```

### Step 3: Verify Your .env File

Open `.env` file in Notepad and verify your credentials:

```env
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
TRADING_MODE=demo
```

### Step 4: Build and Start the Bot

#### Using the Batch File (Easiest)

```cmd
REM Build the image
docker-parallel-bot.bat build

REM Start the bot
docker-parallel-bot.bat start

REM View logs
docker-parallel-bot.bat logs
```

#### Using Docker Compose Directly

```cmd
REM Build and start
docker-compose -f docker-compose.parallel.yml up -d --build

REM View logs
docker-compose -f docker-compose.parallel.yml logs -f
```

## 📊 Monitoring Your Bot

### Option 1: Using the Batch File

```cmd
docker-parallel-bot.bat status
```

### Option 2: Using Git Bash (Best Experience)

If you have Git for Windows installed:

```bash
# In Git Bash terminal
./monitor_parallel_bot.sh
```

### Option 3: Using Web Browser

Open these URLs in your browser:

- **Health Check**: http://localhost:5001/health
- **Statistics**: http://localhost:5001/statistics

### Option 4: Using PowerShell

```powershell
# Get statistics
Invoke-RestMethod -Uri http://localhost:5001/statistics | ConvertTo-Json

# Get health
Invoke-RestMethod -Uri http://localhost:5001/health | ConvertTo-Json
```

### Option 5: Using Command Prompt with curl

```cmd
curl http://localhost:5001/statistics
curl http://localhost:5001/health
```

## 🎮 Bot Management Commands

### Using Batch File (Recommended for Windows)

```cmd
REM Show help
docker-parallel-bot.bat help

REM Build image
docker-parallel-bot.bat build

REM Start bot
docker-parallel-bot.bat start

REM Stop bot
docker-parallel-bot.bat stop

REM Restart bot
docker-parallel-bot.bat restart

REM View logs
docker-parallel-bot.bat logs

REM Check status
docker-parallel-bot.bat status

REM Clean everything
docker-parallel-bot.bat clean

REM Monitor (requires Git Bash)
docker-parallel-bot.bat monitor
```

### Using Docker Compose Directly

```cmd
REM Start
docker-compose -f docker-compose.parallel.yml up -d

REM Stop
docker-compose -f docker-compose.parallel.yml stop

REM Restart
docker-compose -f docker-compose.parallel.yml restart

REM Logs
docker-compose -f docker-compose.parallel.yml logs -f

REM Status
docker-compose -f docker-compose.parallel.yml ps

REM Remove
docker-compose -f docker-compose.parallel.yml down -v
```

## 🔍 Troubleshooting

### Build Fails with Network Errors

The new Alpine-based Dockerfile should fix most network issues. If problems persist:

```cmd
REM Clean everything
docker-compose -f docker-compose.parallel.yml down -v
docker system prune -af

REM Rebuild
docker-parallel-bot.bat build
```

### Container Won't Start

```cmd
REM Check logs
docker logs kael-parallel-trading-bot

REM Check if port 5001 is in use
netstat -ano | findstr :5001

REM Restart Docker Desktop
```

### Can't Access API

1. Wait 30-60 seconds after starting
2. Check if container is running:
   ```cmd
   docker ps
   ```
3. Check logs:
   ```cmd
   docker logs kael-parallel-trading-bot --tail 50
   ```

### Bot Not Trading

1. **Check markets are open**:
   ```cmd
   curl http://localhost:5001/statistics
   ```

2. **Check for errors**:
   ```cmd
   docker logs kael-parallel-trading-bot | findstr ERROR
   ```

3. **Verify connection**:
   ```cmd
   docker logs kael-parallel-trading-bot | findstr "Connected"
   ```

## 📁 File Locations

### Logs

Logs are saved in the `logs` folder:

```cmd
REM View today's log
type logs\binary_bot_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log

REM View trade log
type logs\binary_trades_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
```

### Configuration Files

- **Docker Compose**: `docker-compose.parallel.yml`
- **Dockerfile**: `Dockerfile.parallel`
- **Environment**: `.env`
- **Bot Script**: `autonomous_parallel_trading_bot.py`
- **Management Script**: `docker-parallel-bot.bat`

## ⚙️ Configuration

Edit `.env` file in Notepad:

```env
# Trading mode
TRADING_MODE=demo

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

After editing, restart:

```cmd
docker-parallel-bot.bat restart
```

## 🎯 Quick Commands Reference

```cmd
REM Build
docker-parallel-bot.bat build

REM Start
docker-parallel-bot.bat start

REM Status
docker-parallel-bot.bat status

REM Logs
docker-parallel-bot.bat logs

REM Stop
docker-parallel-bot.bat stop

REM Restart
docker-parallel-bot.bat restart

REM Clean
docker-parallel-bot.bat clean
```

## 🔐 Security Tips

1. ✅ Never commit `.env` file to Git
2. ✅ Always use demo mode for testing
3. ✅ Start with small amounts in live mode
4. ✅ Monitor regularly
5. ✅ Set appropriate risk limits

## 📈 Performance Monitoring

### Using Docker Desktop

1. Open Docker Desktop
2. Click on `kael-parallel-trading-bot` container
3. View:
   - Logs tab for real-time logs
   - Stats tab for CPU/Memory usage
   - Inspect tab for configuration

### Using Command Line

```cmd
REM Container stats
docker stats kael-parallel-trading-bot --no-stream

REM Resource usage
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"
```

## 🆘 Getting Help

### Check Container Status

```cmd
docker ps -a | findstr kael
```

### View Full Logs

```cmd
docker logs kael-parallel-trading-bot
```

### Check Docker Desktop

1. Open Docker Desktop
2. Go to Containers
3. Find `kael-parallel-trading-bot`
4. Click to view details

### Restart Everything

```cmd
REM Stop bot
docker-parallel-bot.bat stop

REM Restart Docker Desktop
REM (Right-click Docker Desktop icon in system tray -> Restart)

REM Start bot
docker-parallel-bot.bat start
```

## 🎉 Success Indicators

Your bot is working when you see:

- ✅ Container status: "Up" in Docker Desktop
- ✅ Health API responds: http://localhost:5001/health
- ✅ Logs show: "Connected. Balance: $XXX.XX"
- ✅ Statistics show active instruments
- ✅ Trade logs show "INSTANT TRADE" entries

## 💡 Tips for Windows Users

1. **Use Command Prompt or PowerShell as Administrator** for better permissions
2. **Keep Docker Desktop running** in the background
3. **Use the batch file** for easier management
4. **Monitor logs** regularly with `docker-parallel-bot.bat logs`
5. **Check status** frequently with `docker-parallel-bot.bat status`

## 🔄 Daily Workflow

```cmd
REM Morning: Check status
docker-parallel-bot.bat status

REM During day: Monitor occasionally
docker-parallel-bot.bat logs

REM Evening: Check performance
curl http://localhost:5001/statistics

REM If needed: Restart
docker-parallel-bot.bat restart
```

## 📞 Support Checklist

Before asking for help, try:

1. ✅ Check logs: `docker-parallel-bot.bat logs`
2. ✅ Check status: `docker-parallel-bot.bat status`
3. ✅ Restart bot: `docker-parallel-bot.bat restart`
4. ✅ Check Docker Desktop is running
5. ✅ Verify `.env` file has correct credentials
6. ✅ Try clean rebuild: `docker-parallel-bot.bat clean` then `docker-parallel-bot.bat build`

---

**Happy Trading! 🚀📈**

*For more details, see `DOCKER_QUICK_START.md`*
