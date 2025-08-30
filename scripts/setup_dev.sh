#!/bin/bash

# Install UV if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
uv pip install -r requirements-dev.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Development environment setup complete!"
echo "To activate the virtual environment, run: source .venv/bin/activate" 