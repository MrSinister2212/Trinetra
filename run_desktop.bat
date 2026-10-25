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

if not exist backend\app\modules\data\sites.json (
    echo [Setup] Generating 500+ site definitions...
    python backend\generate_sites.py
)

if not exist frontend\dist (
    echo [Setup] Building frontend production bundle...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

echo [TRINETRA] Launching native desktop window...
python trinetra_desktop.py
