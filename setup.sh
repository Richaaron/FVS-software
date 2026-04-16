#!/bin/bash

# FVS Result Management System - Setup Script

echo "======================================"
echo "FVS Result Management System Setup"
echo "======================================"
echo ""

# Check Python installation
echo "Checking Python installation..."
python --version

if [ $? -ne 0 ]; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

echo ""
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully!"
else
    echo "✗ Error installing dependencies"
    exit 1
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo "  1. Start backend: python backend/app.py"
echo "  2. Open frontend: Open frontend/index.html in a web browser"
echo ""
