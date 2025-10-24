# Loop Interval Fix - 5 Minutes Between Trades

## Issue
```
⏳ Waiting 300 minutes until next trade...
   Next trade at: 19:22:55  (5 hours later!)
```

The system was waiting 300 minutes (5 hours) instead of 5 minutes between trades.

## Root Cause

The `--loop-interval` parameter is in **MINUTES**, not seconds:

```python
parser.add_argument('--loop-interval', type=int, default=5)  # Minutes!

# Later in code:
logger.info(f"⏳ Waiting {args.loop_interval} minutes until next trade...")
next_time = datetime.now() + timedelta(minutes=args.loop_interval)  # Uses minutes
time.sleep(args.loop_interval * 60)  # Converts to seconds for sleep
```

## Fix

### [Dockerfile](Dockerfile:97)

**Before:**
```dockerfile
CMD ["python", "run_unified_trading.py", "--mode", "basic", "--loop", "--loop-interval", "300"]
#                                                                                         ^^^
#                                                                                   300 MINUTES!
```

**After:**
```dockerfile
CMD ["python", "run_unified_trading.py", "--mode", "basic", "--loop", "--loop-interval", "5"]
#                                                                                         ^
#                                                                                   5 MINUTES
```

## Expected Behavior After Fix

```
⏳ Waiting 5 minutes until next trade...
   Next trade at: 14:27:55
```

The system will now:
1. Execute a trade
2. Wait 5 minutes
3. Execute next trade
4. Repeat continuously (because `--loop` is set)

## Configuration Options

### Via Dockerfile CMD (Default)
```dockerfile
CMD ["python", "run_unified_trading.py", "--loop-interval", "5"]  # 5 minutes
```

### Via docker-compose.yml Override
```yaml
services:
  trading-system:
    command: ["python", "run_unified_trading.py", "--mode", "basic", "--loop", "--loop-interval", "3"]
    #                                                                                             ^
    #                                                                                       3 minutes
```

### Via Environment Variable (if script supports it)
Set in your application configuration if needed.

## Parameter Details

| Parameter | Unit | Default | Description |
|-----------|------|---------|-------------|
| `--loop-interval` | **Minutes** | 5 | Time to wait between trades |
| `--duration` | Minutes | 1 | Trade duration |
| `--health-check-interval` | Seconds | 10 | Health check frequency |

## Rebuild

```bash
docker-compose down
docker-compose build
docker-compose up
```

Or use the helper:
```bash
./docker-rebuild.sh
```

## Verify

After starting, you should see:

```
🔧 Docker Container Starting...
✅ iqoptionapi import successful
🚀 All checks passed! Starting application...

📊 Starting trading...
[Trade execution...]
✅ Trade completed

⏳ Waiting 5 minutes until next trade...
   Next trade at: 14:32:00
```

## Trading Schedule Example

With `--loop-interval 5`:

```
14:22 - Trade #1 executed
14:27 - Trade #2 executed  (5 min later)
14:32 - Trade #3 executed  (5 min later)
14:37 - Trade #4 executed  (5 min later)
...continues every 5 minutes
```

## Other Timing Options

### Faster Trading (Every 3 Minutes)
```dockerfile
CMD ["python", "run_unified_trading.py", "--loop-interval", "3"]
```

### Slower Trading (Every 15 Minutes)
```dockerfile
CMD ["python", "run_unified_trading.py", "--loop-interval", "15"]
```

### Single Trade (No Loop)
```dockerfile
CMD ["python", "run_unified_trading.py", "--mode", "basic"]
# Removed --loop flag
```

## Summary

✅ Fixed: Loop interval now 5 minutes (was 300 minutes)
✅ Clarified: `--loop-interval` is in MINUTES, not seconds
✅ Added: Comment in Dockerfile for clarity

**Result**: System will execute trades every 5 minutes! 🚀

---

**Next**: Rebuild and restart the container:
```bash
docker-compose down && docker-compose build && docker-compose up
```
