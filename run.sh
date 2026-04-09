#!/bin/bash
# run.sh - Quick start script for Reddit Hive Mind backend

echo "🚀 Starting Reddit Hive Mind Backend Setup..."

# Set up data dir
mkdir -p data

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r backend/requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating default .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update your .env file with actual Reddit credentials!"
fi

# Download NLTK VADER lexicon
echo "Downloading NLTK VADER Lexicon..."
python -c "import nltk; nltk.download('vader_lexicon', quiet=True)"

# Run the Uvicorn server
echo "Starting Uvicorn Server on port 8080..."
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
