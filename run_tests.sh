#!/bin/bash

# =============================================================================
# KAEL Trading System - Test Runner
# =============================================================================
# This script helps you run tests easily
# Usage: ./run_tests.sh [test_type]

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================================================="
echo "  KAEL TRADING SYSTEM - TEST RUNNER"
echo "=========================================================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ ERROR: .env file not found!${NC}"
    echo ""
    echo "Please set up credentials first:"
    echo "  python3 setup_credentials.py"
    echo ""
    exit 1
fi

# Check trading mode
TRADING_MODE=$(grep "^TRADING_MODE=" .env | cut -d '=' -f2)
if [ "$TRADING_MODE" != "demo" ]; then
    echo -e "${RED}❌ ERROR: TRADING_MODE must be 'demo' for tests!${NC}"
    echo ""
    echo "Current mode: $TRADING_MODE"
    echo "Please edit .env and set: TRADING_MODE=demo"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Configuration OK${NC}"
echo "   Trading Mode: DEMO"
echo ""

# Determine which tests to run
TEST_TYPE=${1:-all}

case $TEST_TYPE in
    connection|conn|1)
        echo -e "${BLUE}Running Connection Tests...${NC}"
        pytest tests/integration/test_01_connection.py -v -s
        ;;

    data|ingestion|2)
        echo -e "${BLUE}Running Data Ingestion Tests...${NC}"
        pytest tests/integration/test_02_data_ingestion.py -v -s
        ;;

    quick)
        echo -e "${BLUE}Running Quick Tests (Connection + Data)...${NC}"
        pytest tests/integration/test_01_connection.py tests/integration/test_02_data_ingestion.py -v -s
        ;;

    integration|int)
        echo -e "${BLUE}Running All Integration Tests...${NC}"
        pytest tests/integration/ -v -s
        ;;

    all)
        echo -e "${BLUE}Running All Tests...${NC}"
        pytest tests/ -v -s
        ;;

    coverage|cov)
        echo -e "${BLUE}Running Tests with Coverage...${NC}"
        pytest tests/ --cov=advanced_trading_system --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
        ;;

    help|--help|-h)
        echo "Usage: ./run_tests.sh [test_type]"
        echo ""
        echo "Test Types:"
        echo "  connection, conn, 1    - Run connection tests only"
        echo "  data, ingestion, 2     - Run data ingestion tests only"
        echo "  quick                  - Run connection + data tests"
        echo "  integration, int       - Run all integration tests"
        echo "  all                    - Run all tests (default)"
        echo "  coverage, cov          - Run with coverage report"
        echo "  help                   - Show this help"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh connection"
        echo "  ./run_tests.sh quick"
        echo "  ./run_tests.sh coverage"
        echo ""
        exit 0
        ;;

    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo "Run './run_tests.sh help' for usage"
        exit 1
        ;;
esac

echo ""
echo "=========================================================================="
echo -e "${GREEN}✅ Tests completed!${NC}"
echo "=========================================================================="
