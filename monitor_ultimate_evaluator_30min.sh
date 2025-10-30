#!/bin/bash

# ============================================================================
# KAEL Ultimate Strategy Evaluator - 30 Minute Comprehensive Monitor
# ============================================================================
# This script monitors the bot for 30 minutes and ensures:
# 1. All components are working perfectly
# 2. Bot doesn't get stuck
# 3. Bot enters trades at least every 5 minutes
# 4. All services remain healthy
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MONITOR_DURATION_MINUTES=30
CHECK_INTERVAL_SECONDS=30
TRADE_CHECK_INTERVAL_MINUTES=5
API_URL="http://localhost:5001"
COMPOSE_FILE="docker-compose.ultimate-evaluator.yml"

# Tracking variables
START_TIME=$(date +%s)
END_TIME=$((START_TIME + MONITOR_DURATION_MINUTES * 60))
LAST_TRADE_COUNT=0
LAST_TRADE_CHECK_TIME=$START_TIME
CHECKS_PASSED=0
CHECKS_FAILED=0
TRADE_CHECKS_PASSED=0
TRADE_CHECKS_FAILED=0

# Log file
LOG_FILE="logs/monitor_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} ${message}" | tee -a "$LOG_FILE"
}

log_success() {
    log "${GREEN}✅ $1${NC}"
}

log_error() {
    log "${RED}❌ $1${NC}"
}

log_warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    log "${BLUE}ℹ️  $1${NC}"
}

log_header() {
    log ""
    log "${CYAN}$1${NC}"
    log "${CYAN}$(printf '=%.0s' {1..80})${NC}"
}

# ============================================================================
# CHECK FUNCTIONS
# ============================================================================

check_docker_containers() {
    log_header "CHECKING DOCKER CONTAINERS"
    
    local containers=(
        "kael-ultimate-evaluator"
        "kael-timescaledb"
        "kael-prometheus"
        "kael-grafana"
        "kael-dashboard-react"
        "kael-dashboard-angular"
    )
    
    local all_healthy=true
    
    for container in "${containers[@]}"; do
        if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
            
            if [ "$health" = "healthy" ] || [ "$health" = "no-healthcheck" ]; then
                log_success "$container: Running (Health: $health)"
            else
                log_error "$container: Running but unhealthy (Health: $health)"
                all_healthy=false
            fi
        else
            log_error "$container: NOT RUNNING"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        ((CHECKS_PASSED++))
        return 0
    else
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_api_health() {
    log_header "CHECKING API HEALTH"
    
    local response=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>/dev/null || echo "000")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        log_success "Health API responding (HTTP $http_code)"
        ((CHECKS_PASSED++))
        return 0
    else
        log_error "Health API not responding (HTTP $http_code)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_statistics() {
    log_header "CHECKING STATISTICS"
    
    local response=$(curl -s "$API_URL/statistics" 2>/dev/null)
    
    if [ -z "$response" ]; then
        log_error "Failed to fetch statistics"
        ((CHECKS_FAILED++))
        return 1
    fi
    
    # Parse JSON using grep and sed (portable)
    local balance=$(echo "$response" | grep -o '"current_balance":[0-9.]*' | cut -d':' -f2)
    local total_trades=$(echo "$response" | grep -o '"total_trades":[0-9]*' | cut -d':' -f2)
    local win_rate=$(echo "$response" | grep -o '"portfolio_win_rate":[0-9.]*' | cut -d':' -f2)
    local daily_pnl=$(echo "$response" | grep -o '"daily_pnl":-\?[0-9.]*' | cut -d':' -f2)
    local active_strategies=$(echo "$response" | grep -o '"active_strategies":[0-9]*' | cut -d':' -f2)
    
    log_info "Balance: \$$balance"
    log_info "Total Trades: $total_trades"
    log_info "Win Rate: ${win_rate}%"
    log_info "Daily P&L: \$$daily_pnl"
    log_info "Active Strategies: $active_strategies"
    
    # Check if bot is stuck (no new trades)
    if [ "$total_trades" -gt "$LAST_TRADE_COUNT" ]; then
        log_success "Bot is actively trading (new trades detected)"
        LAST_TRADE_COUNT=$total_trades
        LAST_TRADE_CHECK_TIME=$(date +%s)
    fi
    
    ((CHECKS_PASSED++))
    return 0
}

check_strategy_performance() {
    log_header "CHECKING STRATEGY PERFORMANCE"
    
    local response=$(curl -s "$API_URL/strategies" 2>/dev/null)
    
    if [ -z "$response" ]; then
        log_error "Failed to fetch strategy data"
        ((CHECKS_FAILED++))
        return 1
    fi
    
    # Count strategies
    local strategy_count=$(echo "$response" | grep -o '"strategy_name"' | wc -l)
    
    log_info "Active Strategies: $strategy_count"
    
    # Show top 3 strategies by P&L (simplified parsing)
    log_info "Strategy Performance Summary:"
    echo "$response" | grep -o '"strategy_name":"[^"]*"' | head -3 | while read -r line; do
        local strategy=$(echo "$line" | cut -d'"' -f4)
        log_info "  - $strategy"
    done
    
    ((CHECKS_PASSED++))
    return 0
}

check_trade_frequency() {
    log_header "CHECKING TRADE FREQUENCY"
    
    local current_time=$(date +%s)
    local time_since_last_trade=$((current_time - LAST_TRADE_CHECK_TIME))
    local minutes_since_last_trade=$((time_since_last_trade / 60))
    
    log_info "Time since last trade: ${minutes_since_last_trade} minutes"
    
    if [ $time_since_last_trade -gt $((TRADE_CHECK_INTERVAL_MINUTES * 60)) ]; then
        log_warning "No trades in the last $TRADE_CHECK_INTERVAL_MINUTES minutes"
        log_warning "This might indicate the bot is stuck or no opportunities found"
        ((TRADE_CHECKS_FAILED++))
        return 1
    else
        log_success "Trade frequency is acceptable"
        ((TRADE_CHECKS_PASSED++))
        return 0
    fi
}

check_container_logs() {
    log_header "CHECKING CONTAINER LOGS FOR ERRORS"
    
    local container="kael-ultimate-evaluator"
    local error_count=$(docker logs --tail 100 "$container" 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    
    if [ "$error_count" -gt 5 ]; then
        log_warning "Found $error_count errors in recent logs"
        log_info "Last 5 errors:"
        docker logs --tail 100 "$container" 2>&1 | grep -i "error\|exception\|failed" | tail -5 | while read -r line; do
            log_info "  $line"
        done
    else
        log_success "No significant errors in recent logs"
    fi
    
    ((CHECKS_PASSED++))
    return 0
}

check_database_connection() {
    log_header "CHECKING DATABASE CONNECTION"
    
    local db_container="kael-timescaledb"
    
    if docker exec "$db_container" pg_isready -U postgres > /dev/null 2>&1; then
        log_success "Database is accepting connections"
        
        # Check trade count in database
        local trade_count=$(docker exec "$db_container" psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades;" 2>/dev/null | tr -d ' ')
        
        if [ -n "$trade_count" ]; then
            log_info "Trades in database: $trade_count"
        fi
        
        ((CHECKS_PASSED++))
        return 0
    else
        log_error "Database is not accepting connections"
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_dashboards() {
    log_header "CHECKING DASHBOARDS"
    
    # Check React Dashboard
    local react_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
    if [ "$react_status" = "200" ]; then
        log_success "React Dashboard: http://localhost:3000 (HTTP $react_status)"
    else
        log_error "React Dashboard not responding (HTTP $react_status)"
    fi
    
    # Check Angular Dashboard
    local angular_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:4200 2>/dev/null || echo "000")
    if [ "$angular_status" = "200" ]; then
        log_success "Angular Dashboard: http://localhost:4200 (HTTP $angular_status)"
    else
        log_error "Angular Dashboard not responding (HTTP $angular_status)"
    fi
    
    # Check Grafana
    local grafana_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null || echo "000")
    if [ "$grafana_status" = "200" ]; then
        log_success "Grafana Dashboard: http://localhost:3001 (HTTP $grafana_status)"
    else
        log_error "Grafana Dashboard not responding (HTTP $grafana_status)"
    fi
    
    # Check Prometheus
    local prometheus_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9090 2>/dev/null || echo "000")
    if [ "$prometheus_status" = "200" ]; then
        log_success "Prometheus: http://localhost:9090 (HTTP $prometheus_status)"
    else
        log_error "Prometheus not responding (HTTP $prometheus_status)"
    fi
    
    ((CHECKS_PASSED++))
    return 0
}

print_summary() {
    local current_time=$(date +%s)
    local elapsed=$((current_time - START_TIME))
    local elapsed_minutes=$((elapsed / 60))
    local remaining=$((END_TIME - current_time))
    local remaining_minutes=$((remaining / 60))
    
    log_header "MONITORING SUMMARY"
    log_info "Elapsed Time: ${elapsed_minutes} minutes"
    log_info "Remaining Time: ${remaining_minutes} minutes"
    log_info "Checks Passed: $CHECKS_PASSED"
    log_info "Checks Failed: $CHECKS_FAILED"
    log_info "Trade Frequency Checks Passed: $TRADE_CHECKS_PASSED"
    log_info "Trade Frequency Checks Failed: $TRADE_CHECKS_FAILED"
    log_info "Total Trades: $LAST_TRADE_COUNT"
}

# ============================================================================
# MAIN MONITORING LOOP
# ============================================================================

main() {
    log_header "🚀 STARTING 30-MINUTE ULTIMATE EVALUATOR MONITOR"
    log_info "Start Time: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "End Time: $(date -d @$END_TIME '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r $END_TIME '+%Y-%m-%d %H:%M:%S')"
    log_info "Check Interval: ${CHECK_INTERVAL_SECONDS} seconds"
    log_info "Trade Frequency Check: Every ${TRADE_CHECK_INTERVAL_MINUTES} minutes"
    log_info "Log File: $LOG_FILE"
    log ""
    
    # Initial checks
    check_docker_containers
    check_api_health
    check_database_connection
    check_dashboards
    
    log ""
    log_success "Initial checks complete. Starting monitoring loop..."
    log ""
    
    # Main monitoring loop
    while [ $(date +%s) -lt $END_TIME ]; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - START_TIME))
        local elapsed_minutes=$((elapsed / 60))
        
        log_header "CHECK #$((CHECKS_PASSED + CHECKS_FAILED)) - Elapsed: ${elapsed_minutes} minutes"
        
        # Run all checks
        check_docker_containers
        check_api_health
        check_statistics
        check_strategy_performance
        check_trade_frequency
        check_container_logs
        check_database_connection
        
        # Print summary
        print_summary
        
        # Wait for next check
        log ""
        log_info "Waiting ${CHECK_INTERVAL_SECONDS} seconds until next check..."
        log ""
        sleep $CHECK_INTERVAL_SECONDS
    done
    
    # Final summary
    log_header "🏁 30-MINUTE MONITORING COMPLETE"
    log_info "End Time: $(date '+%Y-%m-%d %H:%M:%S')"
    print_summary
    
    # Final statistics
    log ""
    log_header "FINAL STATISTICS"
    check_statistics
    check_strategy_performance
    
    # Generate report
    log ""
    log_header "📊 GENERATING FINAL REPORT"
    
    local success_rate=$((CHECKS_PASSED * 100 / (CHECKS_PASSED + CHECKS_FAILED)))
    
    log_info "Overall Success Rate: ${success_rate}%"
    
    if [ $CHECKS_FAILED -eq 0 ] && [ $TRADE_CHECKS_FAILED -eq 0 ]; then
        log_success "ALL CHECKS PASSED! Bot is working perfectly."
    elif [ $CHECKS_FAILED -lt 5 ]; then
        log_warning "Some checks failed, but bot is mostly operational."
    else
        log_error "Multiple checks failed. Bot may have issues."
    fi
    
    log ""
    log_info "Full log saved to: $LOG_FILE"
    log ""
    log_success "Monitoring complete!"
}

# Trap Ctrl+C
trap 'log_warning "Monitoring interrupted by user"; exit 130' INT

# Run main function
main

exit 0
