#!/bin/bash
# 2-Hour Comprehensive Monitoring Script
# Monitors trading bot, logs activity, tracks performance

LOG_DIR="logs/monitoring"
SESSION_START=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/session_${SESSION_START}.log"
STATS_FILE="${LOG_DIR}/stats_${SESSION_START}.csv"

# Create log directory
mkdir -p ${LOG_DIR}

# Initialize stats CSV
echo "timestamp,balance,trades_today,win_rate,daily_profit,active_count,reconnect_count,status" > ${STATS_FILE}

echo "========================================" | tee -a ${LOG_FILE}
echo "2-HOUR MONITORING SESSION STARTED" | tee -a ${LOG_FILE}
echo "Start Time: $(date)" | tee -a ${LOG_FILE}
echo "Session: ${SESSION_START}" | tee -a ${LOG_FILE}
echo "========================================" | tee -a ${LOG_FILE}

# Function to log statistics
log_stats() {
    TIMESTAMP=$(date +%Y-%m-%d_%H:%M:%S)
    STATS=$(curl -s http://localhost:5001/statistics 2>/dev/null)

    if [ $? -eq 0 ]; then
        BALANCE=$(echo $STATS | python -c "import sys, json; print(json.load(sys.stdin)['balance'])" 2>/dev/null)
        TRADES=$(echo $STATS | python -c "import sys, json; print(json.load(sys.stdin)['trades_today'])" 2>/dev/null)
        WIN_RATE=$(echo $STATS | python -c "import sys, json; print(json.load(sys.stdin)['win_rate'])" 2>/dev/null)
        PROFIT=$(echo $STATS | python -c "import sys, json; print(json.load(sys.stdin)['daily_net'])" 2>/dev/null)
        ACTIVE=$(echo $STATS | python -c "import sys, json; print(json.load(sys.stdin)['active_count'])" 2>/dev/null)
        RECONNECTS=$(echo $STATS | python -c "import sys, json; print(json.load(sys.stdin)['reconnect_count'])" 2>/dev/null)
        STATUS=$(echo $STATS | python -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

        echo "${TIMESTAMP},${BALANCE},${TRADES},${WIN_RATE},${PROFIT},${ACTIVE},${RECONNECTS},${STATUS}" >> ${STATS_FILE}
        echo "[$(date +%H:%M:%S)] Balance: \$${BALANCE} | Trades: ${TRADES} | Win Rate: ${WIN_RATE}% | Profit: +\$${PROFIT}" | tee -a ${LOG_FILE}
    else
        echo "[$(date +%H:%M:%S)] ERROR: Failed to fetch statistics" | tee -a ${LOG_FILE}
    fi
}

# Function to check for errors
check_errors() {
    ERRORS=$(docker logs kael-parallel-trading-bot --since 5m 2>&1 | grep -i "error\|warning\|failed\|buy late" | wc -l)
    if [ $ERRORS -gt 0 ]; then
        echo "[$(date +%H:%M:%S)] ⚠️  WARNING: ${ERRORS} errors detected in last 5 minutes" | tee -a ${LOG_FILE}
        docker logs kael-parallel-trading-bot --since 5m 2>&1 | grep -i "error\|warning\|failed\|buy late" | tail -5 | tee -a ${LOG_FILE}
    fi
}

# Monitor for 2 hours (120 minutes)
END_TIME=$(($(date +%s) + 7200))  # 2 hours = 7200 seconds
ITERATION=0

while [ $(date +%s) -lt $END_TIME ]; do
    ITERATION=$((ITERATION + 1))
    REMAINING=$((($END_TIME - $(date +%s)) / 60))

    echo "" | tee -a ${LOG_FILE}
    echo "=== Check #${ITERATION} | ${REMAINING} minutes remaining ===" | tee -a ${LOG_FILE}

    # Log current stats
    log_stats

    # Check for errors
    check_errors

    # Check container health
    CONTAINER_STATUS=$(docker ps --filter "name=kael-parallel-trading-bot" --format "{{.Status}}")
    if [ -z "$CONTAINER_STATUS" ]; then
        echo "[$(date +%H:%M:%S)] 🚨 CRITICAL: Container is not running!" | tee -a ${LOG_FILE}
        break
    fi

    # Sleep for 5 minutes before next check (2 hours / 5 min = 24 checks)
    sleep 300
done

# Final report
echo "" | tee -a ${LOG_FILE}
echo "========================================" | tee -a ${LOG_FILE}
echo "2-HOUR MONITORING SESSION COMPLETED" | tee -a ${LOG_FILE}
echo "End Time: $(date)" | tee -a ${LOG_FILE}
echo "========================================" | tee -a ${LOG_FILE}

# Get final statistics
FINAL_STATS=$(curl -s http://localhost:5001/statistics)
echo "" | tee -a ${LOG_FILE}
echo "FINAL STATISTICS:" | tee -a ${LOG_FILE}
echo $FINAL_STATS | python -m json.tool | tee -a ${LOG_FILE}

echo "" | tee -a ${LOG_FILE}
echo "Log file: ${LOG_FILE}" | tee -a ${LOG_FILE}
echo "Stats CSV: ${STATS_FILE}" | tee -a ${LOG_FILE}
echo "========================================" | tee -a ${LOG_FILE}
