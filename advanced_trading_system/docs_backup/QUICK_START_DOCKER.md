# 🚀 Quick Start - Docker Deployment

## 30-Second Start

```bash
# 1. Configure credentials
nano .env

# 2. Start the system
./docker-start.sh

# Done! System is running 24/7
```

## Essential Commands

```bash
# View logs (real-time)
docker-compose logs -f

# Stop system
docker-compose down

# Restart system
docker-compose restart

# Check status
docker-compose ps

# Check health
docker inspect --format='{{.State.Health.Status}}' kael-trading-system
```

## Requirements

1. Docker 20.10+
2. Docker Compose 2.0+
3. IQOption account

## What You Need to Configure

Edit `.env` file:

```env
IQOPTION_EMAIL=your_email@example.com      # Your IQOption email
IQOPTION_PASSWORD=your_password             # Your IQOption password
ACCOUNT_TYPE=demo                           # Use 'demo' for testing
```

That's it! Everything else uses defaults.

## Default Configuration

- **Trading Mode**: Basic
- **Loop Interval**: 5 minutes
- **AI Model**: Free rule-based AI (no API keys needed)
- **Account**: Demo (safe for testing)
- **Trading Pair**: EURUSD-OTC
- **Trade Duration**: 1 minute
- **Min Confidence**: 60%
- **Trade Amount**: $10

## System Features

✅ **Automatic Reconnection** - Retries 5 times on failures
✅ **Health Monitoring** - Tracks uptime and errors
✅ **Graceful Shutdown** - Finishes trades before stopping
✅ **Free AI** - No API costs
✅ **24/7 Operation** - Automatic restarts
✅ **Persistent Data** - Logs and database saved

## Customization

Edit `docker-compose.yml` CMD line:

```yaml
# Example: Trade every 10 minutes on GBPUSD
command: python run_unified_trading.py --mode basic --loop --loop-interval 600 --pair GBPUSD-OTC --demo
```

Or set environment variables in `.env`:

```env
MIN_CONFIDENCE=70          # Require 70% confidence
DEFAULT_AMOUNT=20          # Trade with $20
MAX_DAILY_LOSS=50          # Stop after $50 loss
```

## Monitoring

```bash
# View system resources
docker stats kael-trading-system

# View last 100 log lines
docker-compose logs --tail=100 trading-system

# Follow errors only
docker-compose logs -f | grep -i error

# Check container info
docker inspect kael-trading-system
```

## Safety

⚠️ **Demo Mode First**: Always test in demo mode before using real money

⚠️ **Start Small**: Use small amounts initially

⚠️ **Monitor Closely**: Watch logs for first 24 hours

⚠️ **Set Limits**: Configure MAX_DAILY_LOSS appropriately

## Troubleshooting

### Container won't start
```bash
docker-compose logs trading-system
# Check for credential errors
```

### Trades not executing
```bash
# Verify connection
docker-compose exec trading-system python -c "print('Connection OK')"
```

### High resource usage
```bash
# Monitor resources
docker stats kael-trading-system
```

## Going to Production

1. **Test in demo for 24+ hours**
2. **Verify trade execution**
3. **Monitor error rates**
4. **Set conservative limits**
5. **Change to real account**:
   ```env
   ACCOUNT_TYPE=real
   ```
6. **Restart system**:
   ```bash
   docker-compose down && docker-compose up -d
   ```

## File Locations

```
./logs/      - Trading logs
./database/  - Trade history database
./.env       - Configuration
```

## Complete Documentation

- **DOCKER_DEPLOYMENT_GUIDE.md** - Full deployment guide
- **ROBUST_SYSTEM_SUMMARY.md** - Complete feature summary
- **UNIFIED_TRADING_GUIDE.md** - Trading system guide

## Support

1. Check logs: `docker-compose logs -f`
2. Review documentation files
3. Verify configuration
4. Test connection

---

**You're ready to trade! 🎯**

Start in demo mode, monitor for 24 hours, then scale up gradually.
