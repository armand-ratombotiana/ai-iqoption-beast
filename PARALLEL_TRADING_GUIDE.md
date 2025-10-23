# 🚀 Parallel Multi-Instrument Trading Guide

## Overview

The **Parallel Trading Bot** allows you to trade **multiple instruments simultaneously** with advanced portfolio risk management. This guide will help you set up and configure the bot for optimal performance.

---

## 🎯 Key Features

### 1. **Multi-Instrument Trading**
- Trade up to **10 instruments concurrently**
- Independent signal generation per instrument
- Per-instrument performance tracking
- Dynamic instrument selection

### 2. **Portfolio Risk Management**
- Portfolio-wide risk allocation (default: 10% of balance)
- Per-instrument risk limits (default: 2.5% per instrument)
- Correlation-aware position sizing
- Real-time balance monitoring

### 3. **Advanced Controls**
- Per-instrument trade limits
- Portfolio-wide daily/hourly limits
- Concurrent position limits
- Automatic risk rebalancing

### 4. **Performance Tracking**
- Individual instrument statistics
- Portfolio-level metrics
- Win rate per instrument
- Profit/loss tracking

---

## ⚙️ Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Basic Settings
TRADING_MODE=demo                    # 'demo' or 'live'
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password

# Parallel Trading Settings
MAX_CONCURRENT_INSTRUMENTS=5         # Max instruments trading at once (1-10)
MAX_INSTRUMENTS_TO_MONITOR=20        # Total instruments to scan (10-50)
PORTFOLIO_RISK_PERCENT=10.0          # Total portfolio risk % (5-20)
MAX_RISK_PER_INSTRUMENT=2.5          # Risk per instrument % (1-5)

# Trading Amounts
BASE_TRADE_AMOUNT=1.0                # Base trade amount in $
MAX_TRADE_AMOUNT=10.0                # Maximum trade amount in $

# Instrument Pool (comma-separated)
TRADING_ASSETS=EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,AUDJPY,EURAUD,GBPAUD,USDCHF,EURCAD,GBPCAD,AUDCAD

# Risk Limits
MAX_DAILY_LOSS=50                    # Stop trading if daily loss exceeds this
MAX_DAILY_PROFIT=100                 # Stop trading if daily profit reaches this
MIN_BALANCE=50                       # Minimum balance to continue trading

# Per-Instrument Limits
MAX_TRADES_PER_INSTRUMENT_HOUR=10    # Max trades per instrument per hour
MIN_SECONDS_BETWEEN_TRADES=70        # Minimum seconds between trades on same instrument

# Global Limits
MAX_TRADES_PER_HOUR=50               # Total trades per hour (all instruments)
MAX_TRADES_PER_DAY=300               # Total trades per day (all instruments)

# AI Settings
MIN_AI_CONFIDENCE=65                 # Minimum AI confidence to trade (60-90)
MIN_CONSENSUS_AGREEMENT=0.7          # Minimum consensus agreement (0.6-0.9)

# Timing
INSTRUMENT_SCAN_INTERVAL=30          # Seconds between instrument scans

# Performance
MAX_WORKER_THREADS=10                # Thread pool size for parallel execution

# Monitoring
HEALTH_API_PORT=5001                 # Port for health monitoring API
```

---

## 🚀 Quick Start

### 1. **Basic Setup (5 Concurrent Instruments)**

```bash
# .env configuration
MAX_CONCURRENT_INSTRUMENTS=5
PORTFOLIO_RISK_PERCENT=10.0
MAX_RISK_PER_INSTRUMENT=2.0
BASE_TRADE_AMOUNT=1.0
```

**Run the bot:**
```bash
python3 autonomous_parallel_trading_bot.py
```

### 2. **Aggressive Setup (10 Concurrent Instruments)**

```bash
# .env configuration
MAX_CONCURRENT_INSTRUMENTS=10
PORTFOLIO_RISK_PERCENT=15.0
MAX_RISK_PER_INSTRUMENT=2.5
BASE_TRADE_AMOUNT=2.0
MAX_INSTRUMENTS_TO_MONITOR=30
```

### 3. **Conservative Setup (3 Concurrent Instruments)**

```bash
# .env configuration
MAX_CONCURRENT_INSTRUMENTS=3
PORTFOLIO_RISK_PERCENT=5.0
MAX_RISK_PER_INSTRUMENT=1.5
BASE_TRADE_AMOUNT=1.0
MIN_AI_CONFIDENCE=75
```

---

## 📊 How It Works

### Trading Cycle

1. **Scan Phase** (every 30 seconds)
   - Scans all available instruments from the pool
   - Checks which instruments are open for trading
   - Filters by portfolio constraints

2. **Analysis Phase** (parallel)
   - Generates AI signals for each instrument
   - Calculates position sizes based on confidence
   - Checks per-instrument trading rules

3. **Execution Phase** (concurrent)
   - Executes trades on multiple instruments simultaneously
   - Each instrument trades independently
   - Portfolio risk is allocated in real-time

4. **Monitoring Phase**
   - Tracks active trades per instrument
   - Updates statistics continuously
   - Releases risk allocation when trades complete

### Risk Management Flow

```
Portfolio Balance: $1000
├── Portfolio Risk Budget: $100 (10%)
│   ├── EURUSD: $25 (2.5%) - ACTIVE
│   ├── GBPUSD: $25 (2.5%) - ACTIVE
│   ├── USDJPY: $25 (2.5%) - ACTIVE
│   └── Available: $25 (2.5%)
└── Reserved: $900 (90%)
```

---

## 📈 Monitoring

### Real-Time Statistics API

Access statistics while the bot is running:

```bash
# Get current statistics
curl http://localhost:5001/statistics

# Health check
curl http://localhost:5001/health

# Stop the bot
curl -X POST http://localhost:5001/stop
```

### Statistics Output

```json
{
  "status": "running",
  "mode": "demo",
  "balance": 1050.25,
  "start_balance": 1000.00,
  "daily_profit": 75.50,
  "daily_loss": 25.25,
  "daily_net": 50.25,
  "trades_today": 45,
  "wins_today": 28,
  "losses_today": 17,
  "win_rate": 62.22,
  "active_instruments": ["EURUSD", "GBPUSD", "USDJPY"],
  "active_count": 3,
  "total_risk_allocated": 75.00,
  "instruments_traded": 8,
  "instrument_stats": [
    {
      "instrument": "EURUSD",
      "total_trades": 12,
      "wins": 8,
      "losses": 4,
      "win_rate": 66.67,
      "profit": 15.50,
      "consecutive_wins": 2,
      "is_trading": true
    }
  ]
}
```

---

## 🎛️ Configuration Strategies

### Strategy 1: High Volume Trading
**Goal:** Maximum trade frequency across many instruments

```bash
MAX_CONCURRENT_INSTRUMENTS=10
MAX_INSTRUMENTS_TO_MONITOR=30
MAX_TRADES_PER_HOUR=100
MAX_TRADES_PER_DAY=500
INSTRUMENT_SCAN_INTERVAL=20
```

### Strategy 2: Quality Over Quantity
**Goal:** Fewer, higher-confidence trades

```bash
MAX_CONCURRENT_INSTRUMENTS=3
MIN_AI_CONFIDENCE=80
MIN_CONSENSUS_AGREEMENT=0.8
MAX_TRADES_PER_INSTRUMENT_HOUR=5
```

### Strategy 3: Balanced Approach
**Goal:** Moderate risk with good diversification

```bash
MAX_CONCURRENT_INSTRUMENTS=5
PORTFOLIO_RISK_PERCENT=10.0
MAX_RISK_PER_INSTRUMENT=2.0
MIN_AI_CONFIDENCE=70
MAX_TRADES_PER_HOUR=50
```

### Strategy 4: Risk-Averse
**Goal:** Minimal risk, maximum safety

```bash
MAX_CONCURRENT_INSTRUMENTS=2
PORTFOLIO_RISK_PERCENT=5.0
MAX_RISK_PER_INSTRUMENT=1.0
MIN_AI_CONFIDENCE=85
MAX_DAILY_LOSS=20
```

---

## 📝 Log Files

The bot creates detailed logs:

```
logs/
├── parallel_bot_20250123.log       # Main log with all activities
└── parallel_trades_20250123.log    # Trade-specific log
```

### Log Format

```
[2025-01-23 12:35:10] [INFO] [MainThread] 🔍 Scanning 15 instruments...
[2025-01-23 12:35:12] [INFO] [Thread-1] 🎯 TRADE [EURUSD]: CALL $2.50 @ 75%
[2025-01-23 12:35:12] [INFO] [Thread-2] 🎯 TRADE [GBPUSD]: PUT $2.25 @ 72%
[2025-01-23 12:35:13] [INFO] [Thread-1] ✅ [EURUSD] Order placed: 12345
[2025-01-23 12:36:35] [INFO] [Thread-1] 📈 RESULT [EURUSD]: WIN
[2025-01-23 12:36:35] [INFO] [Thread-1]    P/L: +$1.87
```

---

## 🔧 Advanced Configuration

### Custom Instrument Pool

Edit the instrument pool to focus on specific markets:

```bash
# Forex majors only
TRADING_ASSETS=EURUSD,GBPUSD,USDJPY,USDCHF

# Forex + commodities
TRADING_ASSETS=EURUSD,GBPUSD,GOLD,SILVER,OIL

# High volatility pairs
TRADING_ASSETS=GBPJPY,EURJPY,AUDJPY,NZDJPY
```

### Thread Pool Optimization

Adjust based on your system:

```bash
# For powerful systems
MAX_WORKER_THREADS=20
MAX_CONCURRENT_INSTRUMENTS=10

# For limited resources
MAX_WORKER_THREADS=5
MAX_CONCURRENT_INSTRUMENTS=3
```

---

## ⚠️ Important Notes

### Risk Management

1. **Portfolio Risk**: Never allocate more than 10-15% of your balance to active trades
2. **Per-Instrument Risk**: Keep individual instrument risk at 1-3% of balance
3. **Correlation**: The bot automatically avoids trading highly correlated pairs
4. **Daily Limits**: Always set realistic daily loss limits

### Performance Tips

1. **Start Conservative**: Begin with 3-5 concurrent instruments
2. **Monitor First Hour**: Watch the first hour closely to ensure proper operation
3. **Adjust Gradually**: Increase concurrent instruments gradually
4. **Balance Scan Interval**: Lower intervals = more opportunities but higher load

### Common Issues

**Issue**: Too many instruments, not enough trades
- **Solution**: Increase `MAX_INSTRUMENTS_TO_MONITOR`

**Issue**: Portfolio risk limit reached quickly
- **Solution**: Increase `PORTFOLIO_RISK_PERCENT` or decrease `MAX_RISK_PER_INSTRUMENT`

**Issue**: Instruments not trading
- **Solution**: Lower `MIN_AI_CONFIDENCE` or check if markets are open

---

## 🎯 Best Practices

1. **Always start in DEMO mode** to test your configuration
2. **Monitor the first 30 minutes** of any new configuration
3. **Set realistic daily loss limits** (5-10% of balance)
4. **Use the health API** to monitor performance
5. **Review logs daily** to identify patterns
6. **Adjust based on results** - optimize your configuration over time

---

## 📞 Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review the statistics via the health API
3. Ensure your `.env` file is properly configured
4. Verify your IQ Option credentials are correct

---

## 🚦 Quick Reference

| Setting | Conservative | Balanced | Aggressive |
|---------|-------------|----------|------------|
| Concurrent Instruments | 2-3 | 5 | 8-10 |
| Portfolio Risk % | 5% | 10% | 15% |
| Per-Instrument Risk % | 1% | 2% | 3% |
| Min AI Confidence | 80% | 70% | 65% |
| Trades/Hour | 20 | 50 | 100 |

---

**Happy Trading! 🚀**
