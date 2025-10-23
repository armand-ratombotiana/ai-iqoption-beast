#!/bin/bash

# =====================================================
# Setup Verification Script
# =====================================================
# Tests all prerequisites before activating workflows
# =====================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}IQOption AI Trading System - Setup Verification${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# =====================================================
# Helper Functions
# =====================================================

check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    echo -e "  ${YELLOW}Fix:${NC} $2"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    echo -e "  ${YELLOW}Recommendation:${NC} $2"
    ((WARNINGS++))
}

# =====================================================
# 1. Check Prerequisites
# =====================================================

echo -e "${BLUE}[1/8] Checking Prerequisites...${NC}"
echo ""

# Check PostgreSQL
if command -v psql &> /dev/null; then
    check_pass "PostgreSQL client installed"
else
    check_fail "PostgreSQL client not found" "Install PostgreSQL: sudo apt-get install postgresql-client"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    check_pass "Python installed (version $PYTHON_VERSION)"
else
    check_fail "Python 3 not found" "Install Python: sudo apt-get install python3"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js installed (version $NODE_VERSION)"
else
    check_fail "Node.js not found" "Install Node.js: https://nodejs.org/"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    check_pass "npm installed (version $NPM_VERSION)"
else
    check_fail "npm not found" "Install npm: sudo apt-get install npm"
fi

echo ""

# =====================================================
# 2. Check Environment Variables
# =====================================================

echo -e "${BLUE}[2/8] Checking Environment Configuration...${NC}"
echo ""

if [ ! -f .env ]; then
    check_fail ".env file not found" "Copy .env.example to .env and configure"
else
    check_pass ".env file exists"

    # Source .env file
    set -a
    source .env
    set +a

    # Check critical variables
    REQUIRED_VARS=(
        "OPENAI_API_KEY"
        "CLAUDE_API_KEY"
        "DEEPSEEK_API_KEY"
        "IQOPTION_EMAIL"
        "IQOPTION_PASSWORD"
        "IQOPTION_ACCOUNT_TYPE"
        "IQOPTION_API_URL"
        "N8N_SMTP_USER"
        "N8N_SMTP_PASS"
        "N8N_EMAIL_TO"
        "POSTGRES_HOST"
        "POSTGRES_PORT"
        "POSTGRES_DB"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "N8N_TRADE_INTERVAL_MINUTES"
        "N8N_TRADE_AMOUNT"
        "N8N_TRADE_ASSET"
    )

    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            check_fail "$var not set" "Add $var to .env file"
        else
            # Check if it's a placeholder value
            if [[ "${!var}" == *"your_"* ]] || [[ "${!var}" == *"xxxxx"* ]] || [[ "${!var}" == *"change_me"* ]]; then
                check_warn "$var appears to be placeholder" "Set real value for $var"
            else
                check_pass "$var is configured"
            fi
        fi
    done

    # Check account type is demo
    if [ "$IQOPTION_ACCOUNT_TYPE" != "demo" ]; then
        check_warn "Using real account" "Always test with demo account first!"
    else
        check_pass "Using demo account (safe testing)"
    fi
fi

echo ""

# =====================================================
# 3. Check Database
# =====================================================

echo -e "${BLUE}[3/8] Checking Database Connection...${NC}"
echo ""

if command -v psql &> /dev/null; then
    # Test database connection
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" &> /dev/null; then
        check_pass "Database connection successful"

        # Check if tables exist
        TABLE_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('trades', 'daily_stats', 'workflow_executions', 'error_logs');" 2>/dev/null | xargs)

        if [ "$TABLE_COUNT" -eq "4" ]; then
            check_pass "Required tables exist"
        else
            check_fail "Required tables missing ($TABLE_COUNT/4 found)" "Run: psql -U $POSTGRES_USER -d $POSTGRES_DB -f schemas/postgres_schema.sql"
        fi

    else
        check_fail "Cannot connect to database" "Check POSTGRES_* variables in .env and ensure PostgreSQL is running"
    fi
else
    check_warn "Cannot verify database (psql not found)" "Install PostgreSQL client to verify"
fi

echo ""

# =====================================================
# 4. Check IQOption API Server
# =====================================================

echo -e "${BLUE}[4/8] Checking IQOption API Server...${NC}"
echo ""

if command -v curl &> /dev/null; then
    # Extract host and port from IQOPTION_API_URL
    API_HOST=$(echo $IQOPTION_API_URL | sed -E 's|https?://([^:/]+).*|\1|')

    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 $IQOPTION_API_URL/status 2>/dev/null | grep -q "200"; then
        check_pass "IQOption API server is accessible"
    else
        check_fail "Cannot reach IQOption API server at $IQOPTION_API_URL" "Start the API server: cd advanced_trading_system && python main.py --mode api --port 5000"
    fi
else
    check_warn "Cannot verify API server (curl not found)" "Install curl to verify"
fi

echo ""

# =====================================================
# 5. Check Custom n8n Node
# =====================================================

echo -e "${BLUE}[5/8] Checking Custom n8n Node...${NC}"
echo ""

if [ -d "../n8n-nodes-trading" ]; then
    check_pass "Custom node directory exists"

    if [ -f "../n8n-nodes-trading/package.json" ]; then
        check_pass "package.json found"

        if [ -d "../n8n-nodes-trading/node_modules" ]; then
            check_pass "Node modules installed"
        else
            check_warn "Node modules not installed" "Run: cd ../n8n-nodes-trading && npm install"
        fi
    else
        check_fail "package.json missing" "Check ../n8n-nodes-trading directory"
    fi
else
    check_fail "Custom node directory not found" "Ensure ../n8n-nodes-trading exists"
fi

echo ""

# =====================================================
# 6. Check Workflow Files
# =====================================================

echo -e "${BLUE}[6/8] Checking Workflow Files...${NC}"
echo ""

REQUIRED_WORKFLOWS=(
    "workflows/Main_Trading_Workflow.json"
    "workflows/AI_Consensus_Engine.json"
    "workflows/Data_Logger.json"
    "workflows/Email_Reporter.json"
    "workflows/Error_Alert_Workflow.json"
)

for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$workflow" ]; then
        check_pass "$(basename $workflow) exists"
    else
        check_fail "$(basename $workflow) not found" "File missing: $workflow"
    fi
done

echo ""

# =====================================================
# 7. Check Python Dependencies
# =====================================================

echo -e "${BLUE}[7/8] Checking Python Dependencies...${NC}"
echo ""

if [ -f "../advanced_trading_system/requirements.txt" ]; then
    check_pass "requirements.txt found"

    # Check if key packages are installed
    if python3 -c "import flask" 2>/dev/null; then
        check_pass "Flask installed"
    else
        check_warn "Flask not installed" "Run: pip install -r ../advanced_trading_system/requirements.txt"
    fi

    if python3 -c "import requests" 2>/dev/null; then
        check_pass "Requests installed"
    else
        check_warn "Requests not installed" "Run: pip install requests"
    fi
else
    check_warn "requirements.txt not found" "Check ../advanced_trading_system directory"
fi

echo ""

# =====================================================
# 8. Check API Keys (Basic Validation)
# =====================================================

echo -e "${BLUE}[8/8] Validating API Keys...${NC}"
echo ""

# OpenAI
if [[ "$OPENAI_API_KEY" == sk-* ]] && [ ${#OPENAI_API_KEY} -gt 20 ]; then
    check_pass "OpenAI API key format looks valid"
else
    check_warn "OpenAI API key format seems incorrect" "Verify OPENAI_API_KEY in .env"
fi

# Claude
if [[ "$CLAUDE_API_KEY" == sk-ant-* ]] && [ ${#CLAUDE_API_KEY} -gt 20 ]; then
    check_pass "Claude API key format looks valid"
else
    check_warn "Claude API key format seems incorrect" "Verify CLAUDE_API_KEY in .env"
fi

# DeepSeek
if [[ "$DEEPSEEK_API_KEY" == sk-* ]] && [ ${#DEEPSEEK_API_KEY} -gt 10 ]; then
    check_pass "DeepSeek API key format looks valid"
else
    check_warn "DeepSeek API key format seems incorrect" "Verify DEEPSEEK_API_KEY in .env"
fi

echo ""

# =====================================================
# Summary
# =====================================================

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Import workflows into n8n UI"
    echo "2. Configure credentials in each workflow"
    echo "3. Link Error_Alert_Workflow to Main_Trading_Workflow"
    echo "4. Test workflows individually"
    echo "5. Activate Main_Trading_Workflow"
    echo ""
    echo -e "${YELLOW}Remember: Always test on DEMO account first!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some critical checks failed. Please fix the issues above before proceeding.${NC}"
    echo ""
    echo -e "${YELLOW}For detailed setup instructions, see:${NC}"
    echo "  - QUICK_START.md (quick setup)"
    echo "  - README.md (complete guide)"
    echo ""
    exit 1
fi
