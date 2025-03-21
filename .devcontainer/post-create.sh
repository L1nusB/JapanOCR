#!/bin/bash
set -e

echo "Activating base environment..."
# Activate the base environment
source /opt/conda/bin/activate base-env

echo "Installing additional packages (mamba)..."
# Install the remaining packages
mamba install -y -c conda-forge \
  pdf2image \
  opencv \
  poppler \
  ipywidgets \
  matplotlib \
  black \
  pylint \
  mypy

echo "Installing additional packages (pip)..."
# Install pip packages
pip install pytest pytest-cov
# pip install -r requirements.txt

echo "Testing Tesseract installation..."
tesseract --version

echo "Creating example files directory..."
mkdir -p samples
mkdir -p output

echo "Environment setup complete!"