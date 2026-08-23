@echo off
REM Turtle-ID Multi-Agent System - Quick Start Script (Windows)

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║  Turtle-ID Multi-Agent System - Quick Start (Windows) ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✓ Docker found

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✓ Docker Compose found

echo.
echo Starting Turtle-ID services...
echo.

docker-compose up -d

if errorlevel 1 (
    echo ❌ Failed to start services. Check Docker installation.
    pause
    exit /b 1
)

echo.
echo ✓ Services started!
echo.
echo Endpoints:
echo   - Coordinator:       http://localhost:3000
echo   - Image Analysis:    http://localhost:5000
echo   - Database Agent:    http://localhost:5001
echo   - MySQL:             localhost:3306
echo.
echo Check health status:
echo   curl http://localhost:3000/api/health
echo.
echo View logs:
echo   docker-compose logs -f
echo.
echo Stop services:
echo   docker-compose down
echo.
pause
