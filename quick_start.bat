@echo off
REM ============================================================================
REM KAEL Trading Bot - Windows Quick Start Script
REM ============================================================================

echo ================================================================================================
echo ^🤖 KAEL AUTONOMOUS PARALLEL TRADING BOT - QUICK START
echo ================================================================================================
echo.

REM Check if Docker is running
echo Checking Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker Desktop is not running!
    echo.
    echo 🔧 ACTION REQUIRED:
    echo    1. Open Docker Desktop
    echo    2. Wait for it to fully start ^(green icon in system tray^)
    echo    3. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Desktop is running
echo.

REM Check if .env exists
if not exist ".env" (
    echo ❌ ERROR: .env file not found!
    echo    Please create a .env file with your IQ Option credentials.
    pause
    exit /b 1
)

echo ✅ .env file found
echo.

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker-compose -f docker-compose.parallel.yml down 2>nul

REM Build the image
echo.
echo 🔨 Building Docker image ^(this may take a few minutes^)...
docker-compose -f docker-compose.parallel.yml build
if %errorlevel% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

REM Start the services
echo.
echo 🚀 Starting trading bot...
docker-compose -f docker-compose.parallel.yml up -d
if %errorlevel% neq 0 (
    echo ❌ Start failed!
    pause
    exit /b 1
)

REM Wait for initialization
echo.
echo ⏳ Waiting for services to initialize...
timeout /t 30 /nobreak >nul

REM Show status
echo.
echo 📊 Container Status:
docker-compose -f docker-compose.parallel.yml ps

REM Show initial logs
echo.
echo ================================================================================================
echo 📋 INITIAL LOGS
echo ================================================================================================
docker-compose -f docker-compose.parallel.yml logs --tail=50 parallel-trading-bot

echo.
echo ================================================================================================
echo ✅ TRADING BOT IS RUNNING
echo ================================================================================================
echo.
echo 📡 Health API: http://localhost:5001
echo 📊 Statistics: http://localhost:5001/statistics
echo.
echo 🔍 Monitor commands:
echo    View logs:        docker-compose -f docker-compose.parallel.yml logs -f
echo    View stats:       curl http://localhost:5001/statistics
echo    Stop bot:         docker-compose -f docker-compose.parallel.yml down
echo    Restart bot:      docker-compose -f docker-compose.parallel.yml restart
echo.
echo 💡 Run monitoring dashboard:
echo    python monitor_dashboard.py
echo.
echo    OR automated monitoring:
echo    python run_monitor_adjust.py
echo.
echo ================================================================================================
echo.

pause
