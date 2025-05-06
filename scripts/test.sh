#!/bin/bash

# Test script for the Heart of News backend

set -e

# Run linting
echo "Running linting..."
flake8 app tests

# Run type checking
echo "Running type checking..."
mypy app

# Run tests
echo "Running tests..."
pytest -v --cov=app tests/