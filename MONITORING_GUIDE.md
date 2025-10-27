# 🚀 2-Hour Live Monitoring Protocol - COMPLETE GUIDE

## ⚠️ STEP 0: Start Docker Desktop (CRITICAL!)

**Before running ANY commands:**

1. **Open Docker Desktop** (click Docker icon in taskbar/applications)
2. **Wait for green icon** - means Docker is ready
3. **Verify**:
   ```bash
   docker info
   ```
   Should show Docker info, NOT an error

---

## 🎯 Quick Start - Three Options

### Option 1: Fully Automated (Recommended) ⭐

```bash
python run_monitor_adjust.py
```

**Does everything automatically:**
- ✅ Checks Docker
- ✅ Builds & starts containers
- ✅ Monitors for 5 minutes
- ✅ Analyzes performance
- ✅ Suggests adjustments
- ✅ Applies changes & restarts
- ✅ Repeats cycle

### Option 2: Windows Easy Start

```bash
quick_start.bat
```

Then monitor with:
```bash
python monitor_dashboard.py
```

### Option 3: Manual Control

```bash
# Build and start
docker-compose -f docker-compose.parallel.yml build
docker-compose -f docker-compose.parallel.yml up -d

# Monitor
python monitor_dashboard.py

# Or view logs
docker-compose -f docker-compose.parallel.yml logs -f
```

---

## 📊 What to Monitor (Every 5-10 Minutes)

### Check These Metrics:

```bash
curl -s http://localhost:5001/statistics | python -m json.tool
```

**Key Metrics:**
- **Trades Today**: Should increase every 5-10 min
- **Win Rate**: Target 55%+
- **Daily P&L**: Should be positive or breakeven
- **Active Instruments**: Should show 2-3 trading
- **Balance**: Monitor for significant drops

### Quick Health Check:

```bash
# Is it running?
docker-compose -f docker-compose.parallel.yml ps

# Is it healthy?
curl http://localhost:5001/health

# Recent trades?
curl -s http://localhost:5001/recent_trades?limit=10 | python -m json.tool
```

---

## 🎛️ Adjustment Guidelines

### Scenario 1: NO TRADES (10+ minutes, 0 trades)

**Problem**: AI confidence too high or not enough instruments

**Fix** - Edit `.env`:
```bash
MIN_AI_CONFIDENCE=50  # Lower from 60
MAX_CONCURRENT_INSTRUMENTS=5  # Increase from 3
MAX_INSTRUMENTS_TO_MONITOR=30  # Increase from 20
```

**Restart**:
```bash
docker-compose -f docker-compose.parallel.yml restart
```

### Scenario 2: LOW WIN RATE (<50%)

**Problem**: Taking too many risky trades

**Fix** - Edit `.env`:
```bash
MIN_AI_CONFIDENCE=70  # Increase from 60
MIN_PAYOUT_RATIO=0.70  # Increase from 0.65
SAFETY_MARGIN_WIN_RATE=0.05  # Increase from 0.02
```

### Scenario 3: LOSING MONEY

**Problem**: Risk too high or poor strategy

**Fix** - Edit `.env`:
```bash
MIN_AI_CONFIDENCE=75
BASE_TRADE_AMOUNT=0.5  # Reduce from 1.0
MAX_TRADE_AMOUNT=1.0  # Reduce from 10.0
MAX_DAILY_LOSS=10  # Reduce from 50
ENABLE_KELLY_SIZING=false
```

### Scenario 4: HIGH WIN RATE (>65%)

**Problem**: Being too conservative, missing profits

**Fix** - Edit `.env`:
```bash
MIN_AI_CONFIDENCE=55  # Decrease from 60
BASE_TRADE_AMOUNT=2.0  # Increase from 1.0
MAX_TRADE_AMOUNT=5.0  # Increase from 10.0
MAX_CONCURRENT_INSTRUMENTS=5  # Increase from 3
```

### Scenario 5: TIMING ISSUES (Queue delays)

**Problem**: Too many parallel executions

**Fix** - Edit `.env`:
```bash
MAX_CONCURRENT_INSTRUMENTS=2  # Reduce from 3
MAX_PARALLEL_EXECUTIONS=2  # Reduce from 3
API_MIN_INTERVAL=0.5  # Increase from 0.3
```

---

## 📈 Performance Targets

### ✅ Good Performance
- **Trades/10min**: 2-4 trades
- **Win Rate**: 55-60%
- **Execution Time**: <3 seconds
- **Daily P&L**: Positive
- **No errors**: Clean logs

### ⭐ Excellent Performance
- **Trades/10min**: 4-6 trades
- **Win Rate**: 60-70%
- **Execution Time**: <2 seconds
- **Daily P&L**: +$5/hour
- **Smooth operation**: No issues

### 🚨 Poor Performance (Needs Adjustment)
- **Trades/10min**: 0-1 trades OR >10 trades
- **Win Rate**: <50%
- **Execution Time**: >5 seconds
- **Daily P&L**: Negative
- **Errors**: Frequent in logs

---

## 🔄 2-Hour Monitoring Workflow

### Cycle 1: 0-10 minutes (Baseline)
1. Start containers
2. Verify health
3. Monitor activity
4. Record metrics:
   - Trades: _____
   - Win Rate: _____%
   - P&L: $_____
   - Issues: _____

### Cycle 2: 10-20 minutes (Observation)
1. Continue monitoring
2. Look for patterns
3. Identify issues
4. Record metrics

### Cycle 3: 20-30 minutes (First Adjustment)
1. Analyze Cycle 1 & 2
2. Identify ONE problem to fix
3. Apply adjustment
4. Restart bot
5. Monitor changes

### Cycle 4-12: Repeat (30-120 minutes)
1. Monitor 10 minutes
2. Analyze results
3. Adjust if needed
4. Document changes

---

## 🛠️ Common Issues & Solutions

### Container Won't Start
```bash
# Check Docker
docker info

# Check logs
docker-compose -f docker-compose.parallel.yml logs

# Rebuild
docker-compose -f docker-compose.parallel.yml down
docker-compose -f docker-compose.parallel.yml build --no-cache
docker-compose -f docker-compose.parallel.yml up -d
```

### API Not Responding
```bash
# Wait 30 seconds after start
timeout 30

# Check container
docker-compose -f docker-compose.parallel.yml ps

# Check logs for errors
docker-compose -f docker-compose.parallel.yml logs --tail=100 parallel-trading-bot | grep -i error
```

### No Trades Executing
```bash
# Check market hours (Forex closed weekends)
# Check balance
curl http://localhost:5001/statistics

# Lower confidence
# Edit .env: MIN_AI_CONFIDENCE=50
docker-compose -f docker-compose.parallel.yml restart
```

### Too Many Losses
```bash
# Increase confidence
# Edit .env: MIN_AI_CONFIDENCE=75
# Reduce trade amount
# Edit .env: BASE_TRADE_AMOUNT=0.5
docker-compose -f docker-compose.parallel.yml restart
```

---

## 📝 Monitoring Checklist

### Every 5 Minutes:
- [ ] Container running
- [ ] Health API responding
- [ ] New trades executing
- [ ] Win rate acceptable
- [ ] No critical errors in logs

### Every 10 Minutes:
- [ ] Calculate P&L
- [ ] Check execution speed
- [ ] Review strategy breakdown
- [ ] Verify balance stability
- [ ] Look for patterns

### Every 30 Minutes:
- [ ] Analyze overall performance
- [ ] Consider adjustments
- [ ] Document observations
- [ ] Update settings if needed

---

## 💡 Pro Tips

1. **Start Conservative**: Low amounts, high confidence
2. **One Change at a Time**: Don't adjust everything at once
3. **Give It Time**: Wait 10 minutes after each change
4. **Document Everything**: Track what works
5. **Weekend = Testing**: Markets closed, perfect for infrastructure testing
6. **Demo First**: Always test in demo mode
7. **Set Limits**: Use MAX_DAILY_LOSS to protect capital

---

## 🎯 Success Criteria (After 2 Hours)

- [ ] Bot runs stable (no crashes)
- [ ] 20+ trades executed
- [ ] Win rate >55%
- [ ] Positive or breakeven P&L
- [ ] <3 second execution
- [ ] Settings optimized
- [ ] System understood

---

## 📞 Quick Command Reference

```bash
# Start
docker-compose -f docker-compose.parallel.yml up -d

# Stop
docker-compose -f docker-compose.parallel.yml down

# Restart
docker-compose -f docker-compose.parallel.yml restart

# Logs (follow)
docker-compose -f docker-compose.parallel.yml logs -f

# Status
docker-compose -f docker-compose.parallel.yml ps

# Statistics
curl -s http://localhost:5001/statistics | python -m json.tool

# Health
curl http://localhost:5001/health

# Recent trades
curl -s http://localhost:5001/recent_trades?limit=20 | python -m json.tool

# Monitor dashboard
python monitor_dashboard.py

# Automated monitoring
python run_monitor_adjust.py
```

---

## 🚀 Ready to Start!

1. **Start Docker Desktop** ← CRITICAL!
2. Run: `python run_monitor_adjust.py`
3. Follow prompts and monitor
4. Adjust as needed
5. Repeat for 2 hours

**Good luck with your trading! 📈💰**
