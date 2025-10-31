@echo off
echo ================================================== 
echo KAEL 3-HOUR PRE-LIVE TRADING TEST
echo ==================================================
echo.
echo Starting comprehensive 3-hour test...
echo This will monitor the system for 3 hours
echo.
echo Test includes:
echo  - System health checks every 5 minutes
echo  - Trading activity monitoring
echo  - Win/loss rate tracking  
echo  - Error detection
echo.
echo Dashboards available at:
echo  - Angular: http://localhost:4200
echo  - React: http://localhost:3000
echo.
echo ==================================================
echo.
pause
echo Starting test...
bash run_3hour_test.sh
pause
