#!/bin/bash

set -e

# Configuration
VENV_DIR=".venv"
PYTHON_VERSION="python3"
WHISPER_CPP_DIR="whisper.cpp"
WHISPER_MODEL="small"
PYTHON_SCRIPT="main.py"

echo "=========================================="
echo "Meeting Summarizer - Fast Setup"
echo "=========================================="

# Check Python
if ! command -v $PYTHON_VERSION &>/dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

echo "[1/5] Python3 found: $(python3 --version)"

# Create virtual environment if needed
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/5] Creating virtual environment..."
    $PYTHON_VERSION -m venv $VENV_DIR
else
    echo "[2/5] Using existing virtual environment"
fi

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install dependencies (fast - only 3 packages)
echo "[4/5] Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Check FFmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "Warning: FFmpeg is not installed"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Install with: brew install ffmpeg"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Install with: sudo apt-get install ffmpeg"
    fi
fi

# Check whisper.cpp
if [ ! -d "$WHISPER_CPP_DIR" ]; then
    echo "[5/5] Setting up whisper.cpp..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd $WHISPER_CPP_DIR
    make -j4
    cd ..
    
    # Download model
    if [ ! -f "./$WHISPER_CPP_DIR/models/ggml-$WHISPER_MODEL.bin" ]; then
        echo "Downloading Whisper $WHISPER_MODEL model..."
        ./$WHISPER_CPP_DIR/models/download-ggml-model.sh $WHISPER_MODEL
    fi
else
    echo "[5/5] whisper.cpp already installed"
fi

# Run the app
echo ""
echo "=========================================="
echo "Starting Meeting Summarizer..."
echo "=========================================="
echo "Note: Make sure Ollama is running at $OLLAMA_SERVER_URL"
echo ""

python "$PYTHON_SCRIPT"
