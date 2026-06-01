@echo off
setlocal enabledelayedexpansion
title Setup Prerequisites - Smart Meeting Note Generator
echo ==========================================================
echo   Smart Meeting Note Generator - Requirements Installer
echo ==========================================================
echo.
echo This script will check for and install:
echo  1. Python (for voice transcription)
echo  2. Python SpeechRecognition module
echo  3. Node.js (for backend/frontend development)
echo  4. NPM dependencies (if source folders exist)
echo.
echo NOTE: Installing Node.js or Python may require administrative
echo privileges. You might see a Windows UAC prompt.
echo.
pause
echo.

cd /d "%~dp0"

:: ---------------------------------------------------------
:: 1. Check and Install Python
:: ---------------------------------------------------------
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Python is not installed. Attempting to install via winget...
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to install Python. Please install manually from python.org
        ) else (
            echo [SUCCESS] Python installed. 
            echo IMPORTANT: You may need to restart this script or your computer for Python to be recognized in the command line.
        )
    ) else (
        echo [-] Python (py launcher) is already installed.
    )
) else (
    echo [-] Python is already installed.
)
echo.

:: ---------------------------------------------------------
:: 2. Install Python Modules
:: ---------------------------------------------------------
echo [2/4] Installing Python modules...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install SpeechRecognition
if %errorlevel% neq 0 (
    py -m pip install SpeechRecognition
)
echo [-] Python modules installed.
echo.

:: ---------------------------------------------------------
:: 3. Check and Install Node.js
:: ---------------------------------------------------------
echo [3/4] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js is not installed. Attempting to install via winget...
    winget install -e --id OpenJS.NodeJS --accept-package-agreements --accept-source-agreements
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install Node.js. Please install manually from nodejs.org
    ) else (
        echo [SUCCESS] Node.js installed.
        echo IMPORTANT: You may need to restart this script or your computer for Node to be recognized in the command line.
    )
) else (
    echo [-] Node.js is already installed.
)
echo.

:: ---------------------------------------------------------
:: 4. Install NPM Dependencies (Development only)
:: ---------------------------------------------------------
echo [4/4] Checking for project dependencies...

if exist "backend\package.json" (
    echo [-] Installing backend dependencies...
    cd backend
    call npm install
    cd ..
) else (
    echo [-] No backend folder found (skipping npm install).
)

if exist "frontend\package.json" (
    echo [-] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
) else (
    echo [-] No frontend folder found (skipping npm install).
)
echo.

:: ---------------------------------------------------------
:: End
:: ---------------------------------------------------------
echo ==========================================================
echo   INSTALLATION COMPLETE
echo ==========================================================
echo.
echo If Python or Node.js were just installed, please close this 
echo window and open a new one to refresh your environment variables.
echo.
pause
