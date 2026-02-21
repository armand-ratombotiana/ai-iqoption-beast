#!/bin/bash
# Autonomous AI Trading System - Startup Script
# Complete startup with pre-flight checks and monitoring

echo "================================================================================================"
echo "🤖 AUTONOMOUS AI TRADING SYSTEM - STARTUP"
echo "================================================================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Pre-flight checks
echo ""
echo "📋 Step 1: Pre-flight Checks"
echo "--------------------------------"

# Check Python version
echo -n "Checking Python version... "
python_version=$(python --version 2>&1 | awk '{print $2}')
if [[ $(echo "$python_version 3.8" | awk '{print ($1 >= $2)}') -eq 1 ]]; then
    echo -e "${GREEN}✅ Python $python_version${NC}"
else
    echo -e "${RED}❌ Python 3.8+ required (found $python_version)${NC}"
    exit 1
fi

# Check if virtual environment is activated
echo -n "Checking virtual environment... "
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo -e "${GREEN}✅ Active${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment detected${NC}"
    echo "   Recommendation: Use a virtual environment"
fi

# Check required directories
echo -n "Checking directories... "
mkdir -p logs data models templates
echo -e "${GREEN}✅ Created${NC}"

# Check .env file
echo -n "Checking configuration... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env found${NC}"
else
    echo -e "${YELLOW}⚠️  .env not found${NC}"
    echo "   Creating from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}   ✅ Created .env from example${NC}"
        echo -e "${YELLOW}   ⚠️  Please edit .env with your credentials${NC}"
        exit 1
    else
        echo -e "${RED}   ❌ .env.example not found${NC}"
        exit 1
    fi
fi

# Step 2: Dependency check
echo ""
echo "📦 Step 2: Checking Dependencies"
echo "--------------------------------"

echo -n "Checking core dependencies... "
python -c "import numpy, asyncio, logging" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Core dependencies OK${NC}"
else
    echo -e "${RED}❌ Missing core dependencies${NC}"
    echo "   Installing..."
    pip install -r requirements.txt
fi

echo -n "Checking autonomous AI dependencies... "
python -c "import torch, sklearn, scipy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ AI dependencies OK${NC}"
else
    echo -e "${YELLOW}⚠️  Missing AI dependencies${NC}"
    echo "   Installing..."
    pip install -r requirements_autonomous.txt
fi

# Step 3: Verify implementation
echo ""
echo "🔍 Step 3: Verifying Implementation"
echo "--------------------------------"

python verify_autonomous_implementation.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Verification failed${NC}"
    echo "   Please fix errors before continuing"
    exit 1
fi

# Step 4: Run tests (optional)
echo ""
echo "🧪 Step 4: Running Tests (Optional)"
echo "--------------------------------"
read -p "Run tests before starting? (y/N): " run_tests

if [[ $run_tests =~ ^[Yy]$ ]]; then
    python tests/test_autonomous_ai.py
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Some tests failed${NC}"
        read -p "Continue anyway? (y/N): " continue_anyway
        if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "Skipping tests..."
fi

# Step 5: Configuration
echo ""
echo "⚙️  Step 5: Configuration"
echo "--------------------------------"

# Default values
MODE="demo"
AUTONOMY_LEVEL="semi_autonomous"
MAX_TRADES_PER_HOUR=10
CONFIDENCE_THRESHOLD=0.75
RISK_TOLERANCE=0.02

echo "Select configuration:"
echo "  1) Demo - Semi-Autonomous (Recommended)"
echo "  2) Demo - Supervised (Safe testing)"
echo "  3) Demo - Fully Autonomous (Advanced)"
echo "  4) Live - Semi-Autonomous (Real money)"
echo "  5) Custom configuration"
read -p "Choice (1-5): " config_choice

case $config_choice in
    1)
        MODE="demo"
        AUTONOMY_LEVEL="semi_autonomous"
        echo -e "${GREEN}✅ Demo - Semi-Autonomous selected${NC}"
        ;;
    2)
        MODE="demo"
        AUTONOMY_LEVEL="supervised"
        echo -e "${GREEN}✅ Demo - Supervised selected${NC}"
        ;;
    3)
        MODE="demo"
        AUTONOMY_LEVEL="fully_autonomous"
        echo -e "${YELLOW}⚠️  Demo - Fully Autonomous selected${NC}"
        ;;
    4)
        MODE="live"
        AUTONOMY_LEVEL="semi_autonomous"
        echo -e "${RED}⚠️  LIVE TRADING MODE SELECTED${NC}"
        echo -e "${RED}   This involves REAL MONEY!${NC}"
        ;;
    5)
        echo "Custom configuration:"
        read -p "  Mode (demo/live): " MODE
        read -p "  Autonomy level (supervised/semi_autonomous/fully_autonomous): " AUTONOMY_LEVEL
        read -p "  Max trades per hour (default 10): " MAX_TRADES_PER_HOUR
        read -p "  Confidence threshold (default 0.75): " CONFIDENCE_THRESHOLD
        read -p "  Risk tolerance (default 0.02): " RISK_TOLERANCE
        ;;
    *)
        echo -e "${GREEN}Using default: Demo - Semi-Autonomous${NC}"
        ;;
esac

# Step 6: Monitoring option
echo ""
echo "📊 Step 6: Monitoring Options"
echo "--------------------------------"
echo "Select monitoring interface:"
echo "  1) Terminal output (Simple)"
echo "  2) Web dashboard (Recommended)"
echo "  3) Both"
read -p "Choice (1-3): " monitor_choice

# Step 7: Start system
echo ""
echo "🚀 Step 7: Starting Autonomous AI"
echo "================================================================================================"

# Build command
CMD="python run_autonomous_ai.py --mode $MODE --autonomy-level $AUTONOMY_LEVEL"

if [ ! -z "$MAX_TRADES_PER_HOUR" ]; then
    CMD="$CMD --max-trades-per-hour $MAX_TRADES_PER_HOUR"
fi

if [ ! -z "$CONFIDENCE_THRESHOLD" ]; then
    CMD="$CMD --confidence-threshold $CONFIDENCE_THRESHOLD"
fi

if [ ! -z "$RISK_TOLERANCE" ]; then
    CMD="$CMD --risk-tolerance $RISK_TOLERANCE"
fi

# Add confirm flag for live mode
if [ "$MODE" == "live" ]; then
    CMD="$CMD --confirm"
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  Mode: $MODE"
echo "  Autonomy Level: $AUTONOMY_LEVEL"
echo "  Max Trades/Hour: $MAX_TRADES_PER_HOUR"
echo "  Confidence Threshold: $CONFIDENCE_THRESHOLD"
echo "  Risk Tolerance: $RISK_TOLERANCE"
echo ""

# Final confirmation
if [ "$MODE" == "live" ]; then
    echo -e "${RED}================================================================================================${NC}"
    echo -e "${RED}⚠️  WARNING: LIVE TRADING MODE${NC}"
    echo -e "${RED}================================================================================================${NC}"
    echo ""
    echo "You are about to start AUTONOMOUS AI trading with REAL MONEY."
    echo ""
    read -p "Type 'YES' to confirm: " final_confirm
    
    if [ "$final_confirm" != "YES" ]; then
        echo -e "${RED}❌ Cancelled${NC}"
        exit 0
    fi
fi

# Start based on monitoring choice
case $monitor_choice in
    1)
        echo "Starting with terminal output..."
        $CMD
        ;;
    2)
        echo "Starting with web dashboard..."
        echo ""
        echo "Starting autonomous AI in background..."
        $CMD > logs/autonomous_output.log 2>&1 &
        AI_PID=$!
        echo "  PID: $AI_PID"
        
        sleep 3
        
        echo ""
        echo "Starting web monitor..."
        python web_monitor.py
        
        # Cleanup
        kill $AI_PID 2>/dev/null
        ;;
    3)
        echo "Starting with both terminal and web dashboard..."
        echo ""
        echo "Starting autonomous AI..."
        $CMD &
        AI_PID=$!
        
        sleep 3
        
        echo ""
        echo "Starting web monitor..."
        echo "  Terminal: This window"
        echo "  Web: http://localhost:5000"
        python web_monitor.py &
        WEB_PID=$!
        
        # Wait for autonomous AI
        wait $AI_PID
        
        # Cleanup
        kill $WEB_PID 2>/dev/null
        ;;
    *)
        echo "Starting with terminal output (default)..."
        $CMD
        ;;
esac

echo ""
echo "================================================================================================"
echo "✅ Autonomous AI Session Complete"
echo "================================================================================================"
echo ""
echo "📁 Session files:"
echo "  Logs: logs/"
echo "  Data: data/"
echo "  Models: models/"
echo ""
echo "To review session:"
echo "  cat logs/autonomous_ai_*.log"
echo "  cat data/session_report_*.json"
echo ""
echo "================================================================================================"