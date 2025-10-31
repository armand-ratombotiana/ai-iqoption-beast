#!/bin/bash

# Dashboard Monitoring Script
# Monitors both React and Angular dashboards plus API endpoints

echo "=================================================="
echo "KAEL Trading System - Dashboard Monitor"
echo "=================================================="
echo ""
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local timeout="${3:-5}"
    
    response=$(timeout $timeout curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ $name${NC} - HTTP $response - $url"
        return 0
    else
        echo -e "${RED}❌ $name${NC} - HTTP $response - $url"
        return 1
    fi
}

# Test main dashboards
echo "📊 DASHBOARD STATUS"
echo "--------------------------------------------------"
test_endpoint "Angular Dashboard" "http://localhost:4200"
test_endpoint "React Dashboard" "http://localhost:3000"
echo ""

# Test monitoring tools
echo "📈 MONITORING TOOLS"
echo "--------------------------------------------------"
test_endpoint "Prometheus" "http://localhost:9090"
test_endpoint "Grafana" "http://localhost:3001"
echo ""

# Test API endpoints
echo "🔌 API ENDPOINTS"
echo "--------------------------------------------------"
test_endpoint "Health API" "http://localhost:5001/health"
test_endpoint "Statistics API" "http://localhost:5001/statistics"
test_endpoint "Performance API" "http://localhost:5001/performance"
test_endpoint "Strategies API" "http://localhost:5001/strategies"
test_endpoint "Recent Trades API" "http://localhost:5001/recent_trades?limit=5"
test_endpoint "Config API" "http://localhost:5001/config"
echo ""

# Test database
echo "🗄️  DATABASE"
echo "--------------------------------------------------"
db_status=$(docker exec kael-timescaledb pg_isready -U postgres 2>&1 | grep -q "accepting connections" && echo "healthy" || echo "unhealthy")
if [ "$db_status" = "healthy" ]; then
    echo -e "${GREEN}✅ TimescaleDB${NC} - accepting connections"
    
    # Get trade count
    trade_count=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades;" 2>/dev/null | tr -d ' ')
    echo "   📊 Total trades: $trade_count"
    
    # Get view count
    view_count=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM information_schema.views WHERE table_schema='public';" 2>/dev/null | tr -d ' ')
    echo "   👁️  Database views: $view_count"
else
    echo -e "${RED}❌ TimescaleDB${NC} - not responding"
fi
echo ""

# Container status
echo "🐳 CONTAINER STATUS"
echo "--------------------------------------------------"
docker ps --filter "name=kael" --format "table {{.Names}}\t{{.Status}}" | grep -v "NAMES"
echo ""

# Active strategies
echo "🎯 ACTIVE STRATEGIES"
echo "--------------------------------------------------"
strategies=$(docker logs kael-ultimate-evaluator 2>&1 | grep "Strategy thread started" | tail -7 | awk -F': ' '{print $NF}' | sort -u)
if [ ! -z "$strategies" ]; then
    echo "$strategies" | while read strategy; do
        echo -e "${GREEN}✅${NC} $strategy"
    done
else
    echo -e "${YELLOW}⚠️  No strategy threads detected in logs${NC}"
fi
echo ""

# Recent trading activity  
echo "💹 RECENT TRADING ACTIVITY (Last 5 entries)"
echo "--------------------------------------------------"
docker logs kael-ultimate-evaluator 2>&1 | grep -E "(WIN|LOSS|Trade)" | tail -5
echo ""

echo "=================================================="
echo "Monitoring complete at $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="
