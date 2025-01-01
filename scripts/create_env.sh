#!/bin/bash

# Set the directory for the virtual environment
ENV_DIR=$(pwd)/env

# Check if the virtual environment exists
if [ ! -d "$ENV_DIR" ]; then
  echo "Virtual environment not found. Creating one..."
  python -m venv "$ENV_DIR"
else
  echo "Virtual environment already exists. Skipping creation."
fi
