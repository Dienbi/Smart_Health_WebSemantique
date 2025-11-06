@echo off
echo ========================================
echo Starting Fuseki Server with Docker
echo ========================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Start Fuseki using Docker Compose
echo Starting Fuseki server...
docker-compose up -d fuseki

REM Wait a moment for Fuseki to start
echo Waiting for Fuseki to start...
timeout /t 5 /nobreak >nul

REM Check if Fuseki is responding
echo.
echo Checking Fuseki connection...
curl -s http://localhost:3030 >nul 2>&1
if errorlevel 1 (
    echo WARNING: Fuseki may not be ready yet. Please wait a few seconds.
    echo.
    echo You can check the status with:
    echo   docker-compose ps
    echo.
    echo Or check Fuseki directly at:
    echo   http://localhost:3030
) else (
    echo.
    echo ========================================
    echo Fuseki is running!
    echo ========================================
    echo.
    echo Access Fuseki at: http://localhost:3030
    echo Dataset: smarthealth
    echo.
    echo To stop Fuseki, run:
    echo   docker-compose stop fuseki
    echo.
    echo To view logs, run:
    echo   docker-compose logs -f fuseki
    echo.
)

pause
