@echo off
REM Docker Quick Start Script for Global Server (GS1) - Windows

setlocal enabledelayedexpansion

echo.
echo ======================================
echo Global Server Docker Setup
echo ======================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo [OK] Docker and Docker Compose are installed
echo.

echo Building Docker images...
docker-compose build

echo.
echo ======================================
echo Starting services...
echo ======================================
echo.

REM Start services
docker-compose up -d

echo.
echo ======================================
echo Services Started!
echo ======================================
echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak

echo.
echo Checking service health...
echo.

echo Checking MySQL...
docker exec gs1_mysql mysqladmin ping -u root -proot >nul 2>&1
if errorlevel 1 (
    echo MySQL: Starting up...
) else (
    echo MySQL: [OK] Running
)

echo Checking Application...
for /f %%i in ('curl -s -o /dev/null -w "%%{http_code}" http://localhost:9000/health 2^>nul') do set HTTP_CODE=%%i
if "%HTTP_CODE%"=="200" (
    echo Application (GS1): [OK] Running
) else (
    echo Application (GS1): Starting up...
)

echo.
echo ======================================
echo Docker containers are running!
echo ======================================
echo.
echo Access Points:
echo   - Web UI (GS1): http://localhost:9000
echo   - API (GS1): http://localhost:9000/api
echo   - CA Service: http://localhost:9002
echo   - CA API: http://localhost:9002/api
echo   - Database: localhost:3306
echo.
echo Database Credentials:
echo   - Username: root
echo   - Password: root
echo   - Database: gs1
echo.
echo Useful Commands:
echo   - View logs: docker-compose logs -f
echo   - GS1 logs: docker-compose logs -f gs1_app
echo   - CA logs: docker-compose logs -f ca_service
echo   - Stop: docker-compose stop
echo   - Restart: docker-compose restart
echo   - Down: docker-compose down
echo.
echo Documentation: See DOCKER_SETUP.md and CA_management/DOCKER_README.md
echo.

pause
