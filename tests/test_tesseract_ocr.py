import pytest
from pathlib import Path
import tempfile
import os
from japanese_ocr import TesseractOCR, TesseractConfig

# Skip tests if Tesseract is not installed
pytestmark = pytest.mark.skipif(
    os.system("tesseract --version") != 0,
    reason="Tesseract OCR not installed"
)

class TestTesseractConfig:
    """Test TesseractConfig functionality."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = TesseractConfig()
        assert config.lang == "eng"
        assert config.psm == 3
        assert config.oem == 3
        assert config.output_pdf is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = TesseractConfig(
            lang="jpn",
            psm=6,
            oem=1,
            output_pdf=True
        )
        assert config.lang == "jpn"
        assert config.psm == 6
        assert config.oem == 1
        assert config.output_pdf is True
    
    def test_to_cmd_args(self):
        """Test command-line arguments generation."""
        config = TesseractConfig(lang="jpn+eng", psm=6)
        args = config.to_cmd_args()
        assert "-l" in args
        assert "jpn+eng" in args
        assert "--psm" in args
        assert "6" in args

class TestTesseractOCR:
    """Test TesseractOCR functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.ocr = TesseractOCR()
    
    def test_initialization(self):
        """Test proper initialization."""
        assert isinstance(self.ocr.default_config, TesseractConfig)
        assert self.ocr.default_output_dir is None
    
    def test_config_from_string(self):
        """Test creating config from string."""
        config_str = "-l jpn+eng --psm 6 --oem 1"
        config = TesseractOCR.config_from_string(config_str)
        assert config.lang == "jpn+eng"
        assert config.psm == 6
        assert config.oem == 1
    
    def test_config_from_kwargs(self):
        """Test creating config from kwargs."""
        config = TesseractOCR.config_from_kwargs(
            lang="jpn", 
            psm=7,
            oem=2,
            output_pdf=True
        )
        assert config.lang == "jpn"
        assert config.psm == 7
        assert config.oem == 2
        assert config.output_pdf is True

# Add more tests that require actual images when needed