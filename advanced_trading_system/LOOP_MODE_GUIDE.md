# Loop Trading Mode - Complete Guide

## ✅ Feature Added: Automatic Trading Loop

The unified trading system now supports **continuous trading** with automatic execution every N minutes!

## How It Works

### Basic Syntax

```bash
python run_unified_trading.py --mode basic --loop
```

This will:
- Execute a trade
- Wait 5 minutes (default)
- Execute another trade
- Repeat indefinitely (until Ctrl+C)

### Loop Options

**1. Custom Interval**
```bash
# Trade every 3 minutes
python run_unified_trading.py --mode basic --loop --loop-interval 3
```

**2. Limited Iterations**
```bash
# Run exactly 10 trades then stop
python run_unified_trading.py --mode basic --loop --max-iterations 10
```

**3. Combined Options**
```bash
# Trade every 2 minutes, 5 times only
python run_unified_trading.py --mode basic --loop --loop-interval 2 --max-iterations 5
```

## Real Test Results

**Test Configuration:**
- Mode: Basic
- Pair: EURUSD-OTC
- Interval: 2 minutes
- Iterations: 2

**Results:**
```
🔄 ITERATION 1
   RSI: 60.5, Trend: uptrend
   Signal: CALL
   Result: ✅ WIN (+$0.96)

⏳ Waiting 2 minutes...

🔄 ITERATION 2
   RSI: 57.0, Trend: uptrend
   Signal: CALL
   Result: ❌ LOSS (-$1.10)

📊 Session Summary:
   Trades: 2
   Win Rate: 50.0%
   Total P/L: -$0.14
```

## Available Commands

### 1. Basic Loop (Default 5 min)
```bash
IQOPTION_EMAIL=your@email.com \
IQOPTION_PASSWORD=yourpass \
MIN_CONFIDENCE=55 \
python run_unified_trading.py --mode basic --loop
```

### 2. Fast Loop (1 minute - for testing)
```bash
python run_unified_trading.py --mode basic --loop --loop-interval 1 --max-iterations 3
```

### 3. Enhanced Mode Loop
```bash
# Execute 3 trades every 10 minutes
python run_unified_trading.py --mode enhanced --max-trades 3 --loop --loop-interval 10
```

### 4. Parallel Mode Loop
```bash
# Trade 3 pairs every 15 minutes
python run_unified_trading.py --mode parallel --pairs 3 --loop --loop-interval 15
```

### 5. Production Mode (Recommended)
```bash
# Loop every 5 minutes indefinitely
python run_unified_trading.py \
  --mode basic \
  --pair EURUSD-OTC \
  --duration 1 \
  --loop \
  --loop-interval 5
```

## Features

✅ **Automatic Trading**
- System executes trades automatically
- No manual intervention needed
- Configurable intervals

✅ **Smart Waiting**
- Shows next trade time
- Countdown timer
- Graceful interruption (Ctrl+C)

✅ **Session Tracking**
- Tracks all trades in session
- Cumulative statistics
- Win rate calculation

✅ **Error Handling**
- Continues on errors
- Logs all issues
- Doesn't crash the loop

## Use Cases

### Day Trading
```bash
# Trade EURUSD every 5 minutes during market hours
python run_unified_trading.py \
  --mode basic \
  --pair EURUSD-OTC \
  --loop \
  --loop-interval 5 \
  --max-iterations 50
```

### Night Trading (OTC)
```bash
# Trade multiple OTC pairs every 10 minutes
python run_unified_trading.py \
  --mode enhanced \
  --max-trades 3 \
  --loop \
  --loop-interval 10
```

### Scalping
```bash
# Fast 1-minute trades
python run_unified_trading.py \
  --mode basic \
  --pair EURUSD-OTC \
  --duration 1 \
  --loop \
  --loop-interval 2 \
  --max-iterations 20
```

### Long Session
```bash
# Trade every 15 minutes for 4 hours (16 trades)
python run_unified_trading.py \
  --mode basic \
  --loop \
  --loop-interval 15 \
  --max-iterations 16
```

## Loop Output

The system shows clear progress:

```
🔄 LOOP MODE: Trading every 5 minutes
   Max iterations: 10

======================================================================
🔄 ITERATION 1
======================================================================
🎯 BASIC MODE - Single Trade
🔌 Connecting to IQOption...
✅ Connected - PRACTICE - Balance: $10000.00
📊 Getting market data for EURUSD-OTC...
   Price: $1.16600
   Trend: uptrend, RSI: 60.5
💵 Position size: $1.10
📈 Executing CALL trade...
✅ Trade executed! Order ID: 13158001533
⏳ Waiting for result (1 min)...
✅ WIN! Profit: +$0.96
✅ Iteration 1 completed

⏳ Waiting 5 minutes until next trade...
   Next trade at: 19:17:00
```

## Stopping the Loop

**Graceful Stop:**
- Press `Ctrl+C` once
- System will finish current trade
- Show final summary

**Force Stop:**
- Press `Ctrl+C` twice
- Immediate termination

## Risk Management

The loop respects all risk limits:
- ✅ Max daily loss
- ✅ Max daily profit
- ✅ Max consecutive losses
- ✅ Min account balance

If any limit is hit, the system stops automatically.

## Database Storage

All loop trades are stored in the database:
- Each trade logged
- Full market context
- Results tracked
- Performance analytics available

Query the database:
```python
from database.trade_storage import TradeDatabase
db = TradeDatabase('data/trades_advanced.db')
stats = db.get_statistics()
```

## Tips for Loop Trading

1. **Start with Testing**
   ```bash
   # Test with 2-3 iterations first
   python run_unified_trading.py --loop --max-iterations 3
   ```

2. **Use Demo Account**
   ```bash
   # Ensure ACCOUNT_TYPE=demo in .env
   ```

3. **Monitor First Hour**
   - Watch the first 10-20 trades
   - Check win rate
   - Adjust strategy if needed

4. **Set Reasonable Intervals**
   - 5 minutes: Standard
   - 3 minutes: Aggressive
   - 10 minutes: Conservative

5. **Use Max Iterations**
   ```bash
   # Don't run indefinitely until tested
   --max-iterations 50
   ```

## Summary

**Loop Mode Features:**
- ✅ Automatic trading every N minutes
- ✅ Configurable intervals
- ✅ Limited or unlimited iterations
- ✅ Real-time progress display
- ✅ Full session statistics
- ✅ Graceful interruption
- ✅ Database integration
- ✅ Risk management

**Commands:**
```bash
# Basic loop (5 min intervals)
python run_unified_trading.py --loop

# Custom interval
python run_unified_trading.py --loop --loop-interval 3

# Limited iterations
python run_unified_trading.py --loop --max-iterations 10

# Full options
python run_unified_trading.py \
  --mode basic \
  --pair EURUSD-OTC \
  --loop \
  --loop-interval 5 \
  --max-iterations 20
```

Start trading automatically! 🚀
