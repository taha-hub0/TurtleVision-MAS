@echo off
REM Turtle-ID MAS - System Health Check Script (Windows)
REM 
REM Bu betik tüm ajanların sağlık durumunu kontrol eder
REM ve sistem test'ini çalıştırır.
REM
REM Kullanım: test-system.bat

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       Turtle-ID Multi-Agent System - Health Check             ║
echo ║                    Windows Version                             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Configuration
set BACKEND_URL=http://localhost:3000
set IMAGE_ANALYSIS_URL=http://localhost:5000
set DATABASE_URL=http://localhost:5001
set TIMEOUT=5

echo ═══ Agent Health Checks ═══
echo.

REM Check Backend
echo Checking Backend Coordinator...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BACKEND_URL%/health' -TimeoutSec %TIMEOUT% -ErrorAction Stop; Write-Host 'OK' -ForegroundColor Green } catch { Write-Host 'FAILED' -ForegroundColor Red; exit 1 }"
if errorlevel 1 exit /b 1

REM Check Image Analysis
echo Checking Image Analysis Agent...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%IMAGE_ANALYSIS_URL%/health' -TimeoutSec %TIMEOUT% -ErrorAction Stop; Write-Host 'OK' -ForegroundColor Green } catch { Write-Host 'FAILED' -ForegroundColor Red; exit 1 }"
if errorlevel 1 exit /b 1

REM Check Database
echo Checking Database Agent...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%DATABASE_URL%/health' -TimeoutSec %TIMEOUT% -ErrorAction Stop; Write-Host 'OK' -ForegroundColor Green } catch { Write-Host 'FAILED' -ForegroundColor Red; exit 1 }"
if errorlevel 1 exit /b 1

echo.
echo ═══ Agent-Specific Checks ═══
echo.

REM Check Gatekeeper
echo Checking Gatekeeper Agent...
powershell -Command "try { Invoke-WebRequest -Uri '%BACKEND_URL%/api/validation/health' -TimeoutSec %TIMEOUT% -ErrorAction Stop | Out-Null; Write-Host 'OK' -ForegroundColor Green } catch { Write-Host 'FAILED' -ForegroundColor Red }"

REM Check Biolytics
echo Checking Biolytics Agent...
powershell -Command "try { Invoke-WebRequest -Uri '%IMAGE_ANALYSIS_URL%/api/biolytics/health' -TimeoutSec %TIMEOUT% -ErrorAction Stop | Out-Null; Write-Host 'OK' -ForegroundColor Green } catch { Write-Host 'FAILED' -ForegroundColor Red }"

REM Check Matching
echo Checking Matching Agent...
powershell -Command "try { Invoke-WebRequest -Uri '%BACKEND_URL%/api/matching/health' -TimeoutSec %TIMEOUT% -ErrorAction Stop | Out-Null; Write-Host 'OK' -ForegroundColor Green } catch { Write-Host 'FAILED' -ForegroundColor Red }"

REM Check Reporter
echo Checking Reporter Agent...
powershell -Command "try { Invoke-WebRequest -Uri '%BACKEND_URL%/api/reporting/health' -TimeoutSec %TIMEOUT% -ErrorAction Stop | Out-Null; Write-Host 'OK' -ForegroundColor Green } catch { Write-Host 'FAILED' -ForegroundColor Red }"

echo.
echo ═══ Running Integration Tests ═══
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Node.js not found in PATH
    echo Please install Node.js or add it to PATH
) else (
    cd backend
    if exist tests\integration.test.js (
        echo Running integration tests...
        node tests\integration.test.js
        cd ..
    ) else (
        echo WARNING: Integration test file not found
        cd ..
    )
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   System Check Complete                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Turtle-ID System Summary:
echo   Backend:     %BACKEND_URL%
echo   Image Srv:   %IMAGE_ANALYSIS_URL%
echo   Database:    %DATABASE_URL%
echo.
echo Documentation:
echo   - SOLID Agents: docs\SOLID_AGENTS.md
echo   - API Reference: docs\API.md
echo   - Database: docs\DATABASE_SCHEMA.md
echo.

endlocal
