#!/bin/bash
# ============================================================================
# KAEL Autonomous Parallel Trading Bot - Stop Script
# ============================================================================

echo "============================================================================"
echo "🛑 STOPPING KAEL PARALLEL TRADING BOT"
echo "============================================================================"
echo ""

# Check if container is running
if ! docker ps | grep -q "kael-parallel-trading-bot"; then
    echo "ℹ️  Bot is not running"
    exit 0
fi

# Get final statistics before stopping
echo "📊 Fetching final statistics..."
curl -s http://localhost:5001/statistics 2>/dev/null | python3 -m json.tool || echo "   (Statistics unavailable)"
echo ""

# Stop the container gracefully
echo "🛑 Stopping container..."
docker-compose -f docker-compose.parallel.yml stop parallel-trading-bot

if [ $? -eq 0 ]; then
    echo "✅ Container stopped successfully"
else
    echo "⚠️  Warning: Failed to stop container gracefully, forcing stop..."
    docker-compose -f docker-compose.parallel.yml down
fi

echo ""
echo "============================================================================"
echo "✅ PARALLEL TRADING BOT STOPPED"
echo "============================================================================"
echo ""
echo "📁 Logs are preserved in: ./logs/"
echo ""
echo "🔄 To restart: ./start_parallel_bot.sh"
echo "🗑️  To remove completely: docker-compose -f docker-compose.parallel.yml down -v"
