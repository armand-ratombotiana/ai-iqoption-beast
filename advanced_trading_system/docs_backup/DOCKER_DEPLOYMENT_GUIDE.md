# 🐳 Docker Deployment Guide - 24/7 Robust Trading System

## Overview

This guide explains how to deploy the KAEL Advanced Trading System in a Docker container for 24/7 operation with automatic restarts, health monitoring, and graceful shutdown handling.

## Features

✅ **24/7 Operation**: Automatic restart on failures
✅ **Health Monitoring**: Built-in health checks
✅ **Graceful Shutdown**: Proper signal handling (SIGINT/SIGTERM)
✅ **Automatic Reconnection**: 5 retries with 10-second delays
✅ **Free AI**: No API keys required (rule-based AI)
✅ **Resource Limits**: CPU and memory constraints
✅ **Persistent Storage**: Logs and database volumes

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- IQOption account credentials

## Quick Start

### 1. Configure Environment Variables

Edit the `.env` file:

```bash
# IQOption Credentials (REQUIRED)
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
ACCOUNT_TYPE=demo

# FREE AI (enabled by default - no API keys needed)
USE_FREE_AI=true
FREE_AI_TYPE=rule-based
FREE_AI_WEIGHT=1.5

# Paid AI (optional - disabled by default)
USE_OPENAI=false
USE_CLAUDE=false
USE_DEEPSEEK=false

# Trading Settings
MIN_CONFIDENCE=60
CONSENSUS_THRESHOLD=0.5
DEFAULT_AMOUNT=10
MAX_SIMULTANEOUS_TRADES=3
COOLDOWN_PERIOD=180

# Risk Management
MAX_DAILY_LOSS=100
MAX_TRADE_AMOUNT=50
MIN_TRADE_AMOUNT=1
RISK_PER_TRADE=0.02
```

### 2. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the trading system (detached mode)
docker-compose up -d

# View logs (real-time)
docker-compose logs -f

# Stop the system
docker-compose down
```

## Docker Commands

### Basic Operations

```bash
# Start the system
docker-compose up -d

# Stop the system (graceful shutdown)
docker-compose down

# Restart the system
docker-compose restart

# View logs
docker-compose logs -f trading-system

# Check status
docker-compose ps
```

### Advanced Operations

```bash
# Build without cache
docker-compose build --no-cache

# Run with custom parameters
docker-compose run --rm trading-system python run_unified_trading.py --mode basic --loop --loop-interval 600 --pair EURUSD-OTC

# Execute commands inside container
docker-compose exec trading-system bash

# View resource usage
docker stats kael-trading-system

# Check health status
docker inspect --format='{{json .State.Health}}' kael-trading-system | python -m json.tool
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IQOPTION_EMAIL` | - | IQOption email (required) |
| `IQOPTION_PASSWORD` | - | IQOption password (required) |
| `ACCOUNT_TYPE` | demo | Account type (demo/real) |
| `USE_FREE_AI` | true | Enable free rule-based AI |
| `FREE_AI_TYPE` | rule-based | AI type (rule-based/hybrid) |
| `MIN_CONFIDENCE` | 60 | Minimum confidence threshold |
| `DEFAULT_AMOUNT` | 10 | Default trade amount |
| `MAX_DAILY_LOSS` | 100 | Maximum daily loss limit |

### Command Line Arguments

You can customize the Docker CMD in `docker-compose.yml`:

```yaml
command: python run_unified_trading.py --mode basic --loop --loop-interval 300 --pair EURUSD-OTC --duration 1
```

Available arguments:
- `--mode` - Trading mode (basic/advanced)
- `--loop` - Enable continuous trading
- `--loop-interval` - Seconds between trades (default: 300)
- `--max-iterations` - Maximum loop iterations (default: infinite)
- `--pair` - Trading pair (default: EURUSD-OTC)
- `--duration` - Trade duration in minutes (default: 1)
- `--demo` - Use demo account
- `--real` - Use real account (use with caution!)

## Persistent Data

The system uses Docker volumes to persist important data:

```
./logs/          # Trading logs (mounted to /app/logs)
./database/      # SQLite database (mounted to /app/database)
./.env           # Environment configuration (read-only)
```

## Health Monitoring

### Docker Health Check

The container includes automatic health checks every 60 seconds:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' kael-trading-system
```

Status values:
- `healthy` - System is working correctly
- `unhealthy` - System has failed health checks
- `starting` - Initial startup period (30 seconds)

### System Health Metrics

The trading system tracks internal health metrics:

- **API Connection**: Connection status to IQOption
- **Last Successful Trade**: Timestamp of last trade
- **Consecutive Errors**: Error tracking for monitoring
- **Total Trades**: Cumulative trade count
- **Uptime**: System uptime since start

These metrics are logged every iteration and can be viewed in logs.

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs trading-system

# Verify environment variables
docker-compose config

# Test configuration
docker-compose run --rm trading-system python -c "from config.settings import TradingConfig; print('Config OK')"
```

### Connection Issues

```bash
# Check IQOption credentials
docker-compose run --rm trading-system python -c "from iqoptionapi.stable_api import IQ_Option; print('API Import OK')"

# Test network connectivity
docker-compose exec trading-system ping -c 3 iqoption.com
```

### High Resource Usage

```bash
# Monitor resource usage
docker stats kael-trading-system

# Adjust resource limits in docker-compose.yml
# deploy.resources.limits.cpus
# deploy.resources.limits.memory
```

### Database Lock Issues

```bash
# Stop all containers
docker-compose down

# Remove database lock
rm -f database/*.db-shm database/*.db-wal

# Restart
docker-compose up -d
```

## Production Deployment

### Real Account Trading

⚠️ **WARNING**: Only use real account mode after thorough testing!

```bash
# Update .env
ACCOUNT_TYPE=real

# Restart container
docker-compose down && docker-compose up -d
```

### Monitoring and Alerts

Set up monitoring for production:

```bash
# Install monitoring tools
pip install prometheus-client

# Add metrics endpoint
# (Requires code modification - see advanced configuration)
```

### Backup Strategy

```bash
# Backup database
docker-compose exec trading-system cp /app/database/trades.db /app/database/trades_backup_$(date +%Y%m%d).db

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

### Automatic Restarts

The system uses `restart: unless-stopped` policy:
- Automatically restarts on crashes
- Won't restart if manually stopped
- Survives system reboots

To change restart policy:

```yaml
restart: always        # Always restart
restart: on-failure    # Restart only on error
restart: no            # Never restart
```

## System Architecture

```
┌─────────────────────────────────────────────┐
│           Docker Container                   │
│  ┌───────────────────────────────────────┐  │
│  │   RobustTradingSystem                 │  │
│  │   ┌─────────────────────────────┐     │  │
│  │   │  Connection Retry Logic     │     │  │
│  │   │  (5 retries, 10s delay)     │     │  │
│  │   └─────────────────────────────┘     │  │
│  │   ┌─────────────────────────────┐     │  │
│  │   │  Health Monitoring          │     │  │
│  │   │  (uptime, errors, trades)   │     │  │
│  │   └─────────────────────────────┘     │  │
│  │   ┌─────────────────────────────┐     │  │
│  │   │  Signal Handlers            │     │  │
│  │   │  (SIGINT, SIGTERM)          │     │  │
│  │   └─────────────────────────────┘     │  │
│  │   ┌─────────────────────────────┐     │  │
│  │   │  Free AI Model              │     │  │
│  │   │  (Rule-based, no API keys)  │     │  │
│  │   └─────────────────────────────┘     │  │
│  └───────────────────────────────────────┘  │
│                                               │
│  Volumes:                                    │
│  • /app/logs (persistent)                    │
│  • /app/database (persistent)                │
│  • .env (read-only)                          │
└─────────────────────────────────────────────┘
```

## Best Practices

1. **Test in Demo Mode First**: Always test with demo account before using real money
2. **Monitor Logs**: Regularly check logs for errors or unusual behavior
3. **Set Resource Limits**: Prevent runaway containers from consuming all resources
4. **Use .env File**: Never hardcode credentials in docker-compose.yml
5. **Regular Backups**: Backup database and logs periodically
6. **Update Dependencies**: Keep Python packages and base image updated
7. **Health Checks**: Enable health checks for automatic recovery
8. **Graceful Shutdown**: Use `docker-compose down` instead of killing container

## Security Considerations

- **Credentials**: Store IQOption credentials in `.env` file (not in Git)
- **API Keys**: Use environment variables for API keys
- **Read-Only Mounts**: Mount `.env` as read-only
- **Network Isolation**: Use Docker networks for isolation
- **Resource Limits**: Prevent DoS attacks with resource constraints
- **Regular Updates**: Keep base image and dependencies updated

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check system status: `docker-compose ps`
4. Test configuration: `docker-compose config`

## License

See main project LICENSE file.
