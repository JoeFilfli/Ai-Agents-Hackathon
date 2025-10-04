@echo off
REM Docker Start Script for Windows
REM This script helps you start the AI Agents application with Docker

echo ===================================
echo   AI Agents - Docker Startup
echo ===================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose is not installed
    echo Please install Docker Compose from: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo [OK] Docker Compose is installed
echo.

REM Check if .env.local file exists
if not exist .env.local (
    echo [WARNING] No .env.local file found
    echo Creating .env.local from env.example...
    copy env.example .env.local
    echo.
    echo [IMPORTANT] Please edit .env.local and add your OpenAI API key
    echo    File location: .env.local
    echo.
    pause
) else (
    echo [OK] Found .env.local with your API key
)

echo [OK] Environment variables configured
echo.

REM Ask user if they want to rebuild
set /p rebuild="Do you want to rebuild the images? (y/N): "
echo.

if /i "%rebuild%"=="y" (
    echo [BUILD] Building Docker images...
    docker-compose build --no-cache
    if errorlevel 1 (
        echo [ERROR] Build failed
        pause
        exit /b 1
    )
    echo [OK] Build completed successfully
    echo.
)

REM Start the services
echo [START] Starting services...
echo.
docker-compose up -d

if errorlevel 0 (
    echo.
    echo ===================================
    echo   Application Started Successfully!
    echo ===================================
    echo.
    echo Frontend:  http://localhost:3000
    echo Backend:   http://localhost:8000
    echo API Docs:  http://localhost:8000/api/py/docs
    echo.
    echo To view logs:       docker-compose logs -f
    echo To stop services:   docker-compose down
    echo.
) else (
    echo.
    echo [ERROR] Failed to start services
    echo Check logs with: docker-compose logs
    pause
    exit /b 1
)

pause

