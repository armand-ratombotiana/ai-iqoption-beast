# KAEL Trading Bot - Complete Dashboard & Monitoring Setup

## Overview

Your KAEL trading bot now has **6 integrated services** providing comprehensive monitoring and visualization:

1. **Trading Bot** - Core trading engine with Flask API
2. **TimescaleDB** - Time-series PostgreSQL database
3. **Prometheus** - Metrics collection and storage
4. **Grafana** - Advanced metrics visualization
5. **Postgres Exporter** - Database performance metrics
6. **Angular Dashboard UI** - Modern web dashboard

---

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Angular Dashboard** | http://localhost:4200 | Modern Angular UI dashboard |
| **Flask API** | http://localhost:5001/dashboard | Original HTML dashboard |
| **Grafana** | http://localhost:3000 | Advanced metrics & visualization |
| **Prometheus** | http://localhost:9090 | Metrics query & exploration |
| **API Endpoints** | http://localhost:5001/api/* | REST API |

---

## 🎯 Grafana Configuration

Grafana is now **auto-configured** with:

### ✅ Pre-configured Prometheus Data Source
- **Name**: Prometheus
- **URL**: http://prometheus:9090
- **Scrape Interval**: 10s
- **No manual configuration needed!**

### ✅ Pre-loaded KAEL Dashboard
The dashboard includes **9 panels**:

1. **Account Balance ($)** - Real-time balance tracking
2. **Daily P&L ($)** - Profit/Loss over time
3. **Win Rate (%)** - Success rate gauge
4. **Total Trades** - Trade counter
5. **Active Trades** - Current active positions
6. **Wins vs Losses** - Win/Loss comparison
7. **Strategy Performance** - Strategy-by-strategy breakdown
8. **Trade Execution Time (ms)** - Performance metrics
9. **API Response Time (ms)** - API latency

### 📊 Access Grafana Dashboard

1. **Login**: http://localhost:3000
   - Username: `admin`
   - Password: `admin` (you'll be prompted to change this)

2. **View Dashboard**:
   - Click "Dashboards" in left sidebar
   - Look for "KAEL Trading Bot" dashboard
   - Dashboard auto-loads with live data from Prometheus

---

## 📈 Prometheus Metrics

The trading bot exposes **15+ custom metrics** at `/metrics`:

### Account Metrics
```promql
kael_account_balance              # Current balance ($)
kael_daily_pnl                    # Daily profit/loss ($)
kael_roi_percent                  # Return on investment (%)
```

### Trading Metrics
```promql
kael_total_trades_total           # Total trades executed
kael_wins_total                   # Total winning trades
kael_losses_total                 # Total losing trades
kael_win_rate                     # Current win rate (%)
kael_active_trades                # Currently active trades
```

### Strategy Metrics (per strategy)
```promql
kael_strategy_win_rate{strategy="RSI"}       # Win rate by strategy
kael_strategy_trades_total{strategy="MACD"}  # Trades by strategy
kael_strategy_profit{strategy="Bollinger"}   # Profit by strategy
```

### Performance Metrics
```promql
kael_trade_execution_time_ms      # Trade execution latency
kael_api_response_time_ms         # API response latency
```

### Risk Metrics
```promql
kael_max_drawdown                 # Maximum drawdown (%)
kael_current_streak               # Win/loss streak
kael_risk_budget_remaining        # Remaining daily risk budget ($)
```

---

## 🔍 Example Prometheus Queries

Test these queries in Prometheus (http://localhost:9090):

```promql
# Current balance
kael_account_balance

# Win rate over last hour
rate(kael_wins_total[1h]) / rate(kael_total_trades_total[1h]) * 100

# Total profit from all strategies
sum(kael_strategy_profit)

# Average execution time
rate(kael_trade_execution_time_ms_sum[5m]) / rate(kael_trade_execution_time_ms_count[5m])

# Trades per minute
rate(kael_total_trades_total[1m]) * 60
```

---

## 🎨 Angular Dashboard Features

The new Angular dashboard provides:

### Modern UI Components
- Real-time data visualization
- Auto-refresh every 10 seconds
- Responsive design (mobile-friendly)
- Material Design components

### Integrated Views
- **Trading Dashboard** - Main trading metrics
- **Grafana Panels** - Embedded Grafana charts
- **Prometheus Metrics** - Direct metric queries
- **API Integration** - Full REST API access

### Proxy Configuration
The nginx reverse proxy provides:
- `/api` → Flask API (port 5001)
- `/grafana` → Grafana (port 3000)
- `/prometheus` → Prometheus (port 9090)

---

## 🚀 Quick Start

### 1. Start All Services
```bash
docker-compose -f docker-compose.parallel.yml up -d
```

### 2. Verify All Containers Running
```bash
docker-compose -f docker-compose.parallel.yml ps
```

Expected output:
```
NAME                        STATUS
kael-dashboard-ui          Up
kael-grafana               Up
kael-parallel-trading-bot  Up (healthy)
kael-postgres-exporter     Up
kael-prometheus            Up
kael-timescaledb           Up
```

### 3. Access Services
- Angular Dashboard: http://localhost:4200
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

---

## 📁 Configuration Files

### Grafana Provisioning
```
monitoring/grafana/provisioning/
├── datasources/
│   └── prometheus.yml          # Auto-configured Prometheus
└── dashboards/
    ├── default.yml             # Dashboard provider config
    └── kael-dashboard.json     # Pre-built KAEL dashboard
```

### Prometheus Configuration
```
monitoring/
└── prometheus.yml              # Scraping configuration
```

### Angular Dashboard
```
dashboard-ui/
├── Dockerfile                  # Multi-stage build
├── nginx.conf                  # Reverse proxy config
└── src/                        # Angular source code
```

---

## 🛠️ Customization

### Add Custom Grafana Dashboards

1. Create dashboard in Grafana UI
2. Export JSON: Share → Export → Save to file
3. Save to `monitoring/grafana/provisioning/dashboards/`
4. Restart Grafana: `docker-compose restart grafana`

### Add Custom Prometheus Metrics

In `autonomous_parallel_trading_bot.py`:

```python
from prometheus_client import Counter, Gauge

# Define metric
custom_metric = Gauge('kael_custom_metric', 'Description')

# Update metric
custom_metric.set(value)
```

### Modify Angular Dashboard

1. Edit files in `dashboard-ui/src/app/`
2. Rebuild: `docker-compose build dashboard-ui`
3. Restart: `docker-compose up -d dashboard-ui`

---

## 📊 Monitoring Best Practices

### 1. Set Up Alerts in Grafana

Navigate to: Dashboard → Panel → Alert tab

Example alerts:
- Balance drops below $90
- Win rate below 45%
- API response time > 1000ms
- Daily loss > $50

### 2. Use Prometheus Recording Rules

Add to `prometheus.yml`:
```yaml
rule_files:
  - "rules/*.yml"

groups:
  - name: kael_rules
    interval: 1m
    rules:
      - record: kael:win_rate:1h
        expr: rate(kael_wins_total[1h]) / rate(kael_total_trades_total[1h])
```

### 3. Monitor Data Retention

- Prometheus: 30 days (configured)
- Grafana: Unlimited dashboard retention
- TimescaleDB: Configure compression policies

---

## 🐛 Troubleshooting

### Grafana Shows "No Data"

1. Check Prometheus is scraping:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

2. Verify metrics endpoint:
   ```bash
   curl http://localhost:5001/metrics
   ```

3. Check Grafana data source:
   - Grafana → Configuration → Data Sources
   - Test connection should be green

### Angular Dashboard Not Loading

1. Check container logs:
   ```bash
   docker logs kael-dashboard-ui
   ```

2. Verify nginx configuration:
   ```bash
   docker exec kael-dashboard-ui nginx -t
   ```

3. Check API connectivity:
   ```bash
   curl http://localhost:4200/api/health
   ```

### Prometheus Not Collecting Metrics

1. Check bot metrics endpoint:
   ```bash
   curl http://localhost:5001/metrics | grep kael
   ```

2. Verify Prometheus config:
   ```bash
   docker exec kael-prometheus cat /etc/prometheus/prometheus.yml
   ```

3. Reload Prometheus config:
   ```bash
   curl -X POST http://localhost:9090/-/reload
   ```

---

## 📝 Environment Variables

Add to `.env` file:

```bash
# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_secure_password

# Postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=kael

# Trading Bot
IQOPTION_EMAIL=your_email
IQOPTION_PASSWORD=your_password
TRADING_MODE=demo
```

---

## 🎯 Next Steps

1. **Customize Grafana Dashboard**
   - Add more panels for specific strategies
   - Create alert rules
   - Set up notification channels

2. **Enhance Angular Dashboard**
   - Add real-time WebSocket connection
   - Implement advanced charting (Chart.js, D3.js)
   - Add trade execution controls

3. **Scale Monitoring**
   - Add more Prometheus exporters
   - Implement distributed tracing
   - Set up log aggregation (ELK stack)

4. **Security Hardening**
   - Change default Grafana credentials
   - Set up HTTPS/TLS
   - Implement authentication middleware

---

## 📚 Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **PromQL Cheat Sheet**: https://promlabs.com/promql-cheat-sheet/
- **Angular Documentation**: https://angular.io/docs

---

## ✅ Success Checklist

- [ ] All 6 containers running (`docker-compose ps`)
- [ ] Angular dashboard accessible (http://localhost:4200)
- [ ] Grafana dashboard loaded (http://localhost:3000)
- [ ] Prometheus scraping bot (http://localhost:9090/targets)
- [ ] Metrics endpoint responding (curl http://localhost:5001/metrics)
- [ ] Trading bot actively trading (check logs)
- [ ] Balance tracking correctly ($100 fictitious)
- [ ] Strategy metrics populating in Grafana

---

**Your complete monitoring stack is ready! 🎉**

All services are integrated and configured to work together seamlessly. The trading bot exports metrics to Prometheus, Grafana visualizes them with pre-built dashboards, and the Angular UI provides a modern interface to everything.
