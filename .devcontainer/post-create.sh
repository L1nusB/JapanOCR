#!/bin/bash
set -e

echo "Setting up workspace..."
# Activate the base environment
echo "Activating base environment"
source /opt/conda/etc/profile.d/conda.sh
conda activate base

echo "Testing Tesseract installation..."
python -c "import pytesseract; print('Tesseract OCR setup successful!')"
tesseract --version

echo "Creating example files directory..."
mkdir -p samples
mkdir -p output

echo "Environment setup complete!"