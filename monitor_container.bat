@echo off
REM KAEL Trading Bot Container Monitor
REM This script monitors the Docker container and displays real-time logs

echo ================================================================================
echo  KAEL Parallel Trading Bot - Container Monitor
echo ================================================================================
echo.

:menu
echo [1] View Live Logs
echo [2] Check Container Status
echo [3] Check Health Status
echo [4] View Last 50 Log Lines
echo [5] Restart Container
echo [6] Stop Container
echo [7] View Container Stats
echo [Q] Quit
echo.
set /p choice="Select option: "

if /i "%choice%"=="1" goto live_logs
if /i "%choice%"=="2" goto status
if /i "%choice%"=="3" goto health
if /i "%choice%"=="4" goto last_logs
if /i "%choice%"=="5" goto restart
if /i "%choice%"=="6" goto stop
if /i "%choice%"=="7" goto stats
if /i "%choice%"=="Q" goto end
goto menu

:live_logs
echo.
echo Showing live logs (Ctrl+C to stop)...
echo.
docker logs -f kael-parallel-trading-bot
goto menu

:status
echo.
docker ps --filter "name=kael" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
pause
goto menu

:health
echo.
echo Checking health endpoint...
curl -s http://localhost:5001/health | python -m json.tool
echo.
pause
goto menu

:last_logs
echo.
echo Last 50 log lines:
echo ================================================================================
docker logs --tail 50 kael-parallel-trading-bot
echo ================================================================================
echo.
pause
goto menu

:restart
echo.
echo Restarting container...
docker-compose -f docker-compose.parallel.yml restart parallel-trading-bot
echo.
echo Container restarted!
pause
goto menu

:stop
echo.
echo Stopping container...
docker-compose -f docker-compose.parallel.yml stop parallel-trading-bot
echo.
echo Container stopped!
pause
goto menu

:stats
echo.
echo Container resource usage:
echo ================================================================================
docker stats kael-parallel-trading-bot --no-stream
echo ================================================================================
echo.
pause
goto menu

:end
echo.
echo Exiting monitor...
exit /b 0
