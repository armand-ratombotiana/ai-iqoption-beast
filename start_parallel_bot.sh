#!/bin/bash
# ============================================================================
# KAEL Autonomous Parallel Trading Bot - Start Script
# ============================================================================

set -e

echo "============================================================================"
echo "🚀 KAEL AUTONOMOUS PARALLEL TRADING BOT - DOCKER STARTUP"
echo "============================================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "   Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "   Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create a .env file with your IQ Option credentials"
    echo "   See README_PARALLEL_BOT_DOCKER.md for configuration details"
    exit 1
fi

# Check if credentials are set
if ! grep -q "IQOPTION_EMAIL=" .env || ! grep -q "IQOPTION_PASSWORD=" .env; then
    echo "❌ Error: IQ Option credentials not configured in .env"
    echo "   Please set IQOPTION_EMAIL and IQOPTION_PASSWORD in .env file"
    exit 1
fi

# Get trading mode
TRADING_MODE=$(grep "^TRADING_MODE=" .env | cut -d '=' -f2 | tr -d ' ')
if [ -z "$TRADING_MODE" ]; then
    TRADING_MODE="demo"
fi

echo "📋 Configuration:"
echo "   Trading Mode: $TRADING_MODE"
echo ""

# Warning for live mode
if [ "$TRADING_MODE" = "live" ]; then
    echo "⚠️  WARNING: LIVE MODE ENABLED - REAL MONEY TRADING!"
    echo "   Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
fi

# Build the image
echo "🔨 Building Docker image..."
docker-compose -f docker-compose.parallel.yml build

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to build Docker image"
    exit 1
fi

echo "✅ Docker image built successfully"
echo ""

# Start the container
echo "🚀 Starting parallel trading bot..."
docker-compose -f docker-compose.parallel.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to start container"
    exit 1
fi

echo "✅ Bot started successfully!"
echo ""

# Wait a moment for the container to initialize
sleep 3

# Check if container is running
if docker ps | grep -q "kael-parallel-trading-bot"; then
    echo "============================================================================"
    echo "✅ PARALLEL TRADING BOT IS RUNNING"
    echo "============================================================================"
    echo ""
    echo "📊 Monitoring Commands:"
    echo "   View logs:        docker-compose -f docker-compose.parallel.yml logs -f"
    echo "   Check health:     curl http://localhost:5001/health"
    echo "   Get statistics:   curl http://localhost:5001/statistics"
    echo "   Stop bot:         docker-compose -f docker-compose.parallel.yml down"
    echo ""
    echo "📁 Log files are saved in: ./logs/"
    echo ""
    echo "🏥 Health API: http://localhost:5001"
    echo ""
    
    # Show initial logs
    echo "📋 Initial logs (last 20 lines):"
    echo "============================================================================"
    docker-compose -f docker-compose.parallel.yml logs --tail=20 parallel-trading-bot
    echo "============================================================================"
    echo ""
    echo "💡 Tip: Run 'docker-compose -f docker-compose.parallel.yml logs -f' to follow logs"
else
    echo "❌ Error: Container failed to start"
    echo "   Check logs: docker-compose -f docker-compose.parallel.yml logs"
    exit 1
fi
