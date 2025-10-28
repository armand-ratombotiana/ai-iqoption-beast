#!/bin/bash

# =============================================================================
# KAEL Strategy-Per-Thread Trading Bot - Quick Start Script
# =============================================================================

set -e

echo "================================================================================"
echo "🚀 KAEL STRATEGY-PER-THREAD TRADING BOT"
echo "================================================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with your credentials"
    exit 1
fi

# Source environment variables
source .env

# Check credentials
if [ -z "$IQOPTION_EMAIL" ] || [ -z "$IQOPTION_PASSWORD" ]; then
    echo "❌ Error: Missing IQ Option credentials in .env"
    exit 1
fi

echo "✅ Credentials found"
echo "📧 Email: $IQOPTION_EMAIL"
echo "🎯 Mode: ${TRADING_MODE:-demo}"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs config reports database_files
echo "✅ Directories created"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version"
echo ""

# Check dependencies
echo "📦 Checking dependencies..."
if ! python -c "import iqoptionapi" 2>/dev/null; then
    echo "❌ iqoptionapi not installed"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi
echo "✅ Dependencies OK"
echo ""

# Display configuration
echo "================================================================================"
echo "⚙️  CONFIGURATION"
echo "================================================================================"
echo "Strategies: 7 concurrent threads"
echo "  1. enhanced_candle_count"
echo "  2. rsi_divergence"
echo "  3. macd_momentum"
echo "  4. bollinger_rsi_combo"
echo "  5. stochastic"
echo "  6. trend_alignment"
echo "  7. support_resistance"
echo ""
echo "Settings:"
echo "  - Strategy Scan Interval: ${STRATEGY_SCAN_INTERVAL:-5}s"
echo "  - Min Seconds Between Trades: ${MIN_SECONDS_BETWEEN_TRADES:-70}s"
echo "  - Max Daily Loss (per strategy): \$${MAX_DAILY_LOSS:-50}"
echo "  - Max Consecutive Losses: ${MAX_CONSECUTIVE_LOSSES:-5}"
echo "  - Base Trade Amount: \$${BASE_TRADE_AMOUNT:-1.0}"
echo "  - Min AI Confidence: ${MIN_AI_CONFIDENCE:-70}%"
echo ""
echo "Health API: http://localhost:${HEALTH_API_PORT:-5001}"
echo "================================================================================"
echo ""

# Confirm start
read -p "🚀 Start trading bot? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "================================================================================"
echo "🎯 STARTING STRATEGY-PER-THREAD TRADING BOT"
echo "================================================================================"
echo ""

# Start the bot
python autonomous_parallel_trading_bot.py

echo ""
echo "================================================================================"
echo "🏁 BOT STOPPED"
echo "================================================================================"
