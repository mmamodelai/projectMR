#!/bin/bash
# SMS Conductor Database Viewer - Mac Launcher
# Automatically installs dependencies and runs the viewer

echo "=========================================="
echo "  SMS Conductor Database Viewer"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if running from correct directory
if [ ! -f "SMSconductor_DB.py" ]; then
    echo "ERROR: SMSconductor_DB.py not found"
    echo "Please run this script from the conductor-sms directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    deactivate
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Run the viewer
echo "Starting SMS Conductor Database Viewer..."
echo ""
pythonw SMSconductor_DB.py

# Deactivate virtual environment when done
deactivate

