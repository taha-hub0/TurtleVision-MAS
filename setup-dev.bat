@echo off
REM Turtle-ID Multi-Agent System - Development Setup (Windows)

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║  Turtle-ID - Development Environment Setup (Windows)  ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✓ Node.js %NODE_VERSION%

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ %PYTHON_VERSION%

REM Setup Backend
echo.
echo 📦 Setting up Backend...
cd backend
call npm install
if not exist .env copy .env.example .env
echo ✓ Backend setup complete
cd ..

REM Setup Image Analysis Agent
echo.
echo 📦 Setting up Image Analysis Agent...
cd image-analysis-agent

if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo ✓ Image Analysis Agent setup complete
cd ..

REM Setup Database Agent
echo.
echo 📦 Setting up Database Agent...
cd database-agent

if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo ✓ Database Agent setup complete
cd ..

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║  Setup Complete! 🎉                                   ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo   1. Configure environment variables in .env files
echo   2. Set up MySQL database
echo   3. Run database migrations
echo   4. Start services in separate terminals:
echo      Terminal 1: cd backend ^&^& npm run dev
echo      Terminal 2: cd image-analysis-agent ^&^& venv\Scripts\activate ^&^& python app.py
echo      Terminal 3: cd database-agent ^&^& venv\Scripts\activate ^&^& python app.py
echo.
echo Or use Docker:
echo   docker-compose up -d
echo.
pause
