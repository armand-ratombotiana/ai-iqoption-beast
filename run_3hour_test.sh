#!/bin/bash

# =============================================================================
# KAEL 3-HOUR PRE-LIVE TRADING TEST
# =============================================================================
# Purpose: Verify system readiness for $100 live trading next week
# Duration: 3 hours (180 minutes)
# Mode: DEMO (safe testing)
# =============================================================================

TEST_DURATION_MINUTES=180
TEST_START=$(date +%s)
TEST_END=$((TEST_START + TEST_DURATION_MINUTES * 60))
REPORT_FILE="reports/3hour_test_report_$(date +%Y%m%d_%H%M%S).md"
LOG_FILE="logs/3hour_test_log_$(date +%Y%m%d_%H%M%S).log"

# Create directories if they don't exist
mkdir -p reports logs

echo "=================================================="
echo "KAEL 3-HOUR PRE-LIVE TRADING TEST"
echo "=================================================="
echo ""
echo "Test Start Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Duration: $TEST_DURATION_MINUTES minutes (3 hours)"
echo "Mode: DEMO (Safe Testing)"
echo ""
echo "Report will be saved to: $REPORT_FILE"
echo "Logs will be saved to: $LOG_FILE"
echo ""
echo "=================================================="
echo ""

# Initialize counters
total_checks=0
passed_checks=0
failed_checks=0

# Function to log
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check system health
check_system_health() {
    log_message "Checking system health..."

    # Check containers
    containers_up=$(docker ps --filter "name=kael" --format "{{.Names}}" | wc -l)
    if [ $containers_up -ge 4 ]; then
        log_message "✅ All containers running ($containers_up active)"
        ((passed_checks++))
    else
        log_message "❌ Some containers are down (only $containers_up active)"
        ((failed_checks++))
    fi
    ((total_checks++))

    # Check API health
    api_status=$(curl -s http://localhost:5001/health 2>&1 | grep -o '"status":"ok"' || echo "fail")
    if [ "$api_status" != "fail" ]; then
        log_message "✅ API health check passed"
        ((passed_checks++))
    else
        log_message "❌ API health check failed"
        ((failed_checks++))
    fi
    ((total_checks++))

    # Check database
    db_status=$(docker exec kael-timescaledb pg_isready -U postgres 2>&1 | grep -q "accepting connections" && echo "ok" || echo "fail")
    if [ "$db_status" = "ok" ]; then
        log_message "✅ Database is healthy"
        ((passed_checks++))
    else
        log_message "❌ Database connection failed"
        ((failed_checks++))
    fi
    ((total_checks++))
}

# Function to get trading statistics
get_trading_stats() {
    trade_count=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades WHERE entry_time >= NOW() - INTERVAL '3 hours';" 2>/dev/null | tr -d ' ' || echo "0")
    win_count=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades WHERE entry_time >= NOW() - INTERVAL '3 hours' AND result='win';" 2>/dev/null | tr -d ' ' || echo "0")
    loss_count=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades WHERE entry_time >= NOW() - INTERVAL '3 hours' AND result='loss';" 2>/dev/null | tr -d ' ' || echo "0")

    if [ "$trade_count" -gt 0 ]; then
        win_rate=$(echo "scale=2; $win_count * 100 / $trade_count" | bc)
    else
        win_rate="0.00"
    fi

    log_message "📊 Trading Stats: $trade_count trades | Wins: $win_count | Losses: $loss_count | Win Rate: ${win_rate}%"
}

# Main monitoring loop
log_message "🚀 Starting 3-hour test run..."
check_interval=300  # Check every 5 minutes

iteration=0
while [ $(date +%s) -lt $TEST_END ]; do
    current_time=$(date +%s)
    elapsed=$((($current_time - $TEST_START) / 60))
    remaining=$((($TEST_END - $current_time) / 60))
    progress=$((elapsed * 100 / TEST_DURATION_MINUTES))

    ((iteration++))
    log_message "=== Check #$iteration - ${elapsed}min elapsed, ${remaining}min remaining ($progress%) ==="

    # Perform health checks
    check_system_health
    get_trading_stats

    # Wait for next check
    sleep_time=$check_interval
    if [ $((current_time + sleep_time)) -gt $TEST_END ]; then
        sleep_time=$(($TEST_END - $current_time))
    fi

    if [ $sleep_time -gt 0 ]; then
        log_message "Next check in $(($sleep_time / 60)) minutes..."
        sleep $sleep_time
    fi
done

# Generate final report
log_message "🏁 Test completed! Generating final report..."

final_trades=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades WHERE entry_time >= NOW() - INTERVAL '3 hours';" 2>/dev/null | tr -d ' ' || echo "0")
final_wins=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades WHERE entry_time >= NOW() - INTERVAL '3 hours' AND result='win';" 2>/dev/null | tr -d ' ' || echo "0")
final_losses=$(docker exec kael-timescaledb psql -U postgres -d kael -t -c "SELECT COUNT(*) FROM trades WHERE entry_time >= NOW() - INTERVAL '3 hours' AND result='loss';" 2>/dev/null | tr -d ' ' || echo "0")

if [ "$final_trades" -gt 0 ]; then
    final_win_rate=$(echo "scale=2; $final_wins * 100 / $final_trades" | bc)
else
    final_win_rate="0.00"
fi

success_rate=$(echo "scale=2; $passed_checks * 100 / $total_checks" | bc)

cat > "$REPORT_FILE" << 'REPORT_END'
# KAEL 3-Hour Pre-Live Trading Test Report

**Test Date:** $(date '+%Y-%m-%d')
**Duration:** 3 hours (180 minutes)
**Mode:** DEMO

---

## Executive Summary

This test was performed to verify system readiness for live trading with $100 next week.

### System Health Results

- **Total Health Checks:** $total_checks
- **Passed:** $passed_checks ✅
- **Failed:** $failed_checks ❌
- **Success Rate:** ${success_rate}%

### Trading Performance

- **Total Trades:** $final_trades
- **Wins:** $final_wins
- **Losses:** $final_losses
- **Win Rate:** ${final_win_rate}%

---

## Recommendations for Live Trading

### ✅ System is Ready If:
1. Health check success rate > 95%
2. No critical errors detected
3. All strategies performed as expected
4. System remained stable throughout

### Risk Management Settings for $100 Live Trading

Recommended conservative settings:
```bash
BASE_TRADE_AMOUNT=1.0           # $1 per trade (1% of capital)
MAX_DAILY_LOSS=5.0              # Stop at $5 loss (5% max drawdown)
MAX_CONSECUTIVE_LOSSES=3        # Stop after 3 consecutive losses
MIN_BALANCE=95.0                # Stop if balance drops below $95
MAX_TRADES_PER_DAY=20          # Maximum 20 trades per day
MIN_AI_CONFIDENCE=75            # Increase confidence threshold to 75%
```

---

## Next Steps

1. **Review both dashboards:**
   - Angular: http://localhost:4200
   - React: http://localhost:3000

2. **Check detailed logs:** $LOG_FILE

3. **If all tests passed:**
   - Update .env: `TRADING_MODE=live`
   - Verify IQ Option credentials
   - Ensure $100 is in live account
   - Start with conservative risk settings

4. **Monitor closely for first week:**
   - Use monitoring script: ./monitor_dashboards.sh
   - Check dashboards regularly
   - Review trades daily

---

**Report Generated:** $(date '+%Y-%m-%d %H:%M:%S')
**Log File:** $LOG_FILE
REPORT_END

echo ""
echo "=================================================="
echo "✅ TEST COMPLETED!"
echo "=================================================="
echo ""
echo "📄 Full report: $REPORT_FILE"
echo "📋 Detailed logs: $LOG_FILE"
echo ""
echo "Summary:"
echo "  Health Checks: $passed_checks/$total_checks passed ($success_rate%)"
echo "  Trades: $final_trades total | Win Rate: $final_win_rate%"
echo ""

cat "$REPORT_FILE"
