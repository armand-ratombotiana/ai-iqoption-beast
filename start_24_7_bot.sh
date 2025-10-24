#!/bin/bash
################################################################################
# AUTONOMOUS 24/7 TRADING BOT - STARTUP SCRIPT
################################################################################
# This script starts the trading bot with proper environment setup
# and ensures it keeps running 24/7 with auto-restart capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}🤖 AUTONOMOUS 24/7 BINARY OPTIONS TRADING BOT${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_warning "Creating .env from .env.production.example..."
    cp .env.production.example .env
    print_warning "Please edit .env file with your credentials before running the bot"
    print_warning "Command: nano .env"
    exit 1
fi

print_status ".env file found"

# Load environment variables
set -a
source .env
set +a

# Check critical environment variables
if [ -z "$IQOPTION_EMAIL" ] || [ "$IQOPTION_EMAIL" = "your_email@example.com" ]; then
    print_error "IQOPTION_EMAIL not configured in .env"
    exit 1
fi

if [ -z "$IQOPTION_PASSWORD" ] || [ "$IQOPTION_PASSWORD" = "your_password" ]; then
    print_error "IQOPTION_PASSWORD not configured in .env"
    exit 1
fi

print_status "Credentials configured"

# Check trading mode
TRADING_MODE=${TRADING_MODE:-demo}
if [ "$TRADING_MODE" = "live" ]; then
    echo ""
    echo -e "${RED}================================================================================================${NC}"
    echo -e "${RED}⚠️  WARNING: LIVE TRADING MODE ENABLED${NC}"
    echo -e "${RED}⚠️  THIS BOT WILL TRADE WITH REAL MONEY${NC}"
    echo -e "${RED}⚠️  LOSSES ARE REAL AND PERMANENT${NC}"
    echo -e "${RED}================================================================================================${NC}"
    echo ""
    read -p "Are you ABSOLUTELY SURE you want to proceed with LIVE trading? (type 'YES' in capital letters): " confirmation
    if [ "$confirmation" != "YES" ]; then
        print_error "Live trading cancelled by user"
        exit 1
    fi
else
    print_status "Demo mode enabled (safe)"
fi

# Create logs directory
mkdir -p logs
print_status "Logs directory created/verified"

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
print_status "Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Install/upgrade dependencies
print_status "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_status "Dependencies installed"

# Remove emergency stop file if exists (fresh start)
if [ -f "EMERGENCY_STOP" ]; then
    print_warning "Removing existing EMERGENCY_STOP file"
    rm EMERGENCY_STOP
fi

# Print configuration
echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}⚙️  CONFIGURATION${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo "Trading Mode: $TRADING_MODE"
echo "Base Trade Amount: \$${BASE_TRADE_AMOUNT:-1.0}"
echo "Max Daily Loss: \$${MAX_DAILY_LOSS:-50}"
echo "Max Daily Profit: \$${MAX_DAILY_PROFIT:-100}"
echo "Martingale: ${ENABLE_MARTINGALE:-true}"
echo "Max Consecutive Losses: ${MAX_CONSECUTIVE_LOSSES:-5}"
echo "Health API Port: ${HEALTH_API_PORT:-5001}"
echo "Log Level: ${LOG_LEVEL:-INFO}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Function to run the bot with auto-restart
run_bot_with_restart() {
    local restart_count=0
    local max_restarts=${MAX_RESTART_ATTEMPTS:-100}
    local restart_delay=${RESTART_DELAY_SECONDS:-60}

    while true; do
        echo ""
        echo -e "${GREEN}================================================================================================${NC}"
        echo -e "${GREEN}🚀 Starting Trading Bot (Attempt $(($restart_count + 1)))${NC}"
        echo -e "${GREEN}================================================================================================${NC}"
        echo ""

        # Run the bot
        python3 autonomous_trading_bot_24_7.py

        # Check exit code
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            # Normal shutdown
            print_status "Bot shutdown normally"
            break
        else
            # Error occurred
            restart_count=$((restart_count + 1))
            print_error "Bot crashed with exit code: $exit_code"

            # Check if emergency stop file exists
            if [ -f "EMERGENCY_STOP" ]; then
                print_warning "EMERGENCY STOP file detected. Halting all restarts."
                break
            fi

            # Check restart limit
            if [ $restart_count -ge $max_restarts ]; then
                print_error "Maximum restart attempts ($max_restarts) reached. Stopping."
                break
            fi

            print_warning "Auto-restarting in ${restart_delay} seconds... (Restart $restart_count/$max_restarts)"
            sleep $restart_delay
        fi
    done
}

# Set up signal handlers for graceful shutdown
trap 'echo ""; print_warning "Shutdown signal received. Stopping bot gracefully..."; exit 0' SIGINT SIGTERM

# Start the bot
echo ""
print_status "Starting autonomous trading bot..."
print_warning "Press Ctrl+C to stop the bot gracefully"
print_warning "Or create EMERGENCY_STOP file: touch EMERGENCY_STOP"
echo ""

run_bot_with_restart

echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}🏁 Trading Bot Stopped${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""
echo "Check logs in: ${PROJECT_ROOT}/logs/"
echo "Latest log: logs/autonomous_bot_$(date +%Y%m%d).log"
echo ""

# Deactivate virtual environment
deactivate
