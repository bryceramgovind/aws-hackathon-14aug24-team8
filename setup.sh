#!/bin/bash

# Enhanced Call Center AI Setup Script
echo "🚀 Setting up Enhanced Call Center AI with RAG..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [ "$(echo "$python_version >= 3.8" | bc -l)" -eq 1 ]; then
    echo "✅ Python $python_version is compatible"
else
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install boto3 botocore python-dotenv pyyaml

# Install data processing dependencies
echo "📊 Installing data processing libraries..."
pip install pandas numpy scikit-learn

# Install ML/NLP dependencies
echo "🧠 Installing ML and NLP libraries..."
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers transformers
pip install faiss-cpu

# Install remaining dependencies
echo "📦 Installing remaining dependencies..."
pip install -r requirements.txt

# Check AWS CLI
echo "☁️  Checking AWS CLI..."
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI is installed"
    aws --version
else
    echo "⚠️  AWS CLI not found. Installing..."
    pip install awscli
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/processed
mkdir -p logs
mkdir -p backup

# Set up environment file template
echo "🔧 Creating environment template..."
cat > .env.template << EOL
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# S3 Configuration
S3_BUCKET_NAME=your-bucket-name

# Optional: Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-v2

# Logging
LOG_LEVEL=INFO
EOL

echo "📝 Environment template created at .env.template"
echo "   Please copy to .env and fill in your AWS credentials"

# Test imports
echo "🧪 Testing critical imports..."
python3 -c "
try:
    import boto3
    import pandas as pd
    import numpy as np
    import sentence_transformers
    import faiss
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Check data file
echo "📊 Checking for data file..."
if [ -f "data/customer_service_chats.json" ]; then
    echo "✅ Customer service chat data found"
    
    # Get basic stats
    chat_count=$(python3 -c "
import json
try:
    with open('data/customer_service_chats.json', 'r') as f:
        data = json.load(f)
    print(f'📈 Found {len(data)} chat messages')
    
    # Count unique conversations
    contacts = set(msg.get('contact_id') for msg in data if 'contact_id' in msg)
    print(f'💬 Across {len(contacts)} conversations')
except Exception as e:
    print(f'⚠️  Error reading data: {e}')
")
    echo "$chat_count"
else
    echo "⚠️  Customer service chat data not found at data/customer_service_chats.json"
    echo "   Please ensure your data file is in the correct location"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Copy .env.template to .env and add your AWS credentials"
echo "3. Run the demo: python demo_rag.py"
echo "4. Or preprocess your data: python data/preprocess_data.py"
echo ""
echo "📚 See README_RAG.md for detailed usage instructions"
