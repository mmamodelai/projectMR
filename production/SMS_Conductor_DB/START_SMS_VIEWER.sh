#!/bin/bash
# SMS Conductor UI - Mac Launcher
# Double-click this file or run: ./START_SMS_VIEWER.sh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.8+ from:"
    echo "https://www.python.org/downloads/"
    echo ""
    echo "Or install via Homebrew:"
    echo "brew install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import supabase" 2>/dev/null; then
    echo "Installing dependencies..."
    echo ""
    python3 -m pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install dependencies!"
        echo "Try running manually:"
        echo "python3 -m pip install -r requirements.txt"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo ""
    echo "Dependencies installed successfully!"
    echo ""
fi

# Run the application
echo "Starting SMS Conductor UI..."
echo ""
python3 SMSconductor_DB.py

# If the application exits, keep terminal open to see any errors
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with an error."
    echo "Check the error message above."
    echo ""
    read -p "Press Enter to exit..."
fi

