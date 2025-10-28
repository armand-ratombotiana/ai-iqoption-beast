#!/bin/bash

###############################################################################
# Ultimate Strategy Evaluator Startup Script
# Launches the unified bot that evaluates 10+ binary option strategies
###############################################################################

set -e

echo "================================================================================"
echo "🚀 KAEL Ultimate Strategy Evaluator"
echo "================================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file. Please update with your credentials.${NC}"
    else
        echo -e "${RED}❌ No .env.example found. Cannot create .env file.${NC}"
        exit 1
    fi
fi

# Check if IQ Option credentials are set
if ! grep -q "IQOPTION_EMAIL=" .env || ! grep -q "IQOPTION_PASSWORD=" .env; then
    echo -e "${RED}❌ IQ Option credentials not found in .env${NC}"
    echo ""
    echo "Please add your credentials to .env:"
    echo "  IQOPTION_EMAIL=your_email@gmail.com"
    echo "  IQOPTION_PASSWORD=your_password"
    echo ""
    exit 1
fi

# Create necessary directories
echo -e "${GREEN}📁 Creating directories...${NC}"
mkdir -p logs
mkdir -p reports
mkdir -p pgdata

# Build and start services
echo ""
echo -e "${GREEN}🐳 Building and starting Docker containers...${NC}"
docker-compose -f docker-compose.ultimate-evaluator.yml up -d --build

# Wait for services to be ready
echo ""
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 15

# Check service health
echo ""
echo -e "${GREEN}🏥 Checking service health...${NC}"

# Check TimescaleDB
echo -n "   - TimescaleDB: "
if docker exec kael-timescaledb pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${YELLOW}⏳ Starting...${NC}"
fi

# Check Bot
echo -n "   - Ultimate Evaluator: "
if curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${YELLOW}⏳ Starting...${NC}"
fi

# Check Prometheus
echo -n "   - Prometheus: "
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${YELLOW}⏳ Starting...${NC}"
fi

# Check Grafana
echo -n "   - Grafana: "
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${YELLOW}⏳ Starting...${NC}"
fi

echo ""
echo "================================================================================"
echo -e "${GREEN}✅ Ultimate Strategy Evaluator Started!${NC}"
echo "================================================================================"
echo ""
echo "📊 System Information:"
echo "   - Mode: $(grep TRADING_MODE .env | cut -d'=' -f2)"
echo "   - Start Balance: \$100 (fictitious)"
echo "   - Strategies: 10+"
echo ""
echo "📊 Service URLs:"
echo "   - Health API:    http://localhost:5001"
echo "   - Statistics:    http://localhost:5001/statistics"
echo "   - All Strategies: http://localhost:5001/strategies"
echo "   - Prometheus:    http://localhost:9090"
echo "   - Grafana:       http://localhost:3000 (admin/admin)"
echo ""
echo "📁 Data Locations:"
echo "   - Logs:          ./logs/"
echo "   - Reports:       ./reports/"
echo "   - Database:      ./pgdata/"
echo ""
echo "🔧 Useful Commands:"
echo "   - View logs:     docker-compose -f docker-compose.ultimate-evaluator.yml logs -f ultimate-evaluator"
echo "   - Stop:          docker-compose -f docker-compose.ultimate-evaluator.yml down"
echo "   - Restart:       docker-compose -f docker-compose.ultimate-evaluator.yml restart ultimate-evaluator"
echo "   - Export CSV:    curl http://localhost:5001/export/csv?days=7 -o trades.csv"
echo "   - Export JSON:   curl http://localhost:5001/export/json -o performance.json"
echo ""
echo "📈 Monitoring Commands:"
echo "   - Real-time stats:      curl http://localhost:5001/statistics | jq"
echo "   - Strategy performance: curl http://localhost:5001/strategies | jq"
echo "   - Specific strategy:    curl http://localhost:5001/strategy/bollinger_rsi_combo | jq"
echo ""
echo "================================================================================"
echo ""

# Wait a bit more for bot to fully initialize
echo -e "${YELLOW}⏳ Waiting for bot to fully initialize (30 seconds)...${NC}"
sleep 30

# Try to get initial statistics
echo ""
echo -e "${GREEN}📊 Initial Statistics:${NC}"
if curl -s http://localhost:5001/statistics 2>/dev/null | jq -r '.initial_balance, .current_balance, .active_strategies' 2>/dev/null; then
    echo ""
    echo -e "${GREEN}✅ Bot is running and responding!${NC}"
else
    echo -e "${YELLOW}⚠️  Bot starting, statistics will be available shortly.${NC}"
    echo "   Check logs: docker-compose -f docker-compose.ultimate-evaluator.yml logs -f ultimate-evaluator"
fi

echo ""
echo "================================================================================"
echo ""

# Ask if user wants to tail logs
read -p "Show live logs? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}📋 Showing live logs (Ctrl+C to exit)...${NC}"
    echo ""
    docker-compose -f docker-compose.ultimate-evaluator.yml logs -f ultimate-evaluator
fi
