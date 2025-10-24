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
    python3.11-dev \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 default
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3

# Install pip for Python 3.11 properly
RUN python3.11 -m ensurepip --upgrade || \
    (wget https://bootstrap.pypa.io/get-pip.py && \
     python3.11 get-pip.py && \
     rm get-pip.py)

# Make sure pip is linked correctly
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    python -m pip --version

# Upgrade pip, setuptools, wheel
RUN python -m pip install --upgrade pip setuptools wheel

# Copy dependencies first
COPY requirements.txt .

# Show what we're about to install
RUN echo "=== Installing from requirements.txt ===" && \
    cat requirements.txt && \
    echo "========================================"

# Install Python dependencies with verbose output
RUN python -m pip install --no-cache-dir -r requirements.txt || \
    (echo "❌ pip install failed!" && exit 1)

# Show what was installed
RUN echo "=== Installed packages ===" && \
    python -m pip list && \
    echo "========================="

# Verify critical packages are installed
RUN python -c "import requests; print('✅ requests installed')" || \
    (echo "❌ requests not found! Trying to install directly..." && \
     python -m pip install requests && \
     python -c "import requests; print('✅ requests installed after direct install')")

RUN python -c "import numpy; print('✅ numpy installed')" || \
    (echo "❌ numpy not found! Trying to install directly..." && \
     python -m pip install numpy && \
     python -c "import numpy; print('✅ numpy installed after direct install')")

RUN python -c "import websocket; print('✅ websocket installed')" || \
    (echo "❌ websocket not found! Trying to install directly..." && \
     python -m pip install websocket-client && \
     python -c "import websocket; print('✅ websocket installed after direct install')")

# Copy the entire app
COPY . .

# Create necessary directories
RUN mkdir -p logs database

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

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


# Default command (removed --demo, use ACCOUNT_TYPE env var instead)
# --loop-interval is in MINUTES (5 minutes between trades)
CMD ["python", "run_unified_trading.py", "--mode", "basic", "--loop", "--loop-interval", "5"]
