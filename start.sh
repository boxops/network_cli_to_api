#!/bin/bash

# Start script for Network API Gateway

set -e

echo "Starting Network API Gateway..."

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration!"
fi

# Create necessary directories
mkdir -p session_logs data

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    echo "Running locally"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Run the application
    echo "Starting application..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
