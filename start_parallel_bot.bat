@echo off
REM ============================================================================
REM KAEL Autonomous Parallel Trading Bot - Start Script (Windows)
REM ============================================================================

echo ============================================================================
echo 🚀 KAEL AUTONOMOUS PARALLEL TRADING BOT - DOCKER STARTUP
echo ============================================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running
    echo    Please start Docker Desktop
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found
    echo    Please create a .env file with your IQ Option credentials
    echo    See README_PARALLEL_BOT_DOCKER.md for configuration details
    pause
    exit /b 1
)

REM Get trading mode
for /f "tokens=2 delims==" %%a in ('findstr "^TRADING_MODE=" .env') do set TRADING_MODE=%%a
if "%TRADING_MODE%"=="" set TRADING_MODE=demo

echo 📋 Configuration:
echo    Trading Mode: %TRADING_MODE%
echo.

REM Warning for live mode
if "%TRADING_MODE%"=="live" (
    echo ⚠️  WARNING: LIVE MODE ENABLED - REAL MONEY TRADING!
    echo    Press Ctrl+C within 5 seconds to cancel...
    timeout /t 5
)

REM Build the image
echo 🔨 Building Docker image...
docker-compose -f docker-compose.parallel.yml build

if errorlevel 1 (
    echo ❌ Error: Failed to build Docker image
    pause
    exit /b 1
)

echo ✅ Docker image built successfully
echo.

REM Start the container
echo 🚀 Starting parallel trading bot...
docker-compose -f docker-compose.parallel.yml up -d

if errorlevel 1 (
    echo ❌ Error: Failed to start container
    pause
    exit /b 1
)

echo ✅ Bot started successfully!
echo.

REM Wait for container to initialize
timeout /t 3 /nobreak >nul

REM Check if container is running
docker ps | findstr "kael-parallel-trading-bot" >nul
if errorlevel 1 (
    echo ❌ Error: Container failed to start
    echo    Check logs: docker-compose -f docker-compose.parallel.yml logs
    pause
    exit /b 1
)

echo ============================================================================
echo ✅ PARALLEL TRADING BOT IS RUNNING
echo ============================================================================
echo.
echo 📊 Monitoring Commands:
echo    View logs:        docker-compose -f docker-compose.parallel.yml logs -f
echo    Check health:     curl http://localhost:5001/health
echo    Get statistics:   curl http://localhost:5001/statistics
echo    Stop bot:         docker-compose -f docker-compose.parallel.yml down
echo.
echo 📁 Log files are saved in: .\logs\
echo.
echo 🏥 Health API: http://localhost:5001
echo.
echo 📋 Initial logs (last 20 lines):
echo ============================================================================
docker-compose -f docker-compose.parallel.yml logs --tail=20 parallel-trading-bot
echo ============================================================================
echo.
echo 💡 Tip: Run 'docker-compose -f docker-compose.parallel.yml logs -f' to follow logs
echo.
pause
