@echo off
echo SafetyNet Reporting System - Utility Menu
echo ======================================
echo.
echo 1. Start SafetyNet System
echo 2. Stop SafetyNet System
echo 3. View Logs
echo 4. Restart SafetyNet System
echo 5. Check System Status
echo 6. Reset Database (WARNING: All data will be lost)
echo 0. Exit
echo.

set /p choice=Enter your choice (0-6): 

if "%choice%"=="1" (
    echo Starting SafetyNet Reporting System...
    docker-compose up -d
    echo SafetyNet System started. Access at http://localhost:8081
    pause
    goto menu
)

if "%choice%"=="2" (
    echo Stopping SafetyNet Reporting System...
    docker-compose down
    echo SafetyNet System stopped.
    pause
    goto menu
)

if "%choice%"=="3" (
    echo Viewing logs (press Ctrl+C to exit)...
    docker-compose logs -f
    pause
    goto menu
)

if "%choice%"=="4" (
    echo Restarting SafetyNet Reporting System...
    docker-compose restart
    echo SafetyNet System restarted.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo Checking System Status...
    docker-compose ps
    pause
    goto menu
)

if "%choice%"=="6" (
    echo WARNING: This will delete all data in the database.
    set /p confirm=Are you sure you want to continue? (y/n): 
    if /i "%confirm%"=="y" (
        echo Resetting database...
        docker-compose down -v
        docker-compose up -d
        echo Database reset complete.
    ) else (
        echo Database reset cancelled.
    )
    pause
    goto menu
)

if "%choice%"=="0" (
    echo Exiting...
    exit
) else (
    echo Invalid choice. Please try again.
    pause
    goto menu
)

:menu
cls
goto menu
