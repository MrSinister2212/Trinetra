@echo off
title TRINETRA OSINT Platform
echo ===================================================
echo   TRINETRA - Modular OSINT Desktop Application
echo ===================================================
echo Starting TRINETRA Native Desktop Suite...

if not exist .venv (
    echo [Setup] Creating Python virtual environment...
    python -m venv .venv
    call .\.venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
    pip install pywebview pyinstaller
) else (
    call .\.venv\Scripts\activate.bat
)

if exist .venv\Scripts\python.exe (
    set "PYTHON_BIN=.\.venv\Scripts\python.exe"
) else (
    set "PYTHON_BIN=python"
)

REM Ensure greenlet is present for SQLAlchemy asyncio
%PYTHON_BIN% -c "import greenlet" 2>nul || %PYTHON_BIN% -m pip install "greenlet>=3.0.0" "sqlalchemy[asyncio]"

if not exist backend\app\modules\data\sites.json (
    echo [Setup] Generating 500+ site definitions...
    %PYTHON_BIN% backend\generate_sites.py
)

if not exist frontend\dist (
    echo [Setup] Building frontend production bundle...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

echo [TRINETRA] Launching native desktop window...
%PYTHON_BIN% trinetra_desktop.py
