@echo off
REM Setup Monitoring System for Paper Trading
REM Initializes directories, creates sample data, and verifies installation

setlocal enabledelayedexpansion

echo ==================================
echo PAPER TRADING MONITORING SETUP
echo ==================================

REM Check Python availability
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.6+
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo OK Found: %PYTHON_VER%

REM Create required directories
echo.
echo Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "scripts" mkdir scripts
echo OK Directories created

REM Initialize empty data files
echo.
echo Initializing data files...

REM Create empty trades.json if not exists
if not exist "data\trades.json" (
    (echo [) > data\trades.json
    (echo ]) >> data\trades.json
    echo OK Created data\trades.json
)

REM Create empty status.json if not exists
if not exist "data\status.json" (
    (
        echo {
        echo   "is_running": false,
        echo   "connected": false,
        echo   "active_trades": 0,
        echo   "last_trade_time": null,
        echo   "uptime_seconds": 0
        echo }
    ) > data\status.json
    echo OK Created data\status.json
)

REM Create empty metrics.json if not exists
if not exist "data\metrics.json" (
    (
        echo {
        echo   "total_trades": 0,
        echo   "wins": 0,
        echo   "losses": 0,
        echo   "ties": 0,
        echo   "win_rate": 0.0,
        echo   "total_profit": 0.0,
        echo   "daily_profit": 0.0,
        echo   "daily_loss": 0.0,
        echo   "consecutive_losses": 0,
        echo   "max_drawdown": 0.0,
        echo   "trades_per_hour": 0,
        echo   "avg_profit_per_trade": 0.0
        echo }
    ) > data\metrics.json
    echo OK Created data\metrics.json
)

REM Verify Python imports
echo.
echo Checking required modules...

python -c "import json" >nul 2>&1
if not errorlevel 1 echo OK json available

python -c "import sqlite3" >nul 2>&1
if not errorlevel 1 echo OK sqlite3 available

python -c "import logging" >nul 2>&1
if not errorlevel 1 echo OK logging available

python -c "import csv" >nul 2>&1
if not errorlevel 1 echo OK csv available

REM Run health check
echo.
echo Running system health check...
python health_check.py >nul 2>&1
if not errorlevel 1 (
    echo OK Health check passed
) else (
    echo WARNING Health check reported issues (see above^)
)

REM Verify logging setup
echo.
echo Verifying logging configuration...
python logging_config.py --verify >nul 2>&1
if not errorlevel 1 (
    echo OK Logging verified
) else (
    echo WARNING Logging verification issues (non-critical^)
)

REM Create startup scripts
echo.
echo Creating startup scripts...

REM Monitor startup batch file
(
    echo @echo off
    echo REM Start paper trading monitor
    echo python monitor_paper_trading.py %%*
) > scripts\start_monitor.bat
echo OK Created scripts\start_monitor.bat

REM Health check batch file
(
    echo @echo off
    echo REM Run health check
    echo python health_check.py %%*
) > scripts\health_check.bat
echo OK Created scripts\health_check.bat

REM Dashboard batch file
(
    echo @echo off
    echo REM Show performance dashboard
    echo python performance_dashboard.py --all %%*
) > scripts\show_dashboard.bat
echo OK Created scripts\show_dashboard.bat

REM Status batch file
(
    echo @echo off
    echo REM Check current status
    echo echo === MONITORING SYSTEM STATUS ===
    echo echo.
    echo echo Health Check:
    echo python health_check.py
    echo echo.
    echo echo Recent Alerts:
    echo python alert_system.py --alerts
    echo echo.
    echo echo Metrics:
    echo python metrics_collector.py --show-stats
) > scripts\check_status.bat
echo OK Created scripts\check_status.bat

REM Print summary
echo.
echo ==================================
echo SETUP COMPLETE
echo ==================================
echo.
echo Monitoring system components:
echo   OK Real-time Monitor (monitor_paper_trading.py^)
echo   OK Performance Dashboard (performance_dashboard.py^)
echo   OK Alert System (alert_system.py^)
echo   OK Logging Configuration (logging_config.py^)
echo   OK Metrics Collector (metrics_collector.py^)
echo   OK Health Check (health_check.py^)
echo.
echo Quick start commands:
echo   python monitor_paper_trading.py
echo   python health_check.py
echo   python performance_dashboard.py --all
echo   python alert_system.py --alerts
echo.
echo Or use the startup scripts in scripts\ directory:
echo   scripts\start_monitor.bat
echo   scripts\health_check.bat
echo   scripts\show_dashboard.bat
echo   scripts\check_status.bat
echo.
echo Directory structure:
echo   data\          - Trade data and metrics
echo   logs\          - Log files
echo   scripts\       - Startup scripts
echo.
echo For more information, see: MONITORING_SYSTEM_GUIDE.md
echo.

endlocal
