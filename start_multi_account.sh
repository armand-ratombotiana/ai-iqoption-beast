#!/bin/bash

###############################################################################
# Multi-Account Trading Bot Startup Script
# Launches 5 concurrent accounts with different strategy profiles
###############################################################################

set -e

echo "================================================================================"
echo "🚀 KAEL Multi-Account Parallel Trading Bot"
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

# Create necessary directories
echo -e "${GREEN}📁 Creating directories...${NC}"
mkdir -p logs
mkdir -p reports
mkdir -p config
mkdir -p pgdata
mkdir -p database_files

# Check if config/accounts.json exists
if [ ! -f config/accounts.json ]; then
    echo -e "${YELLOW}⚠️  No accounts.json found. It will be created automatically on first run.${NC}"
fi

# Build and start services
echo ""
echo -e "${GREEN}🐳 Building and starting Docker containers...${NC}"
docker-compose -f docker-compose.multi-account.yml up -d --build

# Wait for services to be ready
echo ""
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check service health
echo ""
echo -e "${GREEN}🏥 Checking service health...${NC}"

# Check TimescaleDB
echo -n "   - TimescaleDB: "
if docker exec kael-timescaledb pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${RED}❌ Not ready${NC}"
fi

# Check Bot
echo -n "   - Trading Bot: "
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
echo -e "${GREEN}✅ Multi-Account Trading Bot Started!${NC}"
echo "================================================================================"
echo ""
echo "📊 Service URLs:"
echo "   - Health API:    http://localhost:5001"
echo "   - Statistics:    http://localhost:5001/statistics"
echo "   - Accounts:      http://localhost:5001/accounts"
echo "   - Prometheus:    http://localhost:9090"
echo "   - Grafana:       http://localhost:3000 (admin/admin)"
echo ""
echo "📁 Data Locations:"
echo "   - Logs:          ./logs/"
echo "   - Reports:       ./reports/"
echo "   - Database:      ./pgdata/"
echo ""
echo "🔧 Useful Commands:"
echo "   - View logs:     docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot"
echo "   - Stop:          docker-compose -f docker-compose.multi-account.yml down"
echo "   - Restart:       docker-compose -f docker-compose.multi-account.yml restart multi-account-bot"
echo "   - Export CSV:    curl http://localhost:5001/export/csv?days=7 -o trades.csv"
echo "   - Export JSON:   curl http://localhost:5001/export/json?days=7 -o performance.json"
echo ""
echo "================================================================================"
echo ""

# Tail logs
echo -e "${YELLOW}📋 Showing live logs (Ctrl+C to exit)...${NC}"
echo ""
docker-compose -f docker-compose.multi-account.yml logs -f multi-account-bot
