# PRE-FLIGHT CHECKLIST FOR $100 LIVE TRADING

## 🔴 CRITICAL - BEFORE GOING LIVE

### Step 1: Demo Testing (2-3 DAYS MINIMUM)
- [ ] Run bot on demo mode for at least 2-3 days
- [ ] Achieve minimum 60% win rate
- [ ] Verify ZERO "buy late" errors
- [ ] Confirm at least 30-50 successful trades
- [ ] Verify database logging is working
- [ ] Check average execution time < 5 seconds
- [ ] Ensure balance is trending upward

### Step 2: Configuration Verification
- [ ] Open `.env` file and verify:
  - [ ] `TRADING_MODE=live` ⚠️ **CRITICAL**
  - [ ] `BASE_TRADE_AMOUNT=1.0`
  - [ ] `MAX_TRADE_AMOUNT=2.0`
  - [ ] `MAX_DAILY_LOSS=5`
  - [ ] `MAX_DAILY_PROFIT=20`
  - [ ] `MIN_BALANCE=80`
  - [ ] `MAX_CONCURRENT_INSTRUMENTS=2`
  - [ ] `MIN_AI_CONFIDENCE=70`
  - [ ] `MIN_PAYOUT_RATIO=0.75`
  - [ ] `MAX_TRADES_PER_DAY=30`

### Step 3: IQ Option Account Setup
- [ ] Login to IQ Option website
- [ ] Verify account balance = $100.00
- [ ] Check trading history is empty (or mark starting point)
- [ ] Test credentials work (demo login first)
- [ ] Understand how to manually stop trading if needed
- [ ] Know where to see active trades on IQ Option dashboard

### Step 4: Monitoring Setup
- [ ] Bookmark `http://localhost:5001/statistics` for real-time monitoring
- [ ] Set up phone/email alerts for critical balance changes
- [ ] Have IQ Option mobile app installed for monitoring
- [ ] Calendar reminders to check bot every 2 hours
- [ ] Know how to stop the bot (`docker-compose down`)

### Step 5: Emergency Procedures
- [ ] **STOP COMMAND**: `docker-compose -f docker-compose.parallel.yml down`
- [ ] Know how to check logs: `docker logs kael-parallel-trading-bot`
- [ ] Have backup plan if internet connection drops
- [ ] Know how to manually close open positions on IQ Option
- [ ] Understand the hard stop rules (3 losses, -$5 daily loss)

## ⚡ DAY 1 LAUNCH CHECKLIST

### Morning (Before Market Open)
- [ ] **Double-check TRADING_MODE=live in .env** ⚠️
- [ ] Restart container: `docker-compose -f docker-compose.parallel.yml down && docker-compose -f docker-compose.parallel.yml up -d`
- [ ] Check logs show "Mode: LIVE" (not demo)
- [ ] Verify starting balance in logs matches $100
- [ ] Check database logging is enabled
- [ ] Verify all configuration parameters loaded correctly
- [ ] Review [REAL_MONEY_STRATEGY_$100.md](REAL_MONEY_STRATEGY_$100.md)

### First Hour
- [ ] Monitor EVERY trade manually
- [ ] Verify trades appear on IQ Option dashboard
- [ ] Check execution times are < 5 seconds
- [ ] Confirm NO "buy late" errors
- [ ] Watch balance changes match expectations
- [ ] Verify profit calculations are correct

### First 5 Trades
- [ ] Review each trade result
- [ ] Verify database is logging correctly
- [ ] Check win rate is ≥ 50%
- [ ] Ensure no execution errors
- [ ] If 3 losses in a row → STOP and review

### End of Day 1
- [ ] Review `/statistics` endpoint
- [ ] Check total trades executed
- [ ] Calculate actual win rate
- [ ] Review database for any issues
- [ ] Verify daily P&L
- [ ] If profitable → continue
- [ ] If loss > $5 → STOP and analyze

## 📋 DAILY MONITORING CHECKLIST

### Every 2 Hours
- [ ] Check `/statistics` for current balance
- [ ] Verify win rate is acceptable (≥55%)
- [ ] Look for any error patterns in logs
- [ ] Check connection is stable
- [ ] Ensure trades are executing

### End of Each Day
- [ ] Review all trades in database
- [ ] Calculate daily P&L
- [ ] Update tracking spreadsheet
- [ ] Adjust parameters if needed
- [ ] Plan next day if approaching limits

## 🚨 STOP TRADING IF

### Immediate Stop (No exceptions)
- [ ] Balance drops below $80 (-20%)
- [ ] Daily loss reaches -$5
- [ ] 3 consecutive losses
- [ ] "Buy late" errors start appearing
- [ ] Connection issues detected
- [ ] Unexpected behavior in trades
- [ ] Win rate drops below 40%

### Review & Restart
- [ ] Analyze what went wrong
- [ ] Check logs for errors
- [ ] Review database trades
- [ ] Adjust parameters if needed
- [ ] Test on demo again
- [ ] Resume only when issue is understood

## 📊 SUCCESS METRICS

### Day 1 Goals
- Minimum 5 trades
- Win rate ≥ 55%
- Zero "buy late" errors
- Balance ≥ $100 (break-even or positive)

### Week 1 Goals
- Total trades: 50-100
- Win rate: ≥ 60%
- Weekly profit: +$5 to +$15
- Max drawdown: < 10%
- Zero critical errors

## 🎯 PROFITABILITY TARGETS

### Conservative (60% win rate)
- **Daily**: +$1-2 (1-2%)
- **Weekly**: +$5-10 (5-10%)
- **Monthly**: +$20-40 (20-40%)

### Moderate (70% win rate)
- **Daily**: +$3-5 (3-5%)
- **Weekly**: +$15-20 (15-20%)
- **Monthly**: +$60-80 (60-80%)

### Optimistic (80% win rate)
- **Daily**: +$5-8 (5-8%)
- **Weekly**: +$25-35 (25-35%)
- **Monthly**: +$100-140 (100-140%)

## ⚠️ FINAL WARNINGS

1. **NEVER** go live without 2-3 days of successful demo trading
2. **NEVER** override the hard stop rules
3. **NEVER** increase trade size after losses
4. **ALWAYS** monitor the first day closely
5. **ALWAYS** have the stop command ready
6. **START SMALL** - $1 trades until proven successful

---

## ✅ READY TO GO LIVE?

**Only check YES if ALL boxes above are checked:**

- [ ] Demo testing complete (2-3 days, 60%+ win rate)
- [ ] All configuration verified
- [ ] IQ Option account ready ($100 balance)
- [ ] Monitoring system in place
- [ ] Emergency procedures understood
- [ ] Understand all risk limits
- [ ] Read [REAL_MONEY_STRATEGY_$100.md](REAL_MONEY_STRATEGY_$100.md) completely
- [ ] Mentally prepared for potential losses
- [ ] Will follow the rules no matter what

**If ALL boxes are checked, you may proceed to live trading.**

**REMEMBER**: Capital preservation is MORE IMPORTANT than profits!

---

## 📞 QUICK REFERENCE

### Stop Bot
```bash
docker-compose -f docker-compose.parallel.yml down
```

### Check Stats
```bash
curl http://localhost:5001/statistics | python -m json.tool
```

### View Logs
```bash
docker logs kael-parallel-trading-bot --tail 50
```

### Restart Bot
```bash
docker-compose -f docker-compose.parallel.yml restart
```

### Full Restart (reload .env)
```bash
docker-compose -f docker-compose.parallel.yml down
docker-compose -f docker-compose.parallel.yml up -d
```
