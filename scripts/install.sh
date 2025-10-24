#!/bin/bash

# N8N Trading Node - Installation Script
# This script automates the deployment of the n8n Trading Bot node

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main installation
main() {
    print_header "N8N TRADING NODE - INSTALLATION"

    # Step 1: Check prerequisites
    print_info "Step 1: Checking prerequisites..."

    if ! command_exists node; then
        print_error "Node.js is not installed!"
        print_info "Install Node.js 18+ from: https://nodejs.org/"
        exit 1
    fi
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"

    if ! command_exists python3; then
        print_error "Python 3 is not installed!"
        print_info "Install Python 3.8+ from: https://python.org/"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"

    if ! command_exists npm; then
        print_error "npm is not installed!"
        exit 1
    fi
    NPM_VERSION=$(npm --version)
    print_success "npm found: $NPM_VERSION"

    # Step 2: Install Python dependencies
    print_info "\nStep 2: Installing Python dependencies..."

    if pip3 install flask iqoptionapi >/dev/null 2>&1; then
        print_success "Python dependencies installed"
    else
        print_warning "Some Python packages may already be installed"
    fi

    # Step 3: Install Node dependencies
    print_info "\nStep 3: Installing Node.js dependencies..."

    cd n8n-nodes-trading

    if npm install; then
        print_success "Node dependencies installed"
    else
        print_error "Failed to install Node dependencies"
        exit 1
    fi

    # Step 4: Check for n8n
    print_info "\nStep 4: Checking for n8n installation..."

    if command_exists n8n; then
        N8N_VERSION=$(n8n --version 2>/dev/null || echo "unknown")
        print_success "n8n found: $N8N_VERSION"
        INSTALL_NODE=true
    else
        print_warning "n8n not found in PATH"
        print_info "You'll need to manually link the node to n8n"
        INSTALL_NODE=false
    fi

    # Step 5: Link node to n8n (if n8n found)
    if [ "$INSTALL_NODE" = true ]; then
        print_info "\nStep 5: Linking node to n8n..."

        # Create npm link
        if npm link >/dev/null 2>&1; then
            print_success "Global npm link created"
        else
            print_warning "npm link may already exist"
        fi

        # Check if ~/.n8n exists
        if [ -d "$HOME/.n8n" ]; then
            cd "$HOME/.n8n"

            if npm link n8n-nodes-trading >/dev/null 2>&1; then
                print_success "Node linked to n8n"
            else
                print_warning "Link may already exist"
            fi
        else
            print_warning "~/.n8n directory not found"
            print_info "n8n may not be initialized yet"
        fi
    fi

    cd - >/dev/null

    # Step 6: Installation summary
    print_header "INSTALLATION COMPLETE"

    echo ""
    print_success "Node package installed: n8n-nodes-trading"
    print_success "Dependencies installed"

    if [ "$INSTALL_NODE" = true ]; then
        print_success "Node linked to n8n"
    fi

    # Next steps
    print_header "NEXT STEPS"

    echo ""
    echo "1. Start the Flask API:"
    echo -e "   ${GREEN}python3 trading_api.py${NC}"
    echo ""
    echo "2. Restart n8n:"
    if command_exists systemctl; then
        echo -e "   ${GREEN}sudo systemctl restart n8n${NC}"
    else
        echo -e "   ${GREEN}n8n start${NC}"
    fi
    echo ""
    echo "3. Open n8n in browser:"
    echo -e "   ${GREEN}http://localhost:5678${NC}"
    echo ""
    echo "4. Search for 'Trading Bot' node in n8n"
    echo ""

    # Testing
    print_header "TESTING"

    echo ""
    echo "Test the installation:"
    echo -e "   ${GREEN}python3 test_n8n_node.py${NC}"
    echo ""
    echo "Check available markets:"
    echo -e "   ${GREEN}python3 check_markets.py${NC}"
    echo ""
    echo "Test simple trade:"
    echo -e "   ${GREEN}python3 simple_trade.py${NC}"
    echo ""

    # Documentation
    print_header "DOCUMENTATION"

    echo ""
    echo "📚 Read the documentation:"
    echo "   - DEPLOYMENT_GUIDE.md - Complete deployment guide"
    echo "   - README_IMPLEMENTATION.md - Main guide"
    echo "   - IMPROVEMENTS.md - Improvements from BOT_KAEL.py"
    echo "   - TEST_REPORT.md - Test results"
    echo ""

    print_success "Installation script completed!"
    echo ""
}

# Run main function
main "$@"
