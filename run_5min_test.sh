#!/bin/bash

# =============================================================================
# 5-Minute Test Run Script for Autonomous Trading Bot
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================================================="
echo "  🤖 AUTONOMOUS TRADING BOT - 5 MINUTE TEST RUN"
echo "=========================================================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ ERROR: .env file not found!${NC}"
    echo "Please run: python3 setup_credentials.py"
    exit 1
fi

# Verify demo mode
TRADING_MODE=$(grep "^TRADING_MODE=" .env | cut -d '=' -f2)
if [ "$TRADING_MODE" != "demo" ]; then
    echo -e "${RED}❌ ERROR: TRADING_MODE must be 'demo' for testing!${NC}"
    echo "Current mode: $TRADING_MODE"
    echo "Please edit .env and set: TRADING_MODE=demo"
    exit 1
fi

echo -e "${GREEN}✅ Configuration OK - Demo Mode Confirmed${NC}"
echo ""

# Create logs directory
mkdir -p logs

# Set test duration (5 minutes = 300 seconds)
TEST_DURATION=300

echo "Test Configuration:"
echo "  Duration: 5 minutes"
echo "  Mode: DEMO"
echo "  Start Time: $(date)"
echo ""

echo -e "${BLUE}📊 Starting bot in background...${NC}"
echo ""

# Start the bot in background
python3 autonomous_trading_bot_24_7.py > logs/test_run_$(date +%Y%m%d_%H%M%S).log 2>&1 &
BOT_PID=$!

echo -e "${GREEN}✅ Bot started (PID: $BOT_PID)${NC}"
echo ""

# Function to display statistics
show_stats() {
    if curl -s http://localhost:5001/statistics > /dev/null 2>&1; then
        echo "=================================================="
        echo "📊 CURRENT STATISTICS ($(date +%H:%M:%S))"
        echo "=================================================="
        curl -s http://localhost:5001/statistics | python3 -m json.tool
        echo ""
    fi
}

# Function to cleanup
cleanup() {
    echo ""
    echo "=========================================================================="
    echo "🛑 Stopping bot..."
    echo "=========================================================================="

    # Try graceful shutdown via API
    curl -s -X POST http://localhost:5001/stop > /dev/null 2>&1

    # Wait a bit
    sleep 3

    # Force kill if still running
    if kill -0 $BOT_PID 2>/dev/null; then
        echo "Force stopping bot..."
        kill $BOT_PID 2>/dev/null || true
    fi

    # Show final statistics
    echo ""
    echo "=========================================================================="
    echo "📊 FINAL TEST RESULTS"
    echo "=========================================================================="
    show_stats

    # Show log tail
    echo ""
    echo "=========================================================================="
    echo "📋 LAST 30 LOG LINES"
    echo "=========================================================================="
    tail -30 logs/autonomous_bot_$(date +%Y%m%d).log 2>/dev/null || echo "No logs found"

    echo ""
    echo "=========================================================================="
    echo "✅ 5-MINUTE TEST COMPLETE"
    echo "=========================================================================="
    echo "End Time: $(date)"
    echo "Logs saved in: logs/"
    echo ""
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Wait and show progress
echo "=========================================================================="
echo "⏱️  TEST IN PROGRESS - Running for 5 minutes"
echo "=========================================================================="
echo ""
echo "Press Ctrl+C to stop early"
echo ""

# Monitor for 5 minutes, showing stats every minute
ELAPSED=0
UPDATE_INTERVAL=60  # 1 minute

while [ $ELAPSED -lt $TEST_DURATION ]; do
    # Check if bot is still running
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo -e "${RED}⚠️  Bot stopped unexpectedly!${NC}"
        break
    fi

    # Show progress
    REMAINING=$((TEST_DURATION - ELAPSED))
    SECONDS_REMAINING=$REMAINING
    echo "⏳ Time remaining: ${SECONDS_REMAINING} seconds..."

    # Show stats every minute
    if [ $((ELAPSED % UPDATE_INTERVAL)) -eq 0 ] && [ $ELAPSED -gt 0 ]; then
        show_stats
    fi

    # Sleep for 30 seconds
    sleep 30
    ELAPSED=$((ELAPSED + 30))
done

# Test complete - cleanup will run via trap
echo ""
echo -e "${GREEN}✅ 5-minute test period completed${NC}"
