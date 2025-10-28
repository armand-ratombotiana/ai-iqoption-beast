#!/bin/bash
# Multi-Strategy Trading System Setup Script

set -e

echo "=================================="
echo "🚀 Multi-Strategy Trading System"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check Docker
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found (optional)${NC}"
else
    echo -e "${GREEN}✅ Docker found${NC}"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install psycopg2-binary

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p config
mkdir -p reports
mkdir -p database_files

echo -e "${GREEN}✅ Directories created${NC}"

# Setup database
echo ""
echo "Setting up database..."
read -p "Use Docker for database? (y/n): " use_docker

if [ "$use_docker" = "y" ]; then
    echo "Starting TimescaleDB with Docker..."
    docker-compose up -d timescaledb
    
    echo "Waiting for database to be ready..."
    sleep 10
    
    echo "Initializing database schema..."
    docker exec -i kael-timescaledb psql -U postgres -d kael < database/multi_account_schema.sql
    
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo "Please ensure PostgreSQL is running and create database 'kael'"
    echo "Then run: psql -U postgres -d kael -f database/multi_account_schema.sql"
fi

# Create .env file
echo ""
echo "Creating .env file..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kael

# Trading Mode
TRADING_MODE=demo

# Advanced Strategies
USE_ADVANCED_STRATEGIES=true
STRATEGY_RISK_PROFILE=moderate

# Logging
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Test database connection
echo ""
echo "Testing database connection..."
python3 << EOF
import os
import sys
from database.multi_account_logger import MultiAccountTradeLogger

try:
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kael')
    logger = MultiAccountTradeLogger(database_url)
    print("${GREEN}✅ Database connection successful${NC}")
except Exception as e:
    print(f"${RED}❌ Database connection failed: {e}${NC}")
    sys.exit(1)
EOF

# Initialize account configuration
echo ""
echo "Initializing account configuration..."
python3 << EOF
from config.multi_account_config import get_account_manager

manager = get_account_manager()
summary = manager.get_summary()

print(f"${GREEN}✅ Configured {summary['total_accounts']} accounts${NC}")
for acc in summary['accounts']:
    print(f"  - {acc['account_id']}: {acc['strategy']} strategy")
EOF

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Review config/accounts.json"
echo "2. Run: python multi_strategy_orchestrator.py"
echo "3. Monitor at: http://localhost:5001"
echo ""
echo "For detailed instructions, see: MULTI_STRATEGY_SETUP_GUIDE.md"
echo ""
