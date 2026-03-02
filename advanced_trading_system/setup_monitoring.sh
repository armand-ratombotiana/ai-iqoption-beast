#!/bin/bash
#
# Setup Monitoring System for Paper Trading
# Initializes directories, creates sample data, and verifies installation
#

set -e

echo "=================================="
echo "PAPER TRADING MONITORING SETUP"
echo "=================================="

# Check Python availability
echo ""
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON="python3"
    echo "✓ Found: $($PYTHON --version)"
elif command -v python &> /dev/null; then
    PYTHON="python"
    echo "✓ Found: $($PYTHON --version)"
else
    echo "✗ Python not found. Please install Python 3.6+"
    exit 1
fi

# Create required directories
echo ""
echo "Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p scripts
echo "✓ Directories created"

# Initialize empty data files
echo ""
echo "Initializing data files..."

# Create empty trades.json if not exists
if [ ! -f data/trades.json ]; then
    echo "[]" > data/trades.json
    echo "✓ Created data/trades.json"
fi

# Create empty status.json if not exists
if [ ! -f data/status.json ]; then
    cat > data/status.json << 'EOF'
{
  "is_running": false,
  "connected": false,
  "active_trades": 0,
  "last_trade_time": null,
  "uptime_seconds": 0
}
EOF
    echo "✓ Created data/status.json"
fi

# Create empty metrics.json if not exists
if [ ! -f data/metrics.json ]; then
    cat > data/metrics.json << 'EOF'
{
  "total_trades": 0,
  "wins": 0,
  "losses": 0,
  "ties": 0,
  "win_rate": 0.0,
  "total_profit": 0.0,
  "daily_profit": 0.0,
  "daily_loss": 0.0,
  "consecutive_losses": 0,
  "max_drawdown": 0.0,
  "trades_per_hour": 0,
  "avg_profit_per_trade": 0.0
}
EOF
    echo "✓ Created data/metrics.json"
fi

# Verify Python imports
echo ""
echo "Checking required modules..."

# Check for core modules
modules=("json" "sqlite3" "logging" "csv")

for module in "${modules[@]}"; do
    if $PYTHON -c "import $module" 2>/dev/null; then
        echo "✓ $module available"
    else
        echo "⚠ $module not available (may be needed)"
    fi
done

# Run health check
echo ""
echo "Running system health check..."
if $PYTHON health_check.py 2>/dev/null; then
    echo "✓ Health check passed"
else
    echo "⚠ Health check reported issues (see above)"
fi

# Verify logging setup
echo ""
echo "Verifying logging configuration..."
if $PYTHON logging_config.py --verify 2>/dev/null; then
    echo "✓ Logging verified"
else
    echo "⚠ Logging verification issues (non-critical)"
fi

# Create startup scripts
echo ""
echo "Creating startup scripts..."

# Monitor startup script
cat > scripts/start_monitor.sh << 'SCRIPT'
#!/bin/bash
# Start paper trading monitor
python3 monitor_paper_trading.py "$@"
SCRIPT
chmod +x scripts/start_monitor.sh
echo "✓ Created scripts/start_monitor.sh"

# Health check script
cat > scripts/health_check.sh << 'SCRIPT'
#!/bin/bash
# Run health check
python3 health_check.py "$@"
SCRIPT
chmod +x scripts/health_check.sh
echo "✓ Created scripts/health_check.sh"

# Dashboard script
cat > scripts/show_dashboard.sh << 'SCRIPT'
#!/bin/bash
# Show performance dashboard
python3 performance_dashboard.py --all "$@"
SCRIPT
chmod +x scripts/show_dashboard.sh
echo "✓ Created scripts/show_dashboard.sh"

# Status script
cat > scripts/check_status.sh << 'SCRIPT'
#!/bin/bash
# Check current status
echo "=== MONITORING SYSTEM STATUS ==="
echo ""
echo "Health Check:"
python3 health_check.py | tail -5
echo ""
echo "Recent Alerts:"
python3 alert_system.py --alerts | tail -10
echo ""
echo "Metrics:"
python3 metrics_collector.py --show-stats
SCRIPT
chmod +x scripts/check_status.sh
echo "✓ Created scripts/check_status.sh"

# Print summary
echo ""
echo "=================================="
echo "SETUP COMPLETE"
echo "=================================="
echo ""
echo "Monitoring system components:"
echo "  ✓ Real-time Monitor (monitor_paper_trading.py)"
echo "  ✓ Performance Dashboard (performance_dashboard.py)"
echo "  ✓ Alert System (alert_system.py)"
echo "  ✓ Logging Configuration (logging_config.py)"
echo "  ✓ Metrics Collector (metrics_collector.py)"
echo "  ✓ Health Check (health_check.py)"
echo ""
echo "Quick start commands:"
echo "  # Real-time monitoring"
echo "  python3 monitor_paper_trading.py"
echo ""
echo "  # Health check"
echo "  python3 health_check.py"
echo ""
echo "  # Performance report"
echo "  python3 performance_dashboard.py --all"
echo ""
echo "  # Check alerts"
echo "  python3 alert_system.py --alerts"
echo ""
echo "Or use the startup scripts:"
echo "  ./scripts/start_monitor.sh"
echo "  ./scripts/health_check.sh"
echo "  ./scripts/show_dashboard.sh"
echo "  ./scripts/check_status.sh"
echo ""
echo "Directory structure:"
echo "  data/          - Trade data and metrics"
echo "  logs/          - Log files"
echo "  scripts/       - Startup scripts"
echo ""
echo "For more information, see: MONITORING_SYSTEM_GUIDE.md"
echo ""
