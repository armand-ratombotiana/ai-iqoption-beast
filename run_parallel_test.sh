#!/bin/bash

# =============================================================================
# Parallel Trading Bot Test Script
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================================================="
echo "  🚀 PARALLEL MULTI-INSTRUMENT TRADING BOT - TEST RUN"
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
    exit 1
fi

echo -e "${GREEN}✅ Configuration OK - Demo Mode Confirmed${NC}"
echo ""

# Check parallel settings
MAX_CONCURRENT=$(grep "^MAX_CONCURRENT_INSTRUMENTS=" .env | cut -d '=' -f2 || echo "5")
PORTFOLIO_RISK=$(grep "^PORTFOLIO_RISK_PERCENT=" .env | cut -d '=' -f2 || echo "10.0")

echo "Parallel Trading Configuration:"
echo "  Max Concurrent Instruments: ${MAX_CONCURRENT:-5}"
echo "  Portfolio Risk: ${PORTFOLIO_RISK:-10.0}%"
echo "  Mode: DEMO"
echo ""

# Ask for test duration
echo "Select test duration:"
echo "  1) 5 minutes (quick test)"
echo "  2) 15 minutes (standard test)"
echo "  3) 30 minutes (extended test)"
echo "  4) 60 minutes (full test)"
echo ""
read -p "Enter choice [1-4]: " duration_choice

case $duration_choice in
    1)
        TEST_DURATION=300
        DURATION_NAME="5 minutes"
        ;;
    2)
        TEST_DURATION=900
        DURATION_NAME="15 minutes"
        ;;
    3)
        TEST_DURATION=1800
        DURATION_NAME="30 minutes"
        ;;
    4)
        TEST_DURATION=3600
        DURATION_NAME="60 minutes"
        ;;
    *)
        echo -e "${RED}Invalid choice. Using 15 minutes.${NC}"
        TEST_DURATION=900
        DURATION_NAME="15 minutes"
        ;;
esac

echo ""
echo "Test Configuration:"
echo "  Duration: $DURATION_NAME"
echo "  Start Time: $(date)"
echo ""

# Create logs directory
mkdir -p logs

echo -e "${BLUE}📊 Starting parallel trading bot...${NC}"
echo ""

# Start the bot in background
python3 autonomous_parallel_trading_bot.py > logs/parallel_test_$(date +%Y%m%d_%H%M%S).log 2>&1 &
BOT_PID=$!

echo -e "${GREEN}✅ Bot started (PID: $BOT_PID)${NC}"
echo ""

# Function to display statistics
show_stats() {
    if curl -s http://localhost:5001/statistics > /dev/null 2>&1; then
        echo "=================================================="
        echo "📊 PARALLEL TRADING STATISTICS ($(date +%H:%M:%S))"
        echo "=================================================="
        
        STATS=$(curl -s http://localhost:5001/statistics)
        
        # Parse and display key metrics
        echo "$STATS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"Status: {data.get('status', 'unknown')}\")
    print(f\"Balance: \${data.get('balance', 0):.2f}\")
    print(f\"Daily P/L: \${data.get('daily_net', 0):+.2f}\")
    print(f\"Trades Today: {data.get('trades_today', 0)}\")
    print(f\"Win Rate: {data.get('win_rate', 0):.1f}%\")
    print(f\"Active Instruments: {data.get('active_count', 0)}/{data.get('instruments_traded', 0)}\")
    print(f\"Active: {', '.join(data.get('active_instruments', []))}\")
    print()
    print('Top Performing Instruments:')
    for inst in data.get('instrument_stats', [])[:5]:
        print(f\"  {inst['instrument']}: {inst['total_trades']} trades, {inst['win_rate']:.1f}% WR, \${inst['profit']:+.2f}\")
except Exception as e:
    print(f'Error parsing stats: {e}')
"
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
    tail -30 logs/parallel_bot_$(date +%Y%m%d).log 2>/dev/null || echo "No logs found"

    echo ""
    echo "=========================================================================="
    echo "✅ PARALLEL TRADING TEST COMPLETE"
    echo "=========================================================================="
    echo "End Time: $(date)"
    echo "Logs saved in: logs/"
    echo ""
    echo "To view full logs:"
    echo "  tail -f logs/parallel_bot_$(date +%Y%m%d).log"
    echo ""
    echo "To view trades only:"
    echo "  tail -f logs/parallel_trades_$(date +%Y%m%d).log"
    echo ""
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Wait and show progress
echo "=========================================================================="
echo "⏱️  TEST IN PROGRESS - Running for $DURATION_NAME"
echo "=========================================================================="
echo ""
echo "Press Ctrl+C to stop early"
echo ""

# Monitor for test duration, showing stats every 2 minutes
ELAPSED=0
UPDATE_INTERVAL=120  # 2 minutes

while [ $ELAPSED -lt $TEST_DURATION ]; do
    # Check if bot is still running
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo -e "${RED}⚠️  Bot stopped unexpectedly!${NC}"
        break
    fi

    # Show progress
    REMAINING=$((TEST_DURATION - ELAPSED))
    MINUTES_REMAINING=$((REMAINING / 60))
    echo "⏳ Time remaining: ${MINUTES_REMAINING} minutes..."

    # Show stats every 2 minutes
    if [ $((ELAPSED % UPDATE_INTERVAL)) -eq 0 ] && [ $ELAPSED -gt 0 ]; then
        show_stats
    fi

    # Sleep for 1 minute
    sleep 60
    ELAPSED=$((ELAPSED + 60))
done

# Test complete - cleanup will run via trap
echo ""
echo -e "${GREEN}✅ Test period completed${NC}"
