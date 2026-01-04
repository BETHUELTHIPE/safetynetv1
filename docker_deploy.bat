@echo off
echo CPF Crime Reporting System Docker Deployment Script
echo ==================================================

IF "%1"=="" GOTO HELP
IF "%1"=="build" GOTO BUILD
IF "%1"=="up" GOTO UP
IF "%1"=="down" GOTO DOWN
IF "%1"=="restart" GOTO RESTART
IF "%1"=="logs" GOTO LOGS
IF "%1"=="shell" GOTO SHELL
IF "%1"=="ps" GOTO PS
IF "%1"=="backup" GOTO BACKUP
IF "%1"=="help" GOTO HELP

:BUILD
echo Building Docker containers...
docker-compose build
echo.
GOTO END

:UP
echo Starting Docker containers...
docker-compose up -d
echo.
echo Services are now running! Access:
echo - Main application: http://localhost
echo - Admin interface: http://localhost/admin
echo - pgAdmin: http://localhost:5050
echo.
GOTO END

:DOWN
echo Stopping Docker containers...
docker-compose down
echo.
GOTO END

:RESTART
echo Restarting Docker containers...
docker-compose restart
echo.
GOTO END

:LOGS
IF "%2"=="" (
    echo Showing logs for all services...
    docker-compose logs --tail=100 -f
) ELSE (
    echo Showing logs for %2...
    docker-compose logs --tail=100 -f %2
)
GOTO END

:SHELL
IF "%2"=="" (
    echo Accessing web container shell...
    docker-compose exec web /bin/bash
) ELSE (
    echo Accessing %2 container shell...
    docker-compose exec %2 /bin/bash
)
GOTO END

:PS
echo Current container status:
docker-compose ps
GOTO END

:BACKUP
echo Creating database backup...
set TIMESTAMP=%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
docker-compose exec -T db pg_dump -U postgres cpfcrimereportingsystem > backup_%TIMESTAMP%.sql
echo Backup saved to backup_%TIMESTAMP%.sql
GOTO END

:HELP
echo.
echo Usage: docker_deploy.bat [command] [service]
echo.
echo Available commands:
echo   build   - Build Docker containers
echo   up      - Start Docker containers
echo   down    - Stop Docker containers
echo   restart - Restart Docker containers
echo   logs    - Show container logs (optionally specify service name)
echo   shell   - Access container shell (optionally specify service name)
echo   ps      - Show container status
echo   backup  - Create database backup
echo   help    - Show this help message
echo.
echo Examples:
echo   docker_deploy.bat build
echo   docker_deploy.bat up
echo   docker_deploy.bat logs web
echo   docker_deploy.bat shell db
echo.
GOTO END

:END
