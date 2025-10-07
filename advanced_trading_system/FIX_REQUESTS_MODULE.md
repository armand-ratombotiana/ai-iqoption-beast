# Fix for "ModuleNotFoundError: No module named 'requests'"

## Problem
During Docker build, got this error:
```
ModuleNotFoundError: No module named 'requests'
```

This happened when verifying iqoptionapi import at build time.

## Root Cause
The original Dockerfile copied `iqoptionapi/` **separately** before the main `COPY . .`, which meant:
1. iqoptionapi was copied first
2. Then verification tried to run
3. But `COPY . .` hadn't happened yet, so some files might be missing
4. Order of operations was confusing

## Solution Applied

### 1. Simplified [Dockerfile](Dockerfile) Copy Strategy

**Before:**
```dockerfile
# Copy iqoptionapi first (critical dependency)
COPY iqoptionapi/ ./iqoptionapi/

# Copy the rest of the app
COPY . .

# Verify iqoptionapi is available
RUN python -c "from iqoptionapi.stable_api import IQ_Option; ..."
```

**After:**
```dockerfile
# Install Python dependencies with verification
RUN pip install --no-cache-dir -r requirements.txt

# Verify critical packages are installed FIRST
RUN python -c "import requests; print('✅ requests installed')"
RUN python -c "import numpy; print('✅ numpy installed')"
RUN python -c "import websocket; print('✅ websocket installed')"

# Copy the entire app (including iqoptionapi)
COPY . .

# NOW verify iqoptionapi (after everything is in place)
RUN python -c "from iqoptionapi.stable_api import IQ_Option; print('✅ iqoptionapi verified')"
```

### 2. Key Changes

✅ **Verify dependencies immediately after pip install** (lines 33-35)
- Catches missing packages early
- Fails fast with clear error message

✅ **Single COPY command** (line 38)
- Simpler, less error-prone
- `.dockerignore` already excludes what we don't need

✅ **Verify iqoptionapi AFTER all files are copied** (line 49)
- Ensures everything is in place
- Shows detailed debug info if it fails

✅ **Added pip upgrade** (line 24)
- Ensures latest pip/setuptools/wheel
- Reduces installation issues

## Complete Updated Dockerfile

```dockerfile
# Use Ubuntu 22.04 (Jammy) with Python 3.11
FROM ubuntu:22.04

# Prevent interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install Python, pip, and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    python3.11-venv \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 default
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy dependencies first
COPY requirements.txt .

# Install Python dependencies with verification
RUN pip install --no-cache-dir -r requirements.txt

# Verify critical packages are installed
RUN python -c "import requests; print('✅ requests installed')"
RUN python -c "import numpy; print('✅ numpy installed')"
RUN python -c "import websocket; print('✅ websocket installed')"

# Copy the entire app
COPY . .

# Create necessary directories
RUN mkdir -p logs database

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copy entrypoint script and make executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh || \
    (cp docker-entrypoint.sh /usr/local/bin/ && chmod +x /usr/local/bin/docker-entrypoint.sh)

# Verify iqoptionapi is available (after all files are copied)
RUN python -c "from iqoptionapi.stable_api import IQ_Option; print('✅ iqoptionapi verified')" || \
    (echo "❌ iqoptionapi import failed!" && \
     echo "Checking if iqoptionapi exists:" && \
     ls -la /app/iqoptionapi/ && \
     echo "Python path:" && \
     python -c "import sys; print('\n'.join(sys.path))" && \
     exit 1)

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command
CMD ["python", "run_unified_trading.py", "--mode", "basic", "--loop", "--loop-interval", "300", "--demo"]
```

## Build Process Now Shows

When building, you'll see these verification steps:

```
✅ requests installed
✅ numpy installed
✅ websocket installed
... (files copied) ...
✅ iqoptionapi verified
```

If any step fails, the build stops immediately with a clear error.

## How to Rebuild

```bash
./docker-rebuild.sh
```

This will:
1. ✅ Run pre-flight checks (files exist)
2. ✅ Stop old containers
3. ✅ Remove old images
4. ✅ Build new image with all verification steps
5. ✅ Test the built image
6. ✅ Show next steps

## Expected Output

During build, watch for:
```
Step 6/15 : RUN python -c "import requests; print('✅ requests installed')"
 ---> Running in abc123...
✅ requests installed

Step 7/15 : RUN python -c "import numpy; print('✅ numpy installed')"
 ---> Running in def456...
✅ numpy installed

Step 8/15 : RUN python -c "import websocket; print('✅ websocket installed')"
 ---> Running in ghi789...
✅ websocket installed

...

Step 12/15 : RUN python -c "from iqoptionapi.stable_api import IQ_Option; print('✅ iqoptionapi verified')"
 ---> Running in jkl012...
✅ iqoptionapi verified
```

## Troubleshooting

### If requests still fails:

**1. Check requirements.txt has requests:**
```bash
grep requests requirements.txt
```
Should show: `requests>=2.31.0`

**2. Try installing manually to test:**
```bash
docker run --rm ubuntu:22.04 bash -c "
  apt-get update && apt-get install -y python3-pip
  pip install requests
  python3 -c 'import requests; print(\"✅ works\")'
"
```

**3. Clear Docker cache completely:**
```bash
docker system prune -af
./docker-rebuild.sh
```

## Files Modified

| File | Lines | Change |
|------|-------|--------|
| [Dockerfile](Dockerfile:33-35) | 33-35 | Added dependency verification |
| [Dockerfile](Dockerfile:38) | 38 | Simplified to single COPY |
| [Dockerfile](Dockerfile:49-55) | 49-55 | Moved iqoptionapi verification after COPY |
| [docker-rebuild.sh](docker-rebuild.sh) | All | Enhanced with better messages |

## Summary

✅ **Fixed**: Package installation verification
✅ **Simplified**: Single COPY strategy
✅ **Enhanced**: Clear error messages
✅ **Verified**: All dependencies check before iqoptionapi import

**Next**: Run `./docker-rebuild.sh` 🚀
