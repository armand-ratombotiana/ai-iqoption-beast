#!/bin/bash

# KAEL Ultimate Strategy Evaluator - Quick Monitoring Script
# Run this to check system status at any time

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     KAEL ULTIMATE STRATEGY EVALUATOR - QUICK STATUS CHECK       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check Docker containers
echo "📦 CONTAINERS:"
docker ps --filter "name=kael" --format "  {{.Names}}: {{.Status}}" 2>/dev/null || echo "  ❌ Docker not running"
echo ""

# Test API endpoints
echo "🔌 API STATUS:"
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "  ✅ Ultimate Evaluator API: ONLINE"
else
    echo "  ❌ Ultimate Evaluator API: OFFLINE"
fi

if curl -s http://localhost:4200 > /dev/null 2>&1; then
    echo "  ✅ Enhanced Dashboard: ACCESSIBLE"
else
    echo "  ❌ Enhanced Dashboard: NOT ACCESSIBLE"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ React Dashboard: ACCESSIBLE"
else
    echo "  ❌ React Dashboard: NOT ACCESSIBLE"
fi
echo ""

# Get current performance
echo "📊 CURRENT PERFORMANCE:"
PERF=$(curl -s http://localhost:5001/performance 2>/dev/null)
if [ ! -z "$PERF" ]; then
    echo "$PERF" | python3 -m json.tool 2>/dev/null | head -15
else
    echo "  ❌ Unable to fetch performance data"
fi
echo ""

# Get recent logs
echo "📝 RECENT ACTIVITY (Last 10 lines):"
docker logs kael-ultimate-evaluator --tail 10 2>/dev/null || echo "  ❌ Cannot access logs"
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Dashboard: http://localhost:4200                               ║"
echo "║  API: http://localhost:5001                                     ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
