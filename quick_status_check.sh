#!/bin/bash

# Quick status check for KAEL Ultimate Evaluator

echo "=================================="
echo "🚀 KAEL QUICK STATUS CHECK"
echo "=================================="
echo ""

# Check containers
echo "📦 CONTAINERS:"
docker ps --filter "name=kael-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -7
echo ""

# Check API
echo "🏥 API HEALTH:"
curl -s http://localhost:5001/health | jq -r '.status' 2>/dev/null || echo "❌ API not responding"
echo ""

# Get statistics
echo "📊 STATISTICS:"
STATS=$(curl -s http://localhost:5001/statistics 2>/dev/null)
if [ -n "$STATS" ]; then
    echo "Balance: $(echo $STATS | jq -r '.current_balance' 2>/dev/null || echo 'N/A')"
    echo "Total Trades: $(echo $STATS | jq -r '.total_trades' 2>/dev/null || echo 'N/A')"
    echo "Win Rate: $(echo $STATS | jq -r '.portfolio_win_rate' 2>/dev/null || echo 'N/A')%"
    echo "Daily P&L: $(echo $STATS | jq -r '.daily_pnl' 2>/dev/null || echo 'N/A')"
else
    echo "❌ Unable to fetch statistics"
fi
echo ""

# Recent trades
echo "📈 RECENT ACTIVITY (last 10 lines):"
docker logs --tail 10 kael-ultimate-evaluator 2>&1 | grep -E "(WIN|LOSS|📊|Balance)" || echo "No recent activity"
echo ""

echo "=================================="
echo "✅ Status check complete"
echo "=================================="
