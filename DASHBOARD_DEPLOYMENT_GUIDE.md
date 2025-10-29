# KAEL Ultimate Dashboard - Complete Deployment Guide

## Overview

The KAEL Ultimate Dashboard is a professional, real-time web interface for monitoring the Ultimate Strategy Evaluator. It provides comprehensive visualization of all 7 binary option strategies, portfolio metrics, and performance analytics.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │   React UI   │───▶│  Evaluator   │───▶│ TimescaleDB │  │
│  │ (Port 3000)  │    │  (Port 5001) │    │ (Port 5432) │  │
│  └──────────────┘    └──────────────┘    └─────────────┘  │
│         │                     │                             │
│         │                     ▼                             │
│         │            ┌──────────────┐                       │
│         └───────────▶│  Prometheus  │                       │
│                      │  (Port 9090) │                       │
│                      └──────────────┘                       │
│                             │                                │
│                             ▼                                │
│                      ┌──────────────┐                       │
│                      │    Grafana   │                       │
│                      │  (Port 3001) │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: 2 cores minimum, 4 cores recommended
- **Disk**: 2GB free space
- **Docker**: Docker Desktop or Docker Engine 20.10+
- **Docker Compose**: v2.0+

### Software Installation

1. **Install Docker Desktop**:
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: Follow official Docker Engine installation guide

2. **Verify Installation**:
   ```bash
   docker --version
   docker-compose --version
   ```

## Quick Start (5 Minutes)

### 1. Clone/Navigate to Project

```bash
cd c:\Users\jratombo\Desktop\dev_tools\pythonEnv\app\KAEL\KAEL
```

### 2. Configure Environment

Ensure `.env` file exists with IQ Option credentials:

```bash
IQOPTION_EMAIL=your-email@example.com
IQOPTION_PASSWORD=your-password
TRADING_MODE=demo
```

### 3. Start All Services

```bash
docker-compose -f docker-compose.ultimate-evaluator.yml up -d --build
```

### 4. Access Dashboard

Open browser to: **http://localhost:3000**

### 5. Verify Services

```bash
# Check all containers are running
docker-compose -f docker-compose.ultimate-evaluator.yml ps

# Expected output:
# NAME                       STATUS        PORTS
# kael-dashboard             Up (healthy)  0.0.0.0:3000->80/tcp
# kael-ultimate-evaluator    Up (healthy)  0.0.0.0:5001->5001/tcp
# kael-timescaledb           Up (healthy)  0.0.0.0:5432->5432/tcp
# kael-prometheus            Up            0.0.0.0:9090->9090/tcp
# kael-grafana               Up            0.0.0.0:3001->3000/tcp
```

## Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | Main UI |
| **Evaluator API** | http://localhost:5001 | Backend API |
| **Prometheus** | http://localhost:9090 | Metrics |
| **Grafana** | http://localhost:3001 | Advanced charts |
| **Database** | localhost:5432 | PostgreSQL |

## Detailed Setup

### Step 1: Environment Configuration

Create or update `.env` file:

```bash
# Required
IQOPTION_EMAIL=your-email@example.com
IQOPTION_PASSWORD=your-password

# Trading Mode (CRITICAL)
TRADING_MODE=demo  # Use 'live' for real money

# Optional Customization
MIN_CONFIDENCE_BASE=0.70
BASE_TRADE_AMOUNT=1.0
STRATEGY_SCAN_INTERVAL=5

# Grafana (optional)
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

### Step 2: Build Services

#### Option A: Build All at Once (Recommended)

```bash
docker-compose -f docker-compose.ultimate-evaluator.yml up -d --build
```

#### Option B: Build Individual Services

```bash
# Build evaluator
docker-compose -f docker-compose.ultimate-evaluator.yml build ultimate-evaluator

# Build dashboard
docker-compose -f docker-compose.ultimate-evaluator.yml build dashboard

# Start all
docker-compose -f docker-compose.ultimate-evaluator.yml up -d
```

### Step 3: Monitor Startup

```bash
# Watch logs in real-time
docker-compose -f docker-compose.ultimate-evaluator.yml logs -f

# Or watch specific service
docker-compose -f docker-compose.ultimate-evaluator.yml logs -f dashboard
```

Expected logs:
```
kael-dashboard | Serving on http://0.0.0.0:80
kael-ultimate-evaluator | ✅ 7 strategies ready
kael-ultimate-evaluator | Serving on http://0.0.0.0:5001
```

### Step 4: Health Checks

```bash
# Check dashboard
curl http://localhost:3000/health

# Check evaluator API
curl http://localhost:5001/health

# Check database
docker exec kael-timescaledb pg_isready -U postgres
```

## Dashboard Features

### 1. Portfolio Overview
- **Current Balance**: Real-time balance with ROI trend
- **Daily P&L**: Today's profit/loss
- **Win Rate**: Success percentage across all strategies
- **Total Trades**: Cumulative trade count

### 2. Strategy Performance Table
- **Sortable columns**: Click headers to sort by any metric
- **Color-coded win rates**:
  - 🟢 Green: ≥60% (excellent)
  - 🟡 Yellow: 50-59% (good)
  - 🔴 Red: <50% (needs improvement)
- **Real-time streak tracking**: Current consecutive wins/losses
- **Detailed metrics**: Sharpe ratio, Kelly fraction, confidence

### 3. Performance Chart
- **Multi-metric bars**: Win rate, P&L, Sharpe ratio (×10)
- **Interactive tooltips**: Detailed stats on hover
- **Strategy comparison**: Visual comparison of all strategies

### 4. Export Options
- **Excel**: Multi-sheet workbook with all data
- **PDF**: Professional report
- **CSV**: Raw trade data
- **JSON**: Structured performance data

### 5. Theme System
- **Dark Mode** (default): Eye-friendly for extended use
- **Light Mode**: High-contrast option
- **Auto-save**: Preference persisted across sessions

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose -f docker-compose.ultimate-evaluator.yml logs -f

# Dashboard only
docker logs -f kael-dashboard

# Evaluator only
docker logs -f kael-ultimate-evaluator

# Last 100 lines
docker logs --tail=100 kael-dashboard
```

### Check Container Health

```bash
# Status of all containers
docker-compose -f docker-compose.ultimate-evaluator.yml ps

# Detailed health info
docker inspect kael-dashboard | grep -A 5 Health

# Container resource usage
docker stats kael-dashboard
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.ultimate-evaluator.yml restart

# Restart dashboard only
docker-compose -f docker-compose.ultimate-evaluator.yml restart dashboard

# Restart evaluator only
docker-compose -f docker-compose.ultimate-evaluator.yml restart ultimate-evaluator
```

### Update Dashboard

```bash
# Rebuild and restart
docker-compose -f docker-compose.ultimate-evaluator.yml up -d --build dashboard

# Without cache (clean build)
docker-compose -f docker-compose.ultimate-evaluator.yml build --no-cache dashboard
docker-compose -f docker-compose.ultimate-evaluator.yml up -d dashboard
```

## Troubleshooting

### Dashboard Not Loading

**Symptoms**: Browser shows "Connection refused" or blank page

**Solutions**:
1. Check if container is running:
   ```bash
   docker ps | grep kael-dashboard
   ```

2. Check logs for errors:
   ```bash
   docker logs kael-dashboard
   ```

3. Verify port not in use:
   ```bash
   # Windows
   netstat -ano | findstr :3000

   # Linux/Mac
   lsof -i :3000
   ```

4. Restart dashboard:
   ```bash
   docker-compose -f docker-compose.ultimate-evaluator.yml restart dashboard
   ```

### API Connection Errors

**Symptoms**: Dashboard shows "Network error" or "Connection error"

**Solutions**:
1. Check evaluator is running:
   ```bash
   curl http://localhost:5001/health
   ```

2. Check evaluator logs:
   ```bash
   docker logs kael-ultimate-evaluator | tail -50
   ```

3. Verify network connectivity:
   ```bash
   docker network inspect kael_trading-network
   ```

4. Restart evaluator:
   ```bash
   docker-compose -f docker-compose.ultimate-evaluator.yml restart ultimate-evaluator
   ```

### No Data Showing

**Symptoms**: Dashboard loads but shows "No data available"

**Solutions**:
1. Check if evaluator is trading:
   ```bash
   curl http://localhost:5001/statistics
   ```

2. Verify IQ Option connection:
   ```bash
   docker logs kael-ultimate-evaluator | grep "Connected"
   ```

3. Check trading mode:
   ```bash
   docker logs kael-ultimate-evaluator | grep "Mode:"
   ```

4. Wait for strategies to find signals (may take 5-15 minutes)

### Build Failures

**Symptoms**: Docker build fails with errors

**Solutions**:
1. Clean Docker cache:
   ```bash
   docker system prune -a
   ```

2. Remove old images:
   ```bash
   docker-compose -f docker-compose.ultimate-evaluator.yml down --rmi all
   ```

3. Rebuild from scratch:
   ```bash
   docker-compose -f docker-compose.ultimate-evaluator.yml build --no-cache
   docker-compose -f docker-compose.ultimate-evaluator.yml up -d
   ```

### Port Conflicts

**Symptoms**: Error: "Port is already allocated"

**Solutions**:
1. Find process using port:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <pid> /F

   # Linux/Mac
   lsof -ti:3000 | xargs kill -9
   ```

2. Change port in docker-compose.yml:
   ```yaml
   ports:
     - "3001:80"  # Use 3001 instead of 3000
   ```

## Performance Optimization

### Resource Limits

Adjust in `docker-compose.ultimate-evaluator.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

### Cache Management

Clear browser cache for dashboard updates:
- Chrome: Ctrl+Shift+Delete
- Firefox: Ctrl+Shift+Delete
- Safari: Cmd+Option+E

### Database Optimization

```bash
# Vacuum database
docker exec kael-timescaledb psql -U postgres -d kael -c "VACUUM ANALYZE;"

# Check database size
docker exec kael-timescaledb psql -U postgres -d kael -c "SELECT pg_size_pretty(pg_database_size('kael'));"
```

## Security Best Practices

1. **Change Default Credentials**:
   ```bash
   # In .env file
   GRAFANA_USER=your-username
   GRAFANA_PASSWORD=strong-password
   POSTGRES_PASSWORD=strong-password
   ```

2. **Use HTTPS** (Production):
   - Add SSL certificates
   - Configure nginx for HTTPS
   - Update docker-compose ports

3. **Network Isolation**:
   - Keep services on internal network
   - Only expose necessary ports
   - Use firewall rules

4. **Regular Updates**:
   ```bash
   # Pull latest images
   docker-compose -f docker-compose.ultimate-evaluator.yml pull

   # Rebuild
   docker-compose -f docker-compose.ultimate-evaluator.yml up -d --build
   ```

## Backup & Recovery

### Backup Database

```bash
# Create backup
docker exec kael-timescaledb pg_dump -U postgres kael > backup.sql

# With timestamp
docker exec kael-timescaledb pg_dump -U postgres kael > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database

```bash
# Restore from backup
docker exec -i kael-timescaledb psql -U postgres kael < backup.sql
```

### Backup Configuration

```bash
# Backup .env and docker-compose
cp .env .env.backup
cp docker-compose.ultimate-evaluator.yml docker-compose.ultimate-evaluator.yml.backup
```

## Production Deployment

### 1. Secure Configuration

```bash
# Use strong passwords
IQOPTION_PASSWORD=<strong-password>
POSTGRES_PASSWORD=<strong-password>
GRAFANA_PASSWORD=<strong-password>

# Enable HTTPS
USE_HTTPS=true
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

### 2. Resource Planning

- **Small**: 2 CPU, 4GB RAM (up to 5 strategies)
- **Medium**: 4 CPU, 8GB RAM (up to 10 strategies)
- **Large**: 8 CPU, 16GB RAM (10+ strategies)

### 3. Monitoring Setup

- Set up log aggregation (ELK stack)
- Configure alerts (Prometheus Alertmanager)
- Monitor resource usage (Grafana dashboards)

### 4. High Availability

- Use Docker Swarm or Kubernetes
- Configure load balancing
- Set up database replication

## Maintenance Schedule

### Daily
- Check dashboard accessibility
- Verify trading activity
- Review error logs

### Weekly
- Review performance metrics
- Export and analyze data
- Check disk space

### Monthly
- Update Docker images
- Backup database
- Review and optimize strategies

## Support & Documentation

### Additional Resources
- Ultimate Strategy Evaluator docs
- Dashboard README: `dashboard-ui-react/README.md`
- Docker Compose reference: docker-compose.ultimate-evaluator.yml

### Getting Help
1. Check this guide
2. Review logs: `docker logs kael-dashboard`
3. Check GitHub issues
4. Contact support team

---

**Document Version**: 1.0.0
**Last Updated**: 2025-01-28
**Maintained By**: KAEL Development Team
