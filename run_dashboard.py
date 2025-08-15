#!/usr/bin/env python3
"""
Customer Contact Centre Analytics Dashboard Launcher
Run this script to start the Streamlit dashboard locally.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'numpy', 
        'wordcloud', 'seaborn', 'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n🔧 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    return True

def prepare_data():
    """Ensure data is processed and ready"""
    processed_conversations = Path("data/processed_conversations.csv")
    processed_daily = Path("data/daily_aggregations.csv")
    
    if not processed_conversations.exists() or not processed_daily.exists():
        print("📊 Processing chat data...")
        try:
            subprocess.check_call([sys.executable, "data_processor.py"])
            print("✅ Data processed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to process data. Please check data_processor.py")
            return False
    else:
        print("✅ Processed data found!")
    
    return True

def main():
    """Main function to launch the dashboard"""
    print("🚀 Customer Contact Centre Analytics Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("dashboard.py").exists():
        print("❌ dashboard.py not found. Please run this script from the project root directory.")
        return
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return
    
    # Prepare data
    print("📋 Preparing data...")
    if not prepare_data():
        return
    
    # Launch Streamlit
    print("🌟 Launching dashboard...")
    print("📱 The dashboard will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thank you for using the analytics dashboard!")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

if __name__ == "__main__":
    main()