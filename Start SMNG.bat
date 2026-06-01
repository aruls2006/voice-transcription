@echo off
title Smart Meeting Note Generator
echo ==========================================================
echo     Smart Meeting Note Generator (Windows Desktop App)
echo ==========================================================
echo.

:: Ensure working directory is the exe folder
cd /d "%~dp0"

:: Check Python
echo [LOG] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 goto python_ok
py --version >nul 2>&1
if %errorlevel% equ 0 goto python_ok
echo [WARNING] Python not found. Voice transcription will not work.
echo          Install Python from https://python.org
echo.

:python_ok

:: Start server
echo [LOG] Starting Smart Meeting Notes server...
start "" /min "SmartMeetingNotes.exe"

:: Wait for server to initialize
echo [LOG] Waiting for server on port 5050...
set /a attempt=0

:wait_loop
netstat -ano | findstr :5050 | findstr LISTENING >nul
if %errorlevel% equ 0 goto server_ready
set /a attempt=%attempt%+1
if %attempt% gtr 20 goto server_timeout
ping 127.0.0.1 -n 2 >nul
goto wait_loop

:server_timeout
echo [ERROR] Server failed to start within 20 seconds.
echo Please check if port 5050 is already in use.
pause
exit /b 1

:server_ready
echo [LOG] Server is active on http://localhost:5050

:: Launch Edge in App Mode
echo [LOG] Opening application...
start msedge --app=http://localhost:5050
if %errorlevel% neq 0 (
    echo [WARNING] Edge not found. Opening in default browser...
    explorer "http://localhost:5050"
)

echo.
echo ==========================================================
echo   Smart Meeting Note Generator is now active!
echo.
echo   Local Address: http://localhost:5050
echo.
echo   HEADPHONES TIP: For Google Meet recording with headphones,
echo   open http://localhost:5050 in a normal Chrome/Edge tab
echo   (same browser as your meeting) and select "Share tab audio"
echo   when capturing.
echo.
echo   Press any key to STOP the server and exit.
echo ==========================================================
echo.
pause

echo [LOG] Stopping server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
echo [SUCCESS] Application stopped cleanly.
ping 127.0.0.1 -n 2 >nul
exit /b 0
