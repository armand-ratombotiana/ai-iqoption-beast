# 🚀 QUICK START GUIDE
## IQOption Trading System - Get Running in 5 Minutes

---

## ⚡ Super Quick Start (Copy & Paste)

```bash
# 1. Verify Python dependencies
pip install iqoptionapi

# 2. Run demo trading (safe, no real money)
python run_trading_system.py --mode demo --max-trades 5

# 3. View logs in real-time (separate terminal)
tail -f logs/trading_*.log
```

**Done!** The system is now trading in demo mode with your account.

---

## 📋 What Just Happened?

✅ Connected to IQOption with your credentials (tombokael4@gmail.com)
✅ Switched to PRACTICE account ($9,999.35 demo balance)
✅ Scanned 3 forex pairs (EURUSD, GBPUSD, USDJPY)
✅ Generated trading signals based on price trends
✅ Executed trades in DEMO mode (simulated, no real money)
✅ Tracked profit/loss in real-time
✅ Logged all actions to `logs/` directory

---

## 🎯 Command Reference

### Demo Trading (Recommended)
```bash
# Run 5 demo trades
python run_trading_system.py --mode demo --max-trades 5

# Run 10 demo trades
python run_trading_system.py --mode demo --max-trades 10

# Run unlimited (Ctrl+C to stop)
python run_trading_system.py --mode demo
```

### Live Trading (⚠️ Real Money)
```bash
# CAREFUL - Real money trading
python run_trading_system.py --mode live --max-trades 5 --confirm

# You'll be asked: "Are you sure you want to trade with real money? (yes/no):"
# Type 'yes' to confirm
```

### View Logs
```bash
# Real-time log viewing
tail -f logs/trading_*.log

# View latest log file
ls -t logs/ | head -1 | xargs -I {} cat logs/{}

# Search for trades
grep "Trade #" logs/trading_*.log
```

---

## ⚙️ Configuration

### Current Settings (in `.env` file)
```
Account:       tombokael4@gmail.com
Mode:          PRACTICE (demo)
Risk/Trade:    2%
Max Daily Loss: 10%
Assets:        EURUSD, GBPUSD, USDJPY
Min Confidence: 60%
```

### Change Settings
```bash
# Edit configuration
nano .env

# Example changes:
RISK_PER_TRADE=0.01      # Change to 1% per trade
MIN_CONFIDENCE=70        # Require 70% confidence
TRADING_ASSETS=EURUSD    # Trade only EURUSD
```

---

## 📊 Understanding the Output

### Log Example
```
11:09:21 - Signal: EURUSD - CALL @ 71.5%
  → System found a BUY signal on EURUSD with 71.5% confidence

11:09:21 - Position size: $20.00 (confidence: 71.5%)
  → Calculated trade amount based on 2% risk

11:09:21 - [DRY RUN] Executing CALL on EURUSD for $20.00
  → Simulating trade (demo mode)

11:09:23 - ✅ WIN: +$17.00 (Streak: 1)
  → Trade won, +$17 profit

11:09:23 - Daily P/L: $-3.00
  → Net profit/loss for the day
```

### Trade Actions
- **CALL** = Buy (expect price to go UP)
- **PUT** = Sell (expect price to go DOWN)
- **HOLD** = No trade (confidence too low)

---

## 🛑 How to Stop

### Stop Running System
```bash
# Press Ctrl+C in the terminal where system is running
^C

# System will gracefully shutdown and show summary:
# - Total trades
# - Daily profit/loss
# - Win rate
```

---

## ✅ Verify System is Working

### Check Logs
```bash
cat logs/trading_*.log | grep "TRADING SYSTEM"
```

Expected output:
```
TRADING SYSTEM STARTED
TRADING SYSTEM SHUTDOWN
```

### Check Trades
```bash
cat logs/trading_*.log | grep "Trade #"
```

Expected output:
```
Trade #1 complete
Trade #2 complete
...
```

---

## 🔍 Troubleshooting

### Problem: "Connection failed"
```bash
# Check credentials in .env
cat .env | grep IQOPTION

# Should show:
# IQOPTION_EMAIL=tombokael4@gmail.com
# IQOPTION_PASSWORD=tombokael04
```

### Problem: "No signals generated"
```bash
# Lower confidence threshold
echo "MIN_CONFIDENCE=50" >> .env

# Or check if markets are open (forex trades 24/5)
```

### Problem: "Module not found"
```bash
# Install IQOption API
pip install iqoptionapi

# Verify installation
python -c "import iqoptionapi; print('OK')"
```

---

## 📈 Next Steps

### 1. Run More Demo Trades (Recommended)
```bash
# Test with 50 trades
python run_trading_system.py --mode demo --max-trades 50
```

### 2. Review Performance
```bash
# Check logs for win rate
grep "WIN\|LOSS" logs/trading_*.log | tail -20
```

### 3. Adjust Settings
```bash
# Edit .env to tune parameters
nano .env

# Try different assets, risk levels, confidence thresholds
```

### 4. Consider Live Trading (⚠️ Only After Extensive Testing)
```bash
# Start VERY small ($1-2 trades)
# Update .env:
# BASE_TRADE_AMOUNT=1.0
# MAX_TRADE_AMOUNT=2.0

# Then run:
python run_trading_system.py --mode live --max-trades 5 --confirm
```

---

## 📝 Files Overview

```
run_trading_system.py      → Main script (RUN THIS)
.env                        → Your configuration
logs/trading_*.log          → Trading logs (CHECK THESE)
README_PRODUCTION.md        → Full documentation
archive/                    → Old tests & reports
```

---

## ⚠️ Important Reminders

1. **Demo First** - Always test in demo mode extensively
2. **Start Small** - Begin with minimum amounts ($1-2)
3. **Monitor Closely** - Watch first 10-20 live trades
4. **High Risk** - Binary options can result in total loss
5. **No Guarantees** - Past performance ≠ future results

---

## 🆘 Need Help?

1. **Check Logs**
   ```bash
   tail -f logs/trading_*.log
   ```

2. **Read Full Docs**
   ```bash
   cat README_PRODUCTION.md
   ```

3. **View Test Results**
   ```bash
   cat archive/reports/FINAL_SUCCESS_REPORT.md
   ```

---

## ✅ System Status

```
✅ All 14 component tests PASSING
✅ Complete system run SUCCESSFUL
✅ 6 demo trades EXECUTED
✅ All modules OPERATIONAL
✅ Ready for use
```

---

**Last Updated:** October 6, 2025
**Status:** Production Ready
**Mode:** Demo (safe testing)

🚀 **Ready to trade! Start with demo mode above.**
