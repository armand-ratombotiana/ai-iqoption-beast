#!/bin/bash

# =============================================================================
# Real-time Bot Monitoring Script
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================================================="
echo "  📊 REAL-TIME BOT MONITOR"
echo "=========================================================================="
echo ""

# Function to show statistics
show_stats() {
    clear
    echo "=========================================================================="
    echo "  📊 AUTONOMOUS TRADING BOT - LIVE STATISTICS"
    echo "=========================================================================="
    echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================================================="
    echo ""

    # Get statistics from API
    if curl -s http://localhost:5001/statistics > /tmp/bot_stats.json 2>&1; then
        # Parse and display nicely
        python3 << 'EOF'
import json
import sys

try:
    with open('/tmp/bot_stats.json', 'r') as f:
        stats = json.load(f)

    # Display formatted stats
    print(f"🏦 Account Status:")
    print(f"   Mode: {stats.get('mode', 'N/A').upper()}")
    print(f"   Balance: ${stats.get('balance', 0):.2f}")
    print(f"   Daily P/L: ${stats.get('daily_net', 0):.2f}")
    print()

    print(f"📊 Trading Statistics:")
    print(f"   Trades Today: {stats.get('trades_today', 0)}")
    print(f"   Wins: {stats.get('wins_today', 0)}")
    print(f"   Losses: {stats.get('losses_today', 0)}")
    print(f"   Win Rate: {stats.get('win_rate', 0):.1f}%")
    print()

    print(f"🎯 Streaks:")
    print(f"   Current Wins: {stats.get('consecutive_wins', 0)}")
    print(f"   Current Losses: {stats.get('consecutive_losses', 0)}")
    print(f"   Best Streak: {stats.get('best_winning_streak', 0)}")
    print(f"   Worst Streak: {stats.get('worst_losing_streak', 0)}")
    print()

    print(f"📈 Performance:")
    print(f"   Daily Profit: ${stats.get('daily_profit', 0):.2f}")
    print(f"   Daily Loss: ${stats.get('daily_loss', 0):.2f}")
    print(f"   Total Trades: {stats.get('total_trades', 0)}")
    print(f"   Uptime: {stats.get('uptime_hours', 0):.2f} hours")
    print()

    print(f"🎲 Risk Management:")
    print(f"   Martingale Level: {stats.get('martingale_level', 0)}")
    print()

except Exception as e:
    print(f"❌ Error parsing stats: {e}")
EOF
    else
        echo -e "${RED}❌ Cannot connect to bot API (http://localhost:5001)${NC}"
        echo "   Is the bot running?"
    fi

    echo "=========================================================================="
    echo "  Press Ctrl+C to exit"
    echo "=========================================================================="
}

# Monitor loop
while true; do
    show_stats
    sleep 10  # Update every 10 seconds
done
