@echo off
REM MILITARY ANOMALY SCANNER - QUICK LAUNCH
REM Classification: TOP SECRET//SCI

echo.
echo ================================================
echo   MILITARY ANOMALY SCANNER - MISSION CONTROL
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.8+
    pause
    exit /b 1
)

REM Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama not running. Starting...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Select operation mode:
echo [1] Full Scan (50 pages, 200 images)
echo [2] Quick Scan (10 pages, 50 images)
echo [3] Custom Scan
echo [4] Analyze Local Images Only
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo [INFO] Initiating Full Scan...
    python main.py --pages 50 --images 200
) else if "%choice%"=="2" (
    echo [INFO] Initiating Quick Scan...
    python main.py --pages 10 --images 50
) else if "%choice%"=="3" (
    set /p pages="Enter number of pages: "
    set /p images="Enter number of images: "
    echo [INFO] Initiating Custom Scan...
    python main.py --pages %pages% --images %images%
) else if "%choice%"=="4" (
    set /p local_dir="Enter path to images folder: "
    echo [INFO] Local analysis mode...
    python analyze_local.py --input "%local_dir%"
) else (
    echo [ERROR] Invalid choice
    pause
    exit /b 1
)

echo.
echo ================================================
echo   MISSION COMPLETE - CHECK DATA/REPORTS/
echo ================================================
pause
