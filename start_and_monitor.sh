#!/bin/bash
# =============================================================================
# KAEL TRADING BOT - START AND MONITOR SCRIPT
# =============================================================================

set -e

echo "================================================================================================"
echo "🤖 KAEL AUTONOMOUS PARALLEL TRADING BOT - STARTUP SCRIPT"
echo "================================================================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "   Please create a .env file with your IQ Option credentials."
    exit 1
fi

echo "✅ .env file found"

# Stop any existing containers
echo ""
echo "🛑 Stopping any existing containers..."
docker-compose -f docker-compose.parallel.yml down || true

# Build the image
echo ""
echo "🔨 Building Docker image (this may take a few minutes)..."
docker-compose -f docker-compose.parallel.yml build

# Start the services
echo ""
echo "🚀 Starting trading bot..."
docker-compose -f docker-compose.parallel.yml up -d

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Show status
echo ""
echo "📊 Container Status:"
docker-compose -f docker-compose.parallel.yml ps

# Show logs
echo ""
echo "================================================================================================"
echo "📋 INITIAL LOGS (last 50 lines)"
echo "================================================================================================"
docker-compose -f docker-compose.parallel.yml logs --tail=50 parallel-trading-bot

echo ""
echo "================================================================================================"
echo "✅ TRADING BOT IS RUNNING"
echo "================================================================================================"
echo ""
echo "📡 Health API: http://localhost:5001"
echo "📊 Statistics: http://localhost:5001/statistics"
echo "📈 Recent Trades: http://localhost:5001/recent_trades"
echo "📉 Strategy Stats: http://localhost:5001/strategy_stats"
echo ""
echo "🔍 Monitor commands:"
echo "   - View logs:        docker-compose -f docker-compose.parallel.yml logs -f"
echo "   - View stats:       curl -s http://localhost:5001/statistics | python -m json.tool"
echo "   - Stop bot:         docker-compose -f docker-compose.parallel.yml down"
echo "   - Restart bot:      docker-compose -f docker-compose.parallel.yml restart"
echo ""
echo "💡 Press Ctrl+C to stop monitoring (bot will keep running in background)"
echo "================================================================================================"
echo ""

# Follow logs
docker-compose -f docker-compose.parallel.yml logs -f
