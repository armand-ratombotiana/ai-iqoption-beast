#!/bin/bash

# Docker Start Script for KAEL Trading System
# This script makes it easy to start the trading system in Docker

set -e

echo "🐳 KAEL Trading System - Docker Deployment"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created. Please edit it with your credentials:"
        echo "   - IQOPTION_EMAIL"
        echo "   - IQOPTION_PASSWORD"
        echo ""
        read -p "Press Enter after you've configured the .env file..."
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
fi

# Load environment variables
source .env

# Verify credentials are set
if [ -z "$IQOPTION_EMAIL" ] || [ -z "$IQOPTION_PASSWORD" ]; then
    echo "❌ Error: IQOption credentials not set in .env file"
    echo "Please set IQOPTION_EMAIL and IQOPTION_PASSWORD"
    exit 1
fi

echo "✅ Configuration verified"
echo ""

# Create necessary directories
mkdir -p logs database

# Ask user for deployment mode
echo "Select deployment mode:"
echo "1) Demo Account (Safe - Recommended)"
echo "2) Real Account (⚠️  Use with caution!)"
read -p "Enter choice [1-2]: " mode_choice

case $mode_choice in
    1)
        export ACCOUNT_TYPE=demo
        echo "✅ Using DEMO account"
        ;;
    2)
        echo "⚠️  WARNING: You are about to use a REAL account!"
        read -p "Are you sure? Type 'YES' to confirm: " confirm
        if [ "$confirm" != "YES" ]; then
            echo "Deployment cancelled"
            exit 1
        fi
        export ACCOUNT_TYPE=real
        echo "✅ Using REAL account"
        ;;
    *)
        echo "Invalid choice. Using DEMO account by default"
        export ACCOUNT_TYPE=demo
        ;;
esac

echo ""
echo "Building Docker image..."
docker-compose build

echo ""
echo "Starting trading system..."
docker-compose up -d

echo ""
echo "✅ Trading system started successfully!"
echo ""
echo "📊 Useful commands:"
echo "   View logs:          docker-compose logs -f"
echo "   Stop system:        docker-compose down"
echo "   Restart system:     docker-compose restart"
echo "   Check status:       docker-compose ps"
echo "   View health:        docker inspect --format='{{.State.Health.Status}}' kael-trading-system"
echo ""
echo "📁 Data locations:"
echo "   Logs:               ./logs/"
echo "   Database:           ./database/"
echo ""
echo "🔍 Monitoring:"
docker-compose ps
echo ""

# Follow logs
read -p "Do you want to view logs now? [y/N]: " view_logs
if [[ $view_logs =~ ^[Yy]$ ]]; then
    echo ""
    echo "📋 Following logs (Ctrl+C to stop)..."
    docker-compose logs -f
fi
