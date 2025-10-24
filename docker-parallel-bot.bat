@echo off
REM ============================================================================
REM KAEL Parallel Trading Bot - Docker Management Script (Windows)
REM ============================================================================

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.parallel.yml
set CONTAINER_NAME=kael-parallel-trading-bot

REM Colors for Windows (limited support)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "NC=[0m"

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="build" goto :build
if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="logs" goto :logs
if "%1"=="status" goto :status
if "%1"=="clean" goto :clean
if "%1"=="monitor" goto :monitor

echo %RED%Unknown command: %1%NC%
goto :help

:help
echo ==========================================================================
echo   %CYAN%KAEL Parallel Trading Bot - Docker Manager%NC%
echo ==========================================================================
echo.
echo Usage: docker-parallel-bot.bat [command]
echo.
echo Commands:
echo   build      Build the Docker image
echo   start      Start the bot
echo   stop       Stop the bot
echo   restart    Restart the bot
echo   logs       View bot logs (live)
echo   status     Show bot status and statistics
echo   clean      Remove container and image
echo   monitor    Start monitoring (requires Git Bash)
echo   help       Show this help message
echo.
echo Examples:
echo   docker-parallel-bot.bat build
echo   docker-parallel-bot.bat start
echo   docker-parallel-bot.bat logs
echo.
echo ==========================================================================
goto :eof

:build
echo %CYAN%Building Docker image...%NC%
docker-compose -f %COMPOSE_FILE% build --no-cache
if %errorlevel% equ 0 (
    echo %GREEN%Build completed!%NC%
) else (
    echo %RED%Build failed!%NC%
)
goto :eof

:start
echo %CYAN%Starting KAEL Parallel Trading Bot...%NC%
docker-compose -f %COMPOSE_FILE% up -d
if %errorlevel% equ 0 (
    echo %GREEN%Bot started!%NC%
    echo %CYAN%View logs with: docker-parallel-bot.bat logs%NC%
    echo %CYAN%Check status with: docker-parallel-bot.bat status%NC%
) else (
    echo %RED%Failed to start bot!%NC%
)
goto :eof

:stop
echo %CYAN%Stopping KAEL Parallel Trading Bot...%NC%
docker-compose -f %COMPOSE_FILE% stop
if %errorlevel% equ 0 (
    echo %GREEN%Bot stopped!%NC%
) else (
    echo %RED%Failed to stop bot!%NC%
)
goto :eof

:restart
echo %CYAN%Restarting KAEL Parallel Trading Bot...%NC%
docker-compose -f %COMPOSE_FILE% restart
if %errorlevel% equ 0 (
    echo %GREEN%Bot restarted!%NC%
) else (
    echo %RED%Failed to restart bot!%NC%
)
goto :eof

:logs
echo %CYAN%Showing logs (Ctrl+C to exit)...%NC%
docker-compose -f %COMPOSE_FILE% logs -f
goto :eof

:status
echo %CYAN%Container Status:%NC%
docker-compose -f %COMPOSE_FILE% ps
echo.
docker ps --filter "name=%CONTAINER_NAME%" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo %CYAN%Bot Statistics:%NC%
curl -s http://localhost:5001/statistics 2>nul
if %errorlevel% neq 0 (
    echo %YELLOW%API not responding. Bot may still be starting...%NC%
)
goto :eof

:clean
echo %YELLOW%This will remove the container and image. Are you sure? (Y/N)%NC%
set /p confirm=
if /i "%confirm%"=="Y" (
    echo %CYAN%Cleaning up...%NC%
    docker-compose -f %COMPOSE_FILE% down -v
    docker rmi kael-parallel-trading-bot 2>nul
    echo %GREEN%Cleanup completed!%NC%
) else (
    echo %CYAN%Cleanup cancelled%NC%
)
goto :eof

:monitor
echo %CYAN%Starting monitor (requires Git Bash)...%NC%
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" -c "./monitor_parallel_bot.sh"
) else (
    echo %RED%Git Bash not found!%NC%
    echo Please install Git for Windows or run monitor_parallel_bot.sh manually
    echo.
    echo Alternative: View logs with: docker-parallel-bot.bat logs
)
goto :eof
