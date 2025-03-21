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