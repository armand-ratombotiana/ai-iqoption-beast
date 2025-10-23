#!/bin/bash

# =============================================================================
# 30-Minute Parallel Trading Bot Test Script
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================================================="
echo "  ���� PARALLEL MULTI-INSTRUMENT TRADING BOT - 30 MINUTE TEST"
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

# Get parallel settings
MAX_CONCURRENT=$(grep "^MAX_CONCURRENT_INSTRUMENTS=" .env | cut -d '=' -f2 || echo "5")
PORTFOLIO_RISK=$(grep "^PORTFOLIO_RISK_PERCENT=" .env | cut -d '=' -f2 || echo "10.0")
MAX_MONITOR=$(grep "^MAX_INSTRUMENTS_TO_MONITOR=" .env | cut -d '=' -f2 || echo "20")

echo "Parallel Trading Configuration:"
echo "  Max Concurrent Instruments: ${MAX_CONCURRENT:-5}"
echo "  Instruments to Monitor: ${MAX_MONITOR:-20}"
echo "  Portfolio Risk: ${PORTFOLIO_RISK:-10.0}%"
echo "  Mode: DEMO"
echo ""

# Set test duration (30 minutes = 1800 seconds)
TEST_DURATION=1800

echo "Test Configuration:"
echo "  Duration: 30 minutes"
echo "  Start Time: $(date)"
echo "  Expected End: $(date -d '+30 minutes' 2>/dev/null || date -v+30M 2>/dev/null || echo 'Unknown')"
echo ""

# Create logs directory
mkdir -p logs

echo -e "${BLUE}📊 Starting parallel trading bot in background...${NC}"
echo ""

# Start the bot in background
python3 autonomous_parallel_trading_bot.py > logs/parallel_test_30min_$(date +%Y%m%d_%H%M%S).log 2>&1 &
BOT_PID=$!

echo -e "${GREEN}✅ Parallel Bot started (PID: $BOT_PID)${NC}"
echo ""

# Wait a few seconds for bot to initialize
sleep 5

# Function to display statistics
show_stats() {
    if curl -s http://localhost:5001/statistics > /dev/null 2>&1; then
        echo ""
        echo "=========================================================================="
        echo -e "${CYAN}📊 PARALLEL TRADING STATISTICS ($(date +%H:%M:%S))${NC}"
        echo "=========================================================================="
        
        STATS=$(curl -s http://localhost:5001/statistics)
        
        # Parse and display key metrics
        echo "$STATS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    
    print(f\"\\n🎯 PORTFOLIO STATUS:\")
    print(f\"   Status: {data.get('status', 'unknown').upper()}\")
    print(f\"   Mode: {data.get('mode', 'unknown').upper()}\")
    print(f\"   Balance: \\\${data.get('balance', 0):.2f}\")
    print(f\"   Start Balance: \\\${data.get('start_balance', 0):.2f}\")
    
    daily_net = data.get('daily_net', 0)
    print(f\"\\n💰 DAILY PERFORMANCE:\")
    print(f\"   Daily P/L: \\\${daily_net:+.2f}\")
    print(f\"   Daily Profit: \\\${data.get('daily_profit', 0):.2f}\")
    print(f\"   Daily Loss: \\\${data.get('daily_loss', 0):.2f}\")
    
    print(f\"\\n📈 TRADING STATISTICS:\")
    print(f\"   Trades Today: {data.get('trades_today', 0)}\")
    print(f\"   Wins: {data.get('wins_today', 0)}\")
    print(f\"   Losses: {data.get('losses_today', 0)}\")
    print(f\"   Win Rate: {data.get('win_rate', 0):.1f}%\")
    
    print(f\"\\n🔄 ACTIVE POSITIONS:\")
    print(f\"   Active Instruments: {data.get('active_count', 0)}/{data.get('instruments_traded', 0)}\")
    active = data.get('active_instruments', [])
    if active:
        print(f\"   Currently Trading: {', '.join(active)}\")
    else:
        print(f\"   Currently Trading: None\")
    print(f\"   Risk Allocated: \\\${data.get('total_risk_allocated', 0):.2f}\")
    
    instrument_stats = data.get('instrument_stats', [])
    if instrument_stats:
        print(f\"\\n🏆 TOP PERFORMING INSTRUMENTS:\")
        for i, inst in enumerate(instrument_stats[:5], 1):
            status = '🟢 ACTIVE' if inst.get('is_trading') else '⚪ IDLE'
            print(f\"   {i}. {inst['instrument']:8} | {status:10} | Trades: {inst['total_trades']:3} | WR: {inst['win_rate']:5.1f}% | P/L: \\\${inst['profit']:+7.2f}\")
    
    uptime = data.get('uptime_hours', 0)
    print(f\"\\n⏱️  UPTIME: {uptime:.2f} hours\")
    
except Exception as e:
    print(f'Error parsing stats: {e}')
    import traceback
    traceback.print_exc()
"
        echo ""
        echo "=========================================================================="
    else
        echo -e "${YELLOW}⚠️  Could not connect to statistics API${NC}"
    fi
}

# Function to cleanup
cleanup() {
    echo ""
    echo "=========================================================================="
    echo "🛑 Stopping parallel trading bot..."
    echo "=========================================================================="

    # Try graceful shutdown via API
    echo "Sending shutdown signal..."
    curl -s -X POST http://localhost:5001/stop > /dev/null 2>&1

    # Wait a bit
    sleep 5

    # Force kill if still running
    if kill -0 $BOT_PID 2>/dev/null; then
        echo "Force stopping bot..."
        kill $BOT_PID 2>/dev/null || true
        sleep 2
    fi

    # Show final statistics
    echo ""
    echo "=========================================================================="
    echo -e "${CYAN}📊 FINAL TEST RESULTS${NC}"
    echo "=========================================================================="
    show_stats

    # Show log tail
    echo ""
    echo "=========================================================================="
    echo "📋 LAST 40 LOG LINES"
    echo "=========================================================================="
    tail -40 logs/parallel_bot_$(date +%Y%m%d).log 2>/dev/null || echo "No logs found"

    echo ""
    echo "=========================================================================="
    echo -e "${GREEN}✅ 30-MINUTE PARALLEL TRADING TEST COMPLETE${NC}"
    echo "=========================================================================="
    echo "End Time: $(date)"
    echo ""
    echo "📁 Logs saved in:"
    echo "   Main log: logs/parallel_bot_$(date +%Y%m%d).log"
    echo "   Trade log: logs/parallel_trades_$(date +%Y%m%d).log"
    echo "   Test log: logs/parallel_test_30min_*.log"
    echo ""
    echo "📊 To view logs:"
    echo "   tail -f logs/parallel_bot_$(date +%Y%m%d).log"
    echo "   tail -f logs/parallel_trades_$(date +%Y%m%d).log"
    echo ""
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Wait and show progress
echo "=========================================================================="
echo -e "${BLUE}⏱️  TEST IN PROGRESS - Running for 30 minutes${NC}"
echo "=========================================================================="
echo ""
echo "Press Ctrl+C to stop early"
echo ""
echo "Statistics will be displayed every 3 minutes"
echo ""

# Show initial stats after 30 seconds
sleep 30
show_stats

# Monitor for 30 minutes, showing stats every 3 minutes
ELAPSED=30
UPDATE_INTERVAL=180  # 3 minutes

while [ $ELAPSED -lt $TEST_DURATION ]; do
    # Check if bot is still running
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo -e "${RED}⚠️  Bot stopped unexpectedly!${NC}"
        break
    fi

    # Show progress
    REMAINING=$((TEST_DURATION - ELAPSED))
    MINUTES_REMAINING=$((REMAINING / 60))
    echo -e "${YELLOW}⏳ Time remaining: ${MINUTES_REMAINING} minutes...${NC}"

    # Show stats every 3 minutes
    if [ $((ELAPSED % UPDATE_INTERVAL)) -eq 0 ]; then
        show_stats
    fi

    # Sleep for 1 minute
    sleep 60
    ELAPSED=$((ELAPSED + 60))
done

# Test complete - cleanup will run via trap
echo ""
echo -e "${GREEN}✅ 30-minute test period completed${NC}"