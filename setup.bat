@echo off
REM FVS Result Management System - Setup Script for Windows

echo ======================================
echo FVS Result Management System Setup
echo ======================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version

if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt

if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo To start the application:
echo   1. Start backend: python backend/app.py
echo   2. Open frontend: Open frontend/index.html in a web browser
echo.
pause
