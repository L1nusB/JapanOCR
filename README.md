# Japanese OCR

A flexible Python wrapper for Tesseract OCR with Japanese language support.

## Features

- Simple API for OCR processing of Japanese text
- Support for various image formats (PNG, JPG, TIFF, etc.)
- PDF processing capabilities (with optional dependencies)
- Batch processing of files and directories
- Configurable Tesseract parameters

## Installation

### Basic Installation

```bash
pip install japanese-ocr
```

### With PDF Support

```bash
pip install japanese-ocr[pdf]
```

## Requirements

- Python 3.8+
- Tesseract OCR must be installed on your system
- Japanese language data for Tesseract

## Basic Usage

```python
from japanese_ocr import TesseractOCR, TesseractConfig

# Initialize OCR with Japanese language support
config = TesseractConfig(lang="jpn")
ocr = TesseractOCR(default_config=config)

# Process a single image
text = ocr.process_file("path/to/japanese_image.png", return_text=True)
print(text)

# Process a PDF with multiple pages
pdf_text = ocr.process_file(
    "path/to/document.pdf",
    output_dir="output",
    combine_output=True,
    return_text=True
)
print(pdf_text)
```

## Advanced Configuration

```python
# Custom configuration for vertical Japanese text
config = TesseractConfig(
    lang="jpn+jpn_vert",  # Japanese + Vertical Japanese
    psm=5,                # Assume vertical single uniform text block
    oem=1,                # LSTM OCR Engine only
    config_string="--tessdata-dir /path/to/custom/tessdata"
)

# Process with custom configuration
ocr = TesseractOCR()
text = ocr.process_file("vertical_text.png", config=config, return_text=True)
```

## Processing Directories

```python
# Process all images in a directory
results = ocr.process_directory(
    "path/to/images/",
    output_dir="output/",
    recursive=True,
    return_text=True
)

# Print results for each file
for file_path, text in results.items():
    print(f"File: {file_path}")
    print(f"Text: {text[:100]}...")  # Print first 100 chars
    print("-" * 50)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.