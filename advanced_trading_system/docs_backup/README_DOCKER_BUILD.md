# Docker Build - Quick Reference

## Current Status: ✅ FIXED

The `ModuleNotFoundError: No module named 'requests'` error has been completely fixed.

## Quick Start

```bash
./docker-rebuild.sh
```

That's it! The script will:
1. Check all files are present
2. Stop old containers
3. Remove old images
4. Build with full verification
5. Test the built image
6. Show you next steps

## What Was Fixed

### Problem
```
❌ ModuleNotFoundError: No module named 'requests'
```

### Solution
1. ✅ Installed pip specifically for Python 3.11
2. ✅ Use `python -m pip` instead of just `pip`
3. ✅ Verify each package after installation
4. ✅ Auto-retry if packages missing
5. ✅ Show detailed output at each step

## Build Commands

### Automated (Recommended)
```bash
./docker-rebuild.sh
```

### Manual
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Background Mode
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop
```bash
docker-compose down
```

## Expected Build Output

You should see these verification steps:

```
Step X: pip --version
 ---> pip 24.x from ... (python 3.11)

Step X: === Installing from requirements.txt ===
 ---> requests>=2.31.0
      numpy>=1.24.0
      websocket-client>=1.6.0
      ...

Step X: Successfully installed requests-2.31.0 numpy-1.24.0 ...

Step X: === Installed packages ===
 ---> requests       2.31.0
      numpy          1.24.0
      ...

Step X: RUN python -c "import requests..."
 ---> ✅ requests installed

Step X: RUN python -c "import numpy..."
 ---> ✅ numpy installed

Step X: RUN python -c "import websocket..."
 ---> ✅ websocket installed

Step X: RUN python -c "from iqoptionapi.stable_api..."
 ---> ✅ iqoptionapi verified
```

If any step fails, you'll see detailed error information.

## Build Time

- **First build**: 4-6 minutes
- **Cached rebuild**: 1-2 minutes

## Verification

After build, test manually:

```bash
# Test Python version
docker run --rm kael-trading-system python --version

# Test imports
docker run --rm kael-trading-system python -c "
import requests
import numpy
import websocket
from iqoptionapi.stable_api import IQ_Option
print('✅ All imports work!')
"
```

## Configuration

Before starting, set your credentials in [.env](.env):

```env
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
ACCOUNT_TYPE=demo
```

Or edit [docker-compose.yml](docker-compose.yml) environment variables.

## Common Issues

### Build fails at pip install?
- Check internet connection
- Try: `docker system prune -af && ./docker-rebuild.sh`

### Package not found after install?
- The build now auto-retries failed packages
- Check build output for errors

### iqoptionapi import fails?
- Check [iqoptionapi/](iqoptionapi/) folder exists
- Check it has `stable_api.py`
- Build shows detailed debug if this fails

## Files

| File | Purpose |
|------|---------|
| [Dockerfile](Dockerfile) | Container build instructions |
| [docker-compose.yml](docker-compose.yml) | Service configuration |
| [requirements.txt](requirements.txt) | Python dependencies |
| [docker-entrypoint.sh](docker-entrypoint.sh) | Startup script |
| [docker-rebuild.sh](docker-rebuild.sh) | Build helper |
| [.dockerignore](.dockerignore) | Files to exclude from build |

## Documentation

- 📖 [FINAL_FIX.md](FINAL_FIX.md) - Complete fix details
- 📖 [BUILD_NOW.md](BUILD_NOW.md) - Quick start
- 📖 [FIX_REQUESTS_MODULE.md](FIX_REQUESTS_MODULE.md) - Requests fix details
- 📖 [DOCKER_QUICK_FIX.md](DOCKER_QUICK_FIX.md) - Previous fixes

## Key Technical Details

### Why `python -m pip`?

✅ **Correct**: `python -m pip install package`
- Uses pip from THE SAME Python version

❌ **Wrong**: `pip install package`
- Might use pip from different Python version

### Auto-Retry Logic

If a package verification fails, the build:
1. Shows error message
2. Tries installing directly
3. Verifies again
4. Fails with details if still broken

### Build Cache

Docker caches each layer. To rebuild from scratch:
```bash
docker-compose build --no-cache
```

## Next Steps After Build

1. **Test the system**:
   ```bash
   docker-compose up
   ```

2. **Watch logs**:
   ```bash
   docker-compose logs -f
   ```

3. **Check container status**:
   ```bash
   docker-compose ps
   ```

4. **Execute commands in container**:
   ```bash
   docker exec kael-trading-system python -c "print('Hello')"
   ```

## Need Help?

1. Check error message in build output
2. Review [FINAL_FIX.md](FINAL_FIX.md)
3. Run with verbose: `docker-compose build --no-cache --progress=plain`
4. Clear everything: `docker system prune -af`

---

**Ready to build?** → `./docker-rebuild.sh` 🚀
