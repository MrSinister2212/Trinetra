#!/usr/bin/env bash
echo "==================================================="
echo "  TRINETRA - Modular OSINT Desktop Application"
echo "==================================================="

# Check python environment
if [ -d ".venv" ]; then
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
else
    echo "[Setup] Creating virtual environment..."
    python -m venv .venv
    source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
    pip install -r backend/requirements.txt
    pip install pywebview pyinstaller
fi

# Ensure sites.json exists
if [ ! -f "backend/app/modules/data/sites.json" ]; then
    echo "[Setup] Generating 500+ site definitions..."
    python backend/generate_sites.py
fi

# Ensure frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "[Setup] Building frontend bundle..."
    cd frontend && npm install && npm run build && cd ..
fi

echo "[TRINETRA] Launching native desktop application..."
python trinetra_desktop.py
