@echo off
REM MILITARY ANOMALY SCANNER - INSTALL DEPENDENCIES
REM Classification: TOP SECRET//SCI

echo.
echo ================================================
echo   INSTALLING DEPENDENCIES
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python found
python --version

echo.
echo [INFO] Installing pip packages...
pip install -r requirements.txt

echo.
echo ================================================
echo   DEPENDENCIES INSTALLED
echo ================================================
echo.

echo Next steps:
echo 1. Install Ollama: https://ollama.ai
echo 2. Start Ollama: ollama serve
echo 3. Pull models: ollama pull llava llama2
echo 4. Run: launch.bat
echo.

pause
