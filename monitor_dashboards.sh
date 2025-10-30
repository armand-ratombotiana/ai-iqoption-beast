#!/bin/bash
# KAEL Dashboard Monitoring Script
# Tests both React and Angular dashboards and the ultimate-evaluator backend

echo "=================================================="
echo "KAEL Ultimate Strategy Evaluator - Dashboard Monitor"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local timeout=${3:-5}

    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" --max-time $timeout "$url" 2>/dev/null)
    http_code=$(echo $response | cut -d'|' -f1)
    time_total=$(echo $response | cut -d'|' -f2)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (${time_total}s)"
        return 0
    elif [ "$http_code" = "000" ]; then
        echo -e "${RED}✗ TIMEOUT/UNREACHABLE${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠ HTTP $http_code${NC} (${time_total}s)"
        return 1
    fi
}

# Test Container Status
echo "1. Container Status:"
echo "-------------------"
docker ps --filter "name=kael" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker error"
echo ""

# Test Dashboards
echo "2. Dashboard Frontend Status:"
echo "-----------------------------"
test_endpoint "React Dashboard (port 3000)" "http://localhost:3000" 3
test_endpoint "Angular Dashboard (port 4200)" "http://localhost:4200" 3
echo ""

# Test Backend API
echo "3. Backend API Endpoints:"
echo "-------------------------"
test_endpoint "Health Check" "http://localhost:5001/health" 3
test_endpoint "Statistics (React)" "http://localhost:5001/statistics" 10
test_endpoint "Performance (Angular)" "http://localhost:5001/performance" 10
test_endpoint "Strategies" "http://localhost:5001/strategies" 10
test_endpoint "Config" "http://localhost:5001/config" 5
test_endpoint "Recent Trades" "http://localhost:5001/recent_trades?limit=5" 10
test_endpoint "Strategy Stats" "http://localhost:5001/strategy_stats" 10
test_endpoint "Prometheus Metrics" "http://localhost:5001/metrics" 5
echo ""

# Test Monitoring Stack
echo "4. Monitoring Stack:"
echo "-------------------"
test_endpoint "Prometheus" "http://localhost:9090" 3
test_endpoint "Grafana" "http://localhost:3001" 3
echo ""

# Check for queue warnings in logs
echo "5. Recent Backend Logs:"
echo "----------------------"
echo "Checking for waitress queue warnings..."
queue_warnings=$(docker logs --tail 100 kael-ultimate-evaluator 2>&1 | grep -c "Task queue depth")
if [ "$queue_warnings" -gt 0 ]; then
    echo -e "${RED}⚠ Found $queue_warnings queue warnings in last 100 log lines${NC}"
    docker logs --tail 20 kael-ultimate-evaluator 2>&1 | grep "Task queue depth" | tail -5
else
    echo -e "${GREEN}✓ No queue warnings${NC}"
fi
echo ""

# Check recent trades
echo "6. Recent Trading Activity:"
echo "---------------------------"
docker logs --tail 30 kael-ultimate-evaluator 2>&1 | grep -E "WIN|LOSS" | tail -5
echo ""

echo "=================================================="
echo "Dashboard URLs:"
echo "  React:      http://localhost:3000"
echo "  Angular:    http://localhost:4200"
echo "  Grafana:    http://localhost:3001 (admin/admin)"
echo "  Prometheus: http://localhost:9090"
echo "=================================================="
