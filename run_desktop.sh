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

# Determine python binary
if [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_BIN=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python"
fi

# Ensure greenlet is installed (required by SQLAlchemy asyncio)
"$PYTHON_BIN" -c "import greenlet" 2>/dev/null || "$PYTHON_BIN" -m pip install "greenlet>=3.0.0" "sqlalchemy[asyncio]"

# Ensure sites.json exists
if [ ! -f "backend/app/modules/data/sites.json" ]; then
    echo "[Setup] Generating 500+ site definitions..."
    "$PYTHON_BIN" backend/generate_sites.py
fi

# Ensure frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "[Setup] Building frontend bundle..."
    cd frontend && npm install && npm run build && cd ..
fi

echo "[TRINETRA] Launching native desktop application..."
"$PYTHON_BIN" trinetra_desktop.py
