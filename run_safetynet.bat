@echo off
echo Starting SafetyNet Reporting System...
docker-compose up -d
echo.
echo SafetyNet Reporting System is now running!
echo.
echo Access the web interface at: http://localhost:8081
echo Access the admin interface at: http://localhost:8081/admin
echo.
echo Admin credentials:
echo Username: admin
echo Password: SafeAdmin123
echo.
echo To stop the system, run: docker-compose down
echo.
pause
