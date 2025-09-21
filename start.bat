@echo off
echo ========================================
echo   Smart Rental Tracker - Startup Script
echo ========================================
echo.

REM Set the working directory to the project root
cd /d "%~dp0"

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ and add it to your PATH
    pause
    exit /b 1
)
echo ✓ Node.js found

echo.
echo [3/4] Setting up Backend (FastAPI)...
cd backend

REM Check if virtual environment exists, if not create it
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing/updating Python dependencies...
pip install -r requirements.txt --quiet

REM Check if database exists, if not populate it
if not exist "app\rental.db" (
    echo Database not found, populating with sample data...
    python populate_database.py
)

REM Start backend in a new window
echo Starting FastAPI backend server...
start "Smart Rental Tracker - Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [4/4] Setting up Frontend (Next.js)...
cd ..\frontend

REM Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)

REM Start frontend in a new window
echo Starting Next.js frontend server...
start "Smart Rental Tracker - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   🚀 Smart Rental Tracker Started!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:3000
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
