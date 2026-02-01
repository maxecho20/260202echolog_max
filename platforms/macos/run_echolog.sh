#!/bin/bash
# EchoLog macOS Launcher
# ======================
# Run this script to start EchoLog on macOS

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Check if virtual environment exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "⚠️ Virtual environment not found. Creating one..."
    python3 -m venv "$PROJECT_ROOT/venv"
    source "$PROJECT_ROOT/venv/bin/activate"
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "⚠️ .env file not found. Creating from example..."
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo "📝 Please edit .env file to add your DEEPGRAM_API_KEY"
    fi
fi

# Run the macOS GUI
cd "$PROJECT_ROOT"
python "$SCRIPT_DIR/main_gui_macos.py"
