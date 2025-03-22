"""
Japanese OCR - A flexible Python wrapper for Tesseract OCR with Japanese language support.
"""

from .tesseract_ocr import TesseractOCR, TesseractConfig

__version__ = "0.1.0"
__all__ = ["TesseractOCR", "TesseractConfig"]