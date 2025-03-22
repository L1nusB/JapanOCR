#!/bin/bash

set -e

echo "Installing additional Python requirements..."
pip install -r requirements.txt

echo "Testing Tesseract installation..."
tesseract --version

echo "Creating example files directory..."
mkdir -p samples
mkdir -p output

# Download a sample image for testing
curl -s -o samples/sample.png https://i.imgur.com/TZ3ap6k.png

echo "Setting up Jupyter notebook for examples..."
cat > examples.ipynb << 'EOL'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Tesseract OCR Wrapper Examples\n",
    "\n",
    "This notebook demonstrates how to use the TesseractOCR wrapper."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "import os\n",
    "from pathlib import Path\n",
    "from tesseract_ocr import TesseractOCR, TesseractConfig"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Basic Usage"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Initialize OCR object\n",
    "ocr = TesseractOCR(default_output_dir=\"output\")\n",
    "\n",
    "# Process a sample image\n",
    "text = ocr.process(\"samples/sample.png\", return_text=True)\n",
    "print(text)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Advanced Configuration"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Create a custom configuration\n",
    "config = TesseractConfig(\n",
    "    lang=\"eng\",\n",
    "    psm=6,  # Assume a single uniform block of text\n",
    "    oem=1,  # Use LSTM neural network mode\n",
    "    output_pdf=True  # Generate PDF output\n",
    ")\n",
    "\n",
    "# Process with custom configuration\n",
    "ocr.process(\"samples/sample.png\", config=config)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Processing Multiple Files"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Process all files in a directory\n",
    "results = ocr.process(\"samples\", recursive=True, return_text=True)\n",
    "\n",
    "# Display results\n",
    "for file, text in results.items():\n",
    "    print(f\"\\n===== {file} =====\\n\")\n",
    "    print(text if text else \"[No text extracted]\")\n",
    "    print(\"\\n\" + \"-\"*50)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOL

echo "Creating a simple README..."
cat > README.md << 'EOL'
# Tesseract OCR Wrapper

A flexible Python wrapper for Tesseract OCR with support for:
- Multiple input formats (images, PDFs, directories)
- Custom configurations
- Intelligent processing

## Quick Start

1. Open this repository in GitHub Codespaces
2. Try the example notebook: `examples.ipynb`
3. Import the wrapper in your code:
   ```python
   from tesseract_ocr import TesseractOCR, TesseractConfig
   
   ocr = TesseractOCR()
   text = ocr.process("your_image.png", return_text=True)
   print(text)
   ```

## Features

- Process images directly
- Convert PDFs to images for OCR processing
- Batch process entire directories
- Configure OCR parameters (language, PSM, OEM, etc.)
- Return extracted text or save to files

## Project Structure

- `tesseract_ocr.py` - Main wrapper implementation
- `examples.ipynb` - Jupyter notebook with examples
- `samples/` - Sample images for testing
- `output/` - Default output directory

## Requirements

All requirements are automatically installed in the Codespace:
- Python 3.10+
- Tesseract OCR
- pdf2image
- pytesseract

## License

MIT
EOL

# Create an __init__.py file to make the module importable
cat > __init__.py << 'EOL'
from .tesseract_ocr import TesseractOCR, TesseractConfig
EOL

# Copy TesseractOCR.py to tesseract_ocr.py for consistency (if it exists)
if [ -f "TesseractOCR.py" ]; then
    cp TesseractOCR.py tesseract_ocr.py
fi

echo "Setup complete! You can now start using the OCR wrapper."