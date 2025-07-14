#!/bin/bash

# ChoibenAssist AI Backend - Quick Setup Script
# This script demonstrates the automated setup using Makefile

set -e  # Exit on any error

echo "🚀 ChoibenAssist AI Backend - Quick Setup"
echo "=========================================="
echo ""

# Check if make is available
if ! command -v make &> /dev/null; then
    echo "❌ Error: 'make' is not installed"
    echo "Please install make first:"
    echo "  macOS: Already included with Xcode Command Line Tools"
    echo "  Ubuntu/Debian: sudo apt-get install build-essential"
    echo "  CentOS/RHEL: sudo yum groupinstall 'Development Tools'"
    exit 1
fi

# Check if python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.12+ first"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Run the automated setup
echo "🔧 Running automated setup..."
make setup

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit the .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Start the development server:"
echo "   make run"
echo ""
echo "3. Check available commands:"
echo "   make help"
echo ""
echo "🌐 Once running, visit:"
echo "  - API Docs: http://127.0.0.1:8000/docs"
echo "  - Health Check: http://127.0.0.1:8000/api/health"
