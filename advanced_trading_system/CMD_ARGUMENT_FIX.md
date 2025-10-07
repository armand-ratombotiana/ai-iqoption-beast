# CMD Argument Fix - Removed --demo

## Error
```
run_unified_trading.py: error: unrecognized arguments: --demo
```

## Problem
The Dockerfile CMD included `--demo` argument, but `run_unified_trading.py` doesn't accept it. The script uses the `ACCOUNT_TYPE` environment variable instead.

## Fix

### [Dockerfile](Dockerfile:102)

**Before:**
```dockerfile
CMD ["python", "run_unified_trading.py", "--mode", "basic", "--loop", "--loop-interval", "300", "--demo"]
```

**After:**
```dockerfile
CMD ["python", "run_unified_trading.py", "--mode", "basic", "--loop", "--loop-interval", "300"]
```

## How Account Type is Set

Account type is configured via environment variable in [docker-compose.yml](docker-compose.yml):

```yaml
environment:
  - ACCOUNT_TYPE=demo  # or "real"
```

The script reads this environment variable internally, so the `--demo` flag is not needed.

## Also Fixed

Added back the entrypoint setup that was missing:

```dockerfile
# Copy entrypoint script to /usr/local/bin and make executable
RUN cp docker-entrypoint.sh /usr/local/bin/ && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
```

## Available Arguments

The script accepts these arguments:

```
--mode {basic,enhanced,parallel}  Trading mode
--pair PAIR                        Currency pair (e.g., EURUSD-OTC)
--duration DURATION                Trade duration in minutes
--loop                             Run continuously
--loop-interval LOOP_INTERVAL      Seconds between trades
--max-iterations MAX_ITERATIONS    Max number of iterations
--test-connection                  Test connection only
--health-check-interval            Health check frequency
```

## Configuration Priority

1. **Command line arguments** (from CMD)
2. **Environment variables** (from docker-compose.yml)
3. **Default values** (in the script)

## Rebuild

```bash
docker-compose down
docker-compose build
docker-compose up
```

Or use the automated script:
```bash
./docker-rebuild.sh
```

## Verify

The container should now start without argument errors:

```bash
docker-compose up
```

You should see:
```
🔧 Docker Container Starting...
================================
Python version: Python 3.11.x
✅ iqoptionapi folder exists
✅ iqoptionapi import successful
================================
🚀 All checks passed! Starting application...

[Trading system starts...]
```

## Summary

✅ Removed `--demo` from CMD
✅ Added back entrypoint setup
✅ Account type set via `ACCOUNT_TYPE` env var
✅ Script should now start successfully

**Next**: Rebuild and start! 🚀
