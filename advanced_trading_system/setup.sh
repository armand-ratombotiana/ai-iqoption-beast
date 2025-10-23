#!/bin/bash
# KAEL Trading System - Setup Script
# Automates initial setup and configuration

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    KAEL TRADING SYSTEM - SETUP                               ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
else
    echo -e "${RED}❌ Python $REQUIRED_VERSION or higher required${NC}"
    exit 1
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p data/cache
echo -e "${GREEN}✅ Directories created${NC}"

# Check if .env exists
echo ""
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
    else
        cp .env.example .env
        echo -e "${GREEN}✅ .env file created from template${NC}"
    fi
else
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created from template${NC}"
fi

# Prompt for credentials
echo ""
echo "🔐 IQOption Credentials Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Enter your IQOption email: " IQOPTION_EMAIL
read -sp "Enter your IQOption password: " IQOPTION_PASSWORD
echo ""

# Update .env file
if [ ! -z "$IQOPTION_EMAIL" ] && [ ! -z "$IQOPTION_PASSWORD" ]; then
    # Use sed to replace placeholders
    sed -i "s/IQOPTION_EMAIL=.*/IQOPTION_EMAIL=$IQOPTION_EMAIL/" .env
    sed -i "s/IQOPTION_PASSWORD=.*/IQOPTION_PASSWORD=$IQOPTION_PASSWORD/" .env
    echo -e "${GREEN}✅ Credentials saved to .env${NC}"
else
    echo -e "${YELLOW}⚠️  Credentials not provided. Please edit .env manually${NC}"
fi

# Ask about account type
echo ""
read -p "Use demo account? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    sed -i "s/ACCOUNT_TYPE=.*/ACCOUNT_TYPE=real/" .env
    echo -e "${YELLOW}⚠️  WARNING: Real account mode enabled!${NC}"
else
    sed -i "s/ACCOUNT_TYPE=.*/ACCOUNT_TYPE=demo/" .env
    echo -e "${GREEN}✅ Demo account mode enabled (recommended)${NC}"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if pip install -r requirements.txt > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."

ERRORS=0

if python -c "from iqoptionapi.stable_api import IQ_Option" 2>/dev/null; then
    echo -e "${GREEN}✅ IQOption API${NC}"
else
    echo -e "${RED}❌ IQOption API${NC}"
    ERRORS=$((ERRORS + 1))
fi

if python -c "import numpy" 2>/dev/null; then
    echo -e "${GREEN}✅ NumPy${NC}"
else
    echo -e "${RED}❌ NumPy${NC}"
    ERRORS=$((ERRORS + 1))
fi

if python -c "from dotenv import load_dotenv" 2>/dev/null; then
    echo -e "${GREEN}✅ python-dotenv${NC}"
else
    echo -e "${RED}❌ python-dotenv${NC}"
    ERRORS=$((ERRORS + 1))
fi

if python -c "import anthropic" 2>/dev/null; then
    echo -e "${GREEN}✅ Anthropic SDK${NC}"
else
    echo -e "${YELLOW}⚠️  Anthropic SDK (optional)${NC}"
fi

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Installation verification failed${NC}"
    echo "Please check the errors above and run: pip install -r requirements.txt"
    exit 1
fi

# Test configuration
echo ""
echo "⚙️  Testing configuration..."
if python -c "from config.settings import TradingConfig; TradingConfig.validate()" 2>/dev/null; then
    echo -e "${GREEN}✅ Configuration valid${NC}"
else
    echo -e "${RED}❌ Configuration validation failed${NC}"
    echo "Please check your .env file"
    exit 1
fi

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                           SETUP COMPLETE                                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Test the system:"
echo "   python run_comprehensive_tests.py"
echo ""
echo "2. Run demo trading:"
echo "   python trade.py --mode demo --trades 5"
echo ""
echo "3. View documentation:"
echo "   cat PRODUCTION_SETUP.md"
echo ""
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
