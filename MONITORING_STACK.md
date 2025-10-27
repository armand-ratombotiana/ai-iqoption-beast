# KAEL Trading Bot - Complete Monitoring Stack

## Overview

The KAEL trading bot includes a comprehensive monitoring stack with:
- **Prometheus** - Metrics collection and time-series database
- **Grafana** - Visualization dashboards and alerting
- **Flask API** - Built-in dashboard and REST endpoints
- **TimescaleDB** - Trade history and performance data
- **Postgres Exporter** - Database performance metrics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    KAEL Trading Bot                          │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Flask API    │  │ Prometheus   │  │  TimescaleDB   │  │
│  │  Port: 5001   │  │  Metrics     │  │   Port: 5432   │  │
│  └───────┬───────┘  └──────────────┘  └────────┬────────┘  │
│          │                                       │           │
└──────────┼───────────────────────────────────────┼───────────┘
           │                                       │
           ▼                                       ▼
    ┌──────────────┐                    ┌─────────────────┐
    │  Prometheus  │◄───────────────────│ Postgres        │
    │  Port: 9090  │                    │ Exporter        │
    └──────┬───────┘                    │ Port: 9187      │
           │                            └─────────────────┘
           ▼
    ┌──────────────┐
    │   Grafana    │
    │  Port: 3000  │
    └──────────────┘
```

## Quick Start

### 1. Start the Complete Stack

```bash
docker-compose -f docker-compose.parallel.yml up -d
```

This starts:
- ✅ Trading Bot (port 5001)
- ✅ TimescaleDB (port 5432)
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3000)
- ✅ Postgres Exporter (port 9187)

### 2. Access Dashboards

| Service | URL | Default Login |
|---------|-----|---------------|
| **Flask Dashboard** | http://localhost:5001/dashboard | N/A |
| **Prometheus** | http://localhost:9090 | N/A |
| **Grafana** | http://localhost:3000 | admin/admin |
| **API Docs** | http://localhost:5001/health | N/A |

### 3. Configure Grafana

1. Open http://localhost:3000
2. Login with `admin/admin` (change password on first login)
3. Add Prometheus data source:
   - Go to **Configuration > Data Sources**
   - Click **Add data source**
   - Select **Prometheus**
   - Set URL: `http://prometheus:9090`
   - Click **Save & Test**

4. Import KAEL dashboard:
   - Go to **Dashboards > Import**
   - Upload `monitoring/grafana-dashboard.json`
   - Select Prometheus data source
   - Click **Import**

## Available Metrics

### Account Metrics
- `kael_account_balance` - Current account balance ($)
- `kael_daily_pnl` - Daily profit/loss ($)
- `kael_roi_percent` - Return on investment (%)

### Trading Metrics
- `kael_total_trades` - Total trades executed (counter)
- `kael_wins` - Total winning trades (counter)
- `kael_losses` - Total losing trades (counter)
- `kael_win_rate` - Current win rate (%)
- `kael_active_trades` - Number of active trades

### Strategy Metrics (per strategy)
- `kael_strategy_win_rate{strategy="..."}` - Win rate per strategy (%)
- `kael_strategy_trades{strategy="..."}` - Trades per strategy (counter)
- `kael_strategy_profit{strategy="..."}` - Total profit per strategy ($)

### Performance Metrics
- `kael_trade_execution_time_ms` - Trade execution time histogram
- `kael_api_response_time_ms` - API response time histogram

### Risk Metrics
- `kael_max_drawdown` - Maximum drawdown (%)
- `kael_current_streak` - Win/loss streak (positive=wins, negative=losses)
- `kael_risk_budget_remaining` - Remaining daily risk budget ($)

## REST API Endpoints

### Health & Status
```bash
GET /health
# Returns: {"status": "ok", "timestamp": "..."}

GET /statistics
# Returns: Complete trading statistics

GET /performance
# Returns: Detailed performance metrics with streaks and limits
```

### Trading Data
```bash
GET /recent_trades?limit=10
# Returns: Last N trades with full details

GET /active_trades
# Returns: Currently active trades

GET /strategy_stats?hours=24
# Returns: Strategy performance (filterable by time period)
```

### Configuration
```bash
GET /config
# Returns: Current bot configuration

GET /strategy_info
# Returns: Enabled strategies and risk profile
```

### Control
```bash
POST /pause
# Pause trading (complete active trades first)

POST /resume
# Resume trading

POST /stop
# Shutdown the bot
```

### Metrics
```bash
GET /metrics
# Returns: Prometheus-format metrics
```

## Monitoring Best Practices

### 1. Real-Time Monitoring
- **Flask Dashboard**: Best for quick checks and real-time data
  - Auto-refreshes every 10 seconds
  - Shows current balance, P&L, trades
  - Strategy performance comparison with time filters

- **Grafana**: Best for historical analysis and trends
  - Customizable time ranges
  - Advanced queries and calculations
  - Alerting capabilities

### 2. Key Metrics to Watch

**Critical Alerts:**
- Balance drops below $90 (10% loss)
- Win rate falls below 45%
- Daily loss exceeds $8
- Execution time > 5 seconds

**Warning Alerts:**
- Win rate between 45-50%
- Loss streak >= 3
- Daily loss $5-$8
- Execution time > 2 seconds

### 3. Performance Optimization

Monitor these to optimize:
- **Execution time**: Should be < 500ms
- **API response time**: Should be < 200ms
- **Active trades**: Keep below max concurrent limit
- **Strategy win rates**: Disable strategies < 45% win rate

### 4. Data Retention

- **Prometheus**: 30 days of metrics
- **TimescaleDB**: Unlimited trade history
- **Logs**: 3 files × 10MB = 30MB max

## Advanced Queries (PromQL)

### Trading Performance
```promql
# Win rate over time
rate(kael_wins[5m]) / rate(kael_total_trades[5m]) * 100

# Profit per hour
rate(kael_daily_pnl[1h])

# Average execution time
histogram_quantile(0.95, kael_trade_execution_time_ms_bucket)
```

### Strategy Analysis
```promql
# Best performing strategy
topk(1, kael_strategy_profit)

# Strategy win rate comparison
kael_strategy_win_rate

# Trades per strategy
rate(kael_strategy_trades[1h])
```

### Risk Management
```promql
# Drawdown alert
kael_max_drawdown > 10

# Risk budget alert
kael_risk_budget_remaining < 2

# Loss streak alert
kael_current_streak < -3
```

## Troubleshooting

### Prometheus can't scrape metrics
```bash
# Check if bot is running
docker ps | grep kael-parallel

# Check metrics endpoint
curl http://localhost:5001/metrics

# Check Prometheus targets
# Go to http://localhost:9090/targets
```

### Grafana shows "No Data"
```bash
# Verify Prometheus data source
# In Grafana: Configuration > Data Sources > Prometheus > Test

# Check if metrics exist in Prometheus
# Go to http://localhost:9090/graph
# Query: kael_account_balance
```

### Database connection issues
```bash
# Check TimescaleDB status
docker logs kael-timescaledb

# Test database connection
docker exec -it kael-timescaledb psql -U postgres -d kael -c "SELECT COUNT(*) FROM trades;"
```

## Monitoring Stack Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Flask API | 5001 | HTTP | Dashboard & REST API |
| Prometheus | 9090 | HTTP | Metrics & queries |
| Grafana | 3000 | HTTP | Visualization |
| TimescaleDB | 5432 | PostgreSQL | Trade history |
| Postgres Exporter | 9187 | HTTP | DB metrics |

## Security Notes

1. **Change default passwords:**
   ```bash
   # Set in .env file
   GRAFANA_USER=your_username
   GRAFANA_PASSWORD=your_secure_password
   ```

2. **Firewall configuration:**
   - Only expose port 3000 (Grafana) externally
   - Keep other ports internal to Docker network

3. **HTTPS setup** (production):
   - Use nginx reverse proxy
   - Configure SSL certificates
   - Enable authentication for all endpoints

## Backup & Recovery

### Backup Prometheus Data
```bash
docker run --rm -v kael_prometheus-data:/prometheus \
  -v $(pwd)/backups:/backup alpine \
  tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz /prometheus
```

### Backup Grafana Dashboards
```bash
docker exec kael-grafana grafana-cli admin export-dashboard > backup/dashboards.json
```

### Backup TimescaleDB
```bash
docker exec kael-timescaledb pg_dump -U postgres kael > backup/kael-$(date +%Y%m%d).sql
```

## Support & Resources

- **Prometheus Docs**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/
- **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Grafana Alerting**: https://grafana.com/docs/grafana/latest/alerting/

## Performance Tuning

### For High-Frequency Trading:
1. Reduce Prometheus scrape interval to 5s
2. Increase TimescaleDB shared_buffers
3. Enable Grafana caching
4. Use SSD storage for Docker volumes

### For Resource-Constrained Systems:
1. Increase Prometheus scrape interval to 30s
2. Reduce retention period to 7 days
3. Disable Postgres Exporter if not needed
4. Limit Grafana refresh rate

---

**Ready to monitor!** 🚀📊

Access your dashboards:
- **Main Dashboard**: http://localhost:5001/dashboard
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
