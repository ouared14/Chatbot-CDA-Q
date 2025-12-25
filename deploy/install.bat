@echo off
echo ========================================
echo    AskLAQ2 Application Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed!
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python is installed.
echo Installing required packages...

REM Install required packages
pip install flask torch pandas sentence-transformers gradio scikit-learn numpy waitress

echo.
echo Installation complete!
echo.
echo To run the application, double-click on "AskLAQ2.exe"
echo or run "launch_app.py" with Python.
echo.
pause
