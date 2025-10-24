#!/bin/bash

# =============================================================================
# Enhanced Real-time Parallel Trading Bot Monitor
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

CONTAINER_NAME="kael-parallel-trading-bot"
API_URL="http://localhost:5001"
LOG_FILE="logs/binary_bot_$(date +%Y%m%d).log"

# Function to check if container is running
check_container() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

# Function to get container status
get_container_status() {
    if check_container; then
        echo -e "${GREEN}✅ Running${NC}"
    else
        echo -e "${RED}❌ Stopped${NC}"
    fi
}

# Function to get container uptime
get_container_uptime() {
    if check_container; then
        docker inspect --format='{{.State.StartedAt}}' ${CONTAINER_NAME} 2>/dev/null | xargs -I {} date -d {} +%s 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Function to show header
show_header() {
    clear
    echo "=========================================================================="
    echo -e "  ${CYAN}🤖 KAEL PARALLEL TRADING BOT - LIVE MONITOR${NC}"
    echo "=========================================================================="
    echo -e "  ${BLUE}Time:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "  ${BLUE}Container:${NC} $(get_container_status)"
    echo "=========================================================================="
    echo ""
}

# Function to show statistics from API
show_api_stats() {
    if curl -s --max-time 2 ${API_URL}/statistics > /tmp/bot_stats.json 2>&1; then
        python3 << 'EOF'
import json
import sys
from datetime import datetime

try:
    with open('/tmp/bot_stats.json', 'r') as f:
        stats = json.load(f)

    # Colors
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'

    # Account Status
    print(f"{CYAN}🏦 ACCOUNT STATUS{NC}")
    print(f"   Mode: {YELLOW}{stats.get('mode', 'N/A').upper()}{NC}")
    print(f"   Balance: {GREEN}${stats.get('balance', 0):.2f}{NC}")
    
    daily_net = stats.get('daily_net', 0)
    net_color = GREEN if daily_net >= 0 else RED
    print(f"   Daily P/L: {net_color}${daily_net:+.2f}{NC}")
    print()

    # Trading Statistics
    print(f"{CYAN}📊 TRADING STATISTICS{NC}")
    print(f"   Trades Today: {stats.get('trades_today', 0)}")
    print(f"   Wins: {GREEN}{stats.get('wins_today', 0)}{NC}")
    print(f"   Losses: {RED}{stats.get('losses_today', 0)}{NC}")
    
    win_rate = stats.get('win_rate', 0)
    wr_color = GREEN if win_rate >= 55 else YELLOW if win_rate >= 45 else RED
    print(f"   Win Rate: {wr_color}{win_rate:.1f}%{NC}")
    print()

    # Parallel Trading Status
    print(f"{CYAN}🔄 PARALLEL TRADING{NC}")
    active_instruments = stats.get('active_instruments', [])
    print(f"   Active Instruments: {YELLOW}{len(active_instruments)}{NC}/{stats.get('active_count', 0)}")
    if active_instruments:
        print(f"   Trading: {', '.join(active_instruments[:5])}")
    print(f"   Total Risk Allocated: ${stats.get('total_risk_allocated', 0):.2f}")
    print()

    # Performance Metrics
    print(f"{CYAN}⚡ PERFORMANCE{NC}")
    print(f"   Daily Profit: {GREEN}${stats.get('daily_profit', 0):.2f}{NC}")
    print(f"   Daily Loss: {RED}${stats.get('daily_loss', 0):.2f}{NC}")
    print(f"   Total Trades (All Time): {stats.get('total_trades_all_time', 0)}")
    
    uptime = stats.get('uptime_hours', 0)
    print(f"   Uptime: {uptime:.2f} hours")
    
    avg_scan = stats.get('avg_scan_time_ms', 0)
    avg_exec = stats.get('avg_execution_time_ms', 0)
    print(f"   Avg Scan Time: {avg_scan:.0f}ms")
    print(f"   Avg Execution Time: {avg_exec:.0f}ms")
    print()

    # Top Performing Instruments
    instrument_stats = stats.get('instrument_stats', [])
    if instrument_stats:
        print(f"{CYAN}🏆 TOP PERFORMING INSTRUMENTS{NC}")
        for i, inst in enumerate(instrument_stats[:5], 1):
            profit = inst.get('profit', 0)
            profit_color = GREEN if profit >= 0 else RED
            win_rate = inst.get('win_rate', 0)
            wr_color = GREEN if win_rate >= 55 else YELLOW if win_rate >= 45 else RED
            
            print(f"   {i}. {inst.get('instrument', 'N/A')}: "
                  f"{profit_color}${profit:+.2f}{NC} | "
                  f"{wr_color}{win_rate:.1f}%{NC} WR | "
                  f"{inst.get('total_trades', 0)} trades")
        print()

    # System Status
    print(f"{CYAN}🔧 SYSTEM STATUS{NC}")
    status = stats.get('status', 'unknown')
    status_color = GREEN if status == 'running' else RED
    print(f"   Status: {status_color}{status.upper()}{NC}")
    print(f"   Operation Mode: {stats.get('operation_mode', 'N/A')}")
    print(f"   Reconnects: {stats.get('reconnect_count', 0)}")
    print()

except Exception as e:
    print(f"{RED}❌ Error parsing stats: {e}{NC}")
EOF
    else
        echo -e "${RED}❌ Cannot connect to bot API (${API_URL})${NC}"
        echo "   Is the bot running?"
        echo ""
    fi
}

# Function to show recent logs
show_recent_logs() {
    echo "=========================================================================="
    echo -e "${CYAN}📝 RECENT LOGS (Last 10 lines)${NC}"
    echo "=========================================================================="
    
    if check_container; then
        docker logs --tail 10 ${CONTAINER_NAME} 2>&1 | tail -10
    else
        echo -e "${RED}Container not running${NC}"
    fi
    
    echo ""
}

# Function to show container stats
show_container_stats() {
    echo "=========================================================================="
    echo -e "${CYAN}🐳 CONTAINER STATS${NC}"
    echo "=========================================================================="
    
    if check_container; then
        docker stats ${CONTAINER_NAME} --no-stream --format "   CPU: {{.CPUPerc}}\n   Memory: {{.MemUsage}}\n   Network I/O: {{.NetIO}}"
    else
        echo -e "${RED}Container not running${NC}"
    fi
    
    echo ""
}

# Function to show menu
show_menu() {
    echo "=========================================================================="
    echo -e "${YELLOW}COMMANDS:${NC}"
    echo "  [r] Refresh now"
    echo "  [l] Show full logs"
    echo "  [s] Stop bot"
    echo "  [t] Restart bot"
    echo "  [q] Quit monitor"
    echo "=========================================================================="
}

# Function to handle user input
handle_input() {
    read -t 1 -n 1 key
    case $key in
        r|R)
            return 0
            ;;
        l|L)
            clear
            echo "=========================================================================="
            echo -e "${CYAN}📝 FULL LOGS${NC}"
            echo "=========================================================================="
            docker logs ${CONTAINER_NAME} 2>&1 | tail -50
            echo ""
            echo "Press any key to return..."
            read -n 1
            ;;
        s|S)
            echo ""
            echo -e "${YELLOW}Stopping bot...${NC}"
            docker-compose -f docker-compose.parallel.yml stop
            echo -e "${GREEN}Bot stopped${NC}"
            sleep 2
            ;;
        t|T)
            echo ""
            echo -e "${YELLOW}Restarting bot...${NC}"
            docker-compose -f docker-compose.parallel.yml restart
            echo -e "${GREEN}Bot restarted${NC}"
            sleep 2
            ;;
        q|Q)
            clear
            echo -e "${GREEN}Monitor stopped${NC}"
            exit 0
            ;;
    esac
}

# Main monitoring loop
main() {
    echo "=========================================================================="
    echo -e "  ${CYAN}🚀 Starting KAEL Parallel Trading Bot Monitor${NC}"
    echo "=========================================================================="
    sleep 2

    while true; do
        show_header
        show_api_stats
        show_container_stats
        show_recent_logs
        show_menu
        
        # Wait for input or auto-refresh after 10 seconds
        for i in {1..10}; do
            handle_input
            sleep 1
        done
    done
}

# Run main function
main
