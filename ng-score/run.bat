@echo off
cd /d "%~dp0"

echo.
echo  ============================================
echo   Network Goodness Score - Beer Sheva
echo  ============================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    echo  Install Python 3.9+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  Python %PYVER% detected.
echo.

:: ── Virtual environment ────────────────────────────────────────────────────
if not exist ".venv\Scripts\activate.bat" (
    echo  [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  Done.
    echo.
) else (
    echo  [1/3] Virtual environment already exists.
    echo.
)

call .venv\Scripts\activate.bat

:: ── Install requirements ───────────────────────────────────────────────────
echo  [2/3] Installing requirements (first run may take a few minutes)...
echo.
pip install -r requirements.txt --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo  ERROR: Failed to install requirements.
    pause
    exit /b 1
)
echo.
echo  Requirements ready.
echo.

:: ── Start server ───────────────────────────────────────────────────────────
echo  [3/3] Starting server...
echo.
echo  -------------------------------------------------------
echo   Open http://localhost:8000 in your browser.
echo.
echo   NOTE: First startup downloads building data from
echo   OpenStreetMap for 19 neighborhoods (~2-5 min).
echo   Subsequent startups use the local cache and are fast.
echo.
echo   Press Ctrl+C to stop the server.
echo  -------------------------------------------------------
echo.

uvicorn main:app --reload

echo.
echo  Server stopped.
pause
