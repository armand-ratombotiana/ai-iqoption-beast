# KAEL Trading Bot - Complete Dockerized Monitoring Stack

## 🚀 Overview

You now have a **complete production-ready trading bot** with comprehensive monitoring and visualization capabilities!

## 📦 What's Included

### 1. Trading Bot Services
- **KAEL Parallel Trading Bot** - Multi-instrument binary options trader
  - Advanced TA-Lib strategies (RSI, MACD, Bollinger, Stochastic, etc.)
  - Fictitious $100 balance tracking
  - Risk management with 3 profiles (Conservative/Moderate/Aggressive)
  - Real-time strategy performance tracking

- **TimescaleDB** - Time-series database for trade history
  - Unlimited historical data
  - SQL queries for analysis
  - Automatic data retention

### 2. Monitoring Stack
- **Prometheus** - Metrics collection and storage
  - 15+ custom trading metrics
  - 30-day retention period
  - 10-second scrape interval

- **Grafana** - Beautiful dashboards and visualization
  - Pre-built KAEL dashboard
  - Real-time charts and graphs
  - Customizable panels

- **Postgres Exporter** - Database performance metrics
  - Connection pool monitoring
  - Query performance
  - Database health

### 3. Dashboards
- **Flask Dashboard** (Port 5001) - Primary real-time dashboard
  - Auto-refresh every 10 seconds
  - Strategy performance comparison
  - Time period filtering (1h, 24h, 7d, all time)
  - Control buttons (Pause/Resume/Stop)

- **Grafana** (Port 3000) - Historical analysis
  - Balance tracking over time
  - Win rate trends
  - Strategy comparison charts
  - Performance metrics

## 🎯 Quick Start

### Start Everything
```bash
docker-compose -f docker-compose.parallel.yml up -d
```

### Access Dashboards
| Dashboard | URL | Login |
|-----------|-----|-------|
| **Main Dashboard** | http://localhost:5001/dashboard | N/A |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | N/A |

### View Logs
```bash
# Trading bot logs
docker logs -f kael-parallel-trading-bot

# All services status
docker-compose -f docker-compose.parallel.yml ps
```

### Stop Everything
```bash
docker-compose -f docker-compose.parallel.yml down
```

## 📊 Available Metrics

### Account Metrics
- `kael_account_balance` - Current balance ($100 fictitious)
- `kael_daily_pnl` - Daily profit/loss
- `kael_roi_percent` - Return on investment

### Trading Metrics
- `kael_total_trades` - Total executions
- `kael_wins` / `kael_losses` - Win/loss counts
- `kael_win_rate` - Current win percentage
- `kael_active_trades` - Open positions

### Strategy Metrics (per strategy)
- `kael_strategy_win_rate{strategy="..."}` - Win rate per strategy
- `kael_strategy_trades{strategy="..."}` - Trades per strategy
- `kael_strategy_profit{strategy="..."}` - Profit per strategy

### Performance Metrics
- `kael_trade_execution_time_ms` - Execution speed
- `kael_api_response_time_ms` - API latency

### Risk Metrics
- `kael_max_drawdown` - Maximum loss from peak
- `kael_current_streak` - Win/loss streak
- `kael_risk_budget_remaining` - Daily risk budget left

## 🔌 REST API Endpoints

### Health & Metrics
```bash
GET /health              # Bot health check
GET /metrics             # Prometheus metrics
GET /performance         # Detailed performance data
GET /statistics          # Trading statistics
```

### Data Access
```bash
GET /recent_trades?limit=10               # Last N trades
GET /active_trades                        # Currently open
GET /strategy_stats?hours=24              # Strategy performance
GET /config                               # Bot configuration
GET /strategy_info                        # Enabled strategies
```

### Control
```bash
POST /pause              # Pause trading
POST /resume             # Resume trading
POST /stop               # Shutdown bot
```

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Docker Network                      │
│  ┌────────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ Trading Bot    │  │ TimescaleDB│  │ Prometheus │ │
│  │   Port 5001    │  │ Port 5432  │  │ Port 9090  │ │
│  └────────┬───────┘  └─────┬──────┘  └─────┬──────┘ │
│           │                 │                │        │
│  ┌────────┴────────┐  ┌─────┴──────┐  ┌─────┴──────┐ │
│  │   Dashboard     │  │  Postgres  │  │  Grafana   │ │
│  │  (Built-in)     │  │  Exporter  │  │ Port 3000  │ │
│  └─────────────────┘  └────────────┘  └────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
KAEL/
├── autonomous_parallel_trading_bot.py  # Main bot
├── docker-compose.parallel.yml         # Complete stack
├── Dockerfile.parallel                 # Bot container
├── requirements.txt                    # Python deps
│
├── monitoring/
│   ├── prometheus.yml                  # Metrics config
│   └── grafana-dashboard.json          # Dashboard config
│
├── strategies/
│   ├── advanced_strategies.py          # TA-Lib strategies
│   ├── strategy_config.py              # Risk profiles
│   └── strategy_integrator.py          # Strategy engine
│
├── database/
│   ├── db_manager.py                   # Database layer
│   ├── trade_logger.py                 # Trade recording
│   └── schema.sql                      # Database schema
│
├── dashboard-ui/                       # Angular dashboard (optional)
│   └── src/...
│
└── logs/                               # Application logs
```

## 🎨 Features

### Advanced Strategies
1. **RSI Divergence** - Detects price/RSI divergences
2. **MACD Momentum** - Trend following with MACD
3. **Bollinger + RSI** - Mean reversion combo
4. **Stochastic Oscillator** - Overbought/oversold detection
5. **Support/Resistance** - Price level analysis
6. **Moving Average Cross** - Trend identification
7. **Momentum Breakout** - Volatility breakouts

### Risk Management
- **3 Risk Profiles**: Conservative (0.70 conf) / Moderate (0.78 conf) / Aggressive (0.65 conf)
- **Min Confluence**: 2+ strategies must agree
- **Max Daily Loss**: $8 stop-loss
- **Position Sizing**: $1-$2 per trade
- **Max Concurrent**: 2 simultaneous trades

### Monitoring Features
- **Real-time Updates**: 10-second auto-refresh
- **Historical Analysis**: 30 days of metrics in Prometheus
- **Strategy Comparison**: Filter by time period (1h/24h/7d/all)
- **Performance Tracking**: Win rate, P&L, streaks
- **Alert Ready**: Grafana alerting for critical metrics

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password

# Trading Mode
TRADING_MODE=demo  # or 'live'

# Optional - Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_secure_password
```

### Risk Profile Selection
Edit `autonomous_parallel_trading_bot.py`:
```python
# Line ~1547
risk_profile = 'moderate'  # or 'conservative' / 'aggressive'
```

## 📈 Monitoring Best Practices

### Critical Alerts to Set Up
1. **Balance Drop**: Alert if balance < $90
2. **Win Rate**: Alert if < 45%
3. **Daily Loss**: Alert if > $8
4. **Execution Time**: Alert if > 5000ms

### PromQL Queries for Alerts
```promql
# Balance alert
kael_account_balance < 90

# Win rate alert
kael_win_rate < 45

# Risk budget alert
kael_risk_budget_remaining < 2

# Loss streak alert
kael_current_streak < -3
```

## 🐛 Troubleshooting

### Bot not starting
```bash
# Check logs
docker logs kael-parallel-trading-bot

# Check all services
docker-compose -f docker-compose.parallel.yml ps

# Rebuild
docker-compose -f docker-compose.parallel.yml up -d --build
```

### No metrics in Prometheus
```bash
# Test metrics endpoint
curl http://localhost:5001/metrics

# Check Prometheus targets
# Visit: http://localhost:9090/targets
```

### Grafana shows "No Data"
1. Verify Prometheus data source configured
2. Check if bot is running and trading
3. Verify network connectivity between containers

## 🚦 Port Reference

| Service | Port | Purpose |
|---------|------|---------|
| Trading Bot | 5001 | Dashboard & API |
| TimescaleDB | 5432 | Database |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Visualization |
| Postgres Exporter | 9187 | DB Metrics |

## 📝 Documentation

- **Full Monitoring Guide**: [MONITORING_STACK.md](MONITORING_STACK.md)
- **Strategy Details**: `strategies/advanced_strategies.py`
- **API Reference**: `GET /health` for endpoints

## 🎯 Next Steps

1. **Start the stack**: `docker-compose -f docker-compose.parallel.yml up -d`
2. **Open dashboard**: http://localhost:5001/dashboard
3. **Watch it trade**: Monitor real-time metrics
4. **Configure Grafana**: http://localhost:3000
5. **Set up alerts**: Configure Grafana alerting for critical metrics
6. **Analyze performance**: Use strategy comparison to find best performers

## ✨ Success Metrics

Your bot is healthy when:
- ✅ Win rate > 50%
- ✅ Daily P&L positive
- ✅ Execution time < 500ms
- ✅ All strategies enabled and trading
- ✅ No database errors in logs

## 🔐 Security Notes

1. **Change default passwords** in .env file
2. **Don't expose ports** except 3000 (Grafana) externally
3. **Use HTTPS** in production with reverse proxy
4. **Backup data** regularly (database and Prometheus volumes)
5. **Monitor logs** for suspicious activity

## 📊 Performance Expectations

With $100 fictitious balance:
- **Target Win Rate**: 55-60%
- **Daily Target**: +$2-5 (2-5% ROI)
- **Max Drawdown**: < 10% ($10)
- **Trades per Day**: 10-50 (depending on market conditions)
- **Average Trade**: $1-2 position size

---

**You're all set!** 🎉

Start your trading bot and access the dashboard at:
👉 **http://localhost:5001/dashboard**

Monitor performance in Grafana:
👉 **http://localhost:3000**

Happy trading! 📈🤖💰
