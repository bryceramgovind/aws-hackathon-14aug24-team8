#!/bin/bash

# Customer Contact Centre Analytics Dashboard Launcher
echo "🚀 Customer Contact Centre Analytics Dashboard"
echo "================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "🔧 Installing dependencies..."
pip3 install -r requirements.txt

# Process data if needed
if [ ! -f "data/processed_conversations.csv" ]; then
    echo "📊 Processing chat data..."
    python3 data_processor.py
fi

# Launch dashboard
echo "🌟 Launching dashboard..."
echo "📱 The dashboard will open in your default web browser"
echo "🔗 URL: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the server"
echo "================================================="

streamlit run dashboard.py --server.port 8501 --browser.gatherUsageStats false