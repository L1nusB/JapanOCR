import os
import tempfile
import logging
from typing import Dict, List, Optional, Union, Set, Tuple, Any
from pathlib import Path
import subprocess
from dataclasses import dataclass, field, fields

# Optional imports (only needed if installed)
try:
    import pdf2image
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Create a logger for this module without modifying global settings
logger = logging.getLogger("TesseractOCR")
# Set up handler for this logger only
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
# Prevent propagation to avoid duplicate logs
logger.propagate = False


@dataclass
class TesseractConfig:
    """Configuration options for Tesseract OCR."""
    lang: str = "eng"
    dpi: int = 300
    psm: int = 3
    oem: int = 3
    config_string: str = ""
    output_pdf: bool = False
    tessdata_dir: Optional[str] = None
    
    def to_cmd_args(self) -> List[str]:
        """Convert configuration to command line arguments."""
        args = []
        
        # Language
        args.extend(["-l", self.lang])
        
        # Page segmentation mode
        args.extend(["--psm", str(self.psm)])
        
        # OCR engine mode
        args.extend(["--oem", str(self.oem)])
        
        # Custom config string
        if self.config_string:
            for param in self.config_string.split():
                args.append(param)
        
        # Output PDF
        if self.output_pdf:
            args.append("pdf")
        
        # Tessdata directory
        if self.tessdata_dir:
            args.extend(["--tessdata-dir", self.tessdata_dir])
            
        return args


class TesseractOCR:
    """
    A comprehensive wrapper for Tesseract OCR that handles various input formats
    and offers extensive configuration options.
    
    Features:
    - Support for image files (png, jpg, tiff, etc.)
    - Support for PDF files (requires pdf2image package)
    - Batch processing from directories or file lists
    - Flexible configuration options
    """
    
    SUPPORTED_IMAGE_FORMATS: Set[str] = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"}
    
    def __init__(
        self,
        tesseract_cmd: str = "tesseract",
        default_config: Optional[TesseractConfig] = None,
        default_output_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the TesseractOCR wrapper.
        
        Args:
            tesseract_cmd: Path to the Tesseract executable
            default_config: Default configuration to use
            default_output_dir: Default directory to save output files
        """
        self.tesseract_cmd = tesseract_cmd
        self.default_config = default_config or TesseractConfig()
        
        if default_output_dir:
            self.default_output_dir = Path(default_output_dir)
            os.makedirs(self.default_output_dir, exist_ok=True)
        else:
            self.default_output_dir = None
        
        # Verify Tesseract is installed
        self._verify_tesseract()
        
        # Check PDF support
        if not PDF_SUPPORT:
            logger.warning(
                "pdf2image package not found. PDF support is disabled. "
                "Install with: pip install pdf2image"
            )
    
    def _verify_tesseract(self) -> None:
        """Verify that Tesseract is installed and accessible."""
        try:
            result = subprocess.run(
                [self.tesseract_cmd, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"Tesseract check failed: {result.stderr}")
            logger.info(f"Using Tesseract: {result.stdout.splitlines()[0]}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Tesseract executable not found at '{self.tesseract_cmd}'. "
                "Make sure Tesseract is installed and in your PATH."
            )
        
    def process(
        self,
        input_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        config: Optional[TesseractConfig] = None,
        return_text: bool = False,
        combine_output: bool = False,
        **kwargs
    ) -> Union[Optional[str], Dict[str, Optional[str]]]:
        """
        Process input dynamically based on its type.
        
        This function intelligently determines what type of input was provided
        and calls the appropriate processing method.
        
        Args:
            input_path: Path to input (file, directory, or file list)
            output_dir: Directory to save output files
            config: Tesseract configuration
            return_text: Whether to return extracted text
            combine_output: For multi-page documents, whether to create a combined output file
            **kwargs: Additional arguments for specific processing methods
                      (recursive, file_extensions, etc.)
        
        Returns:
            - For single files: The extracted text (if return_text=True) or None
            - For directories/file lists: Dict mapping filenames to extracted text
            
        Raises:
            ValueError: If the input type cannot be determined
        """
        path = Path(input_path)
        
        # Check if input is a file list
        if path.is_file() and path.suffix.lower() == '.txt':
            # Check first line to see if it contains file paths
            try:
                with open(path, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line and Path(first_line).exists():
                        logger.info(f"Processing as file list: {path}")
                        return self.process_file_list(path, output_dir, config, return_text, combine_output)
            except Exception as e:
                logger.debug(f"Failed to process as file list: {e}")
        
        # Check if input is a directory
        if path.is_dir():
            logger.info(f"Processing as directory: {path}")
            return self.process_directory(
                path, 
                output_dir, 
                config, 
                recursive=kwargs.get('recursive', False),
                file_extensions=kwargs.get('file_extensions'),
                return_text=return_text,
                combine_output=combine_output
            )
        
        # Process as a single file
        if path.is_file():
            extension = path.suffix.lower()
            if extension in self.SUPPORTED_IMAGE_FORMATS or extension == '.pdf':
                logger.info(f"Processing as single file: {path}")
                return self.process_file(
                    path, 
                    output_dir, 
                    config, 
                    output_filename_base=kwargs.get('output_filename_base'),
                    return_text=return_text,
                    combine_output=combine_output
                )
        
        raise ValueError(
            f"Could not determine how to process: {input_path}. "
            "Input must be an image file, PDF, directory, or a text file containing file paths."
        )
    
    def process_file(
        self,
        input_file: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        config: Optional[TesseractConfig] = None,
        output_filename_base: Optional[str] = None,
        return_text: bool = False,
        combine_output: bool = False
    ) -> Optional[str]:
        """
        Process a single file with Tesseract OCR.
        
        Args:
            input_file: Path to the input file (image or PDF)
            output_dir: Directory to save the output files
            config: Tesseract configuration options
            output_filename_base: Base name for output files
            return_text: Whether to return the extracted text
            combine_output: For multi-page documents, whether to create a combined output file
            
        Returns:
            The extracted text if return_text is True, otherwise None
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Determine output directory
        out_dir = Path(output_dir) if output_dir else self.default_output_dir
        
        # Use provided config or default
        cfg = config or self.default_config
        
        # Handle different file types
        if input_path.suffix.lower() == ".pdf":
            return self._process_pdf(
                input_path, 
                out_dir, 
                cfg, 
                output_filename_base,
                return_text,
                combine_output
            )
        elif input_path.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS:
            return self._process_image(
                input_path, 
                out_dir, 
                cfg, 
                output_filename_base,
                return_text
            )
        else:
            raise ValueError(
                f"Unsupported file format: {input_path.suffix}. "
                f"Supported formats: {self.SUPPORTED_IMAGE_FORMATS} and .pdf"
            )
    
    def _process_image(
        self,
        image_path: Path,
        output_dir: Optional[Path],
        config: TesseractConfig,
        output_filename_base: Optional[str] = None,
        return_text: bool = False
    ) -> Optional[str]:
        """Process a single image file with Tesseract."""
        # Determine output base filename
        if output_filename_base:
            out_base = output_filename_base
        else:
            out_base = image_path.stem
            
        # Set up output path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            out_path = output_dir / out_base
        else:
            # Create temporary output if no directory specified
            tmp_dir = tempfile.mkdtemp()
            out_path = Path(tmp_dir) / out_base
        
        # Build command
        cmd = [self.tesseract_cmd, str(image_path), str(out_path)]
        
        # When return_text is True, we always want txt output regardless of PDF settings
        output_formats = []
        if config.output_pdf:
            output_formats.append("pdf")
        
        # Always add txt to cmd when return_text is True
        # If txt is not specified, tesseract defaults to txt output anyway
        if return_text and config.output_pdf:
            output_formats.append("txt")
        
        # Add basic config args (lang, psm, oem, etc.)
        cmd.extend(config.to_cmd_args())
        
        # If we have output_formats, replace "pdf" from to_cmd_args with our full list
        if output_formats:
            # Remove "pdf" if it was added by to_cmd_args
            if "pdf" in cmd:
                cmd.remove("pdf")
            # Add all formats
            cmd.extend(output_formats)
        
        logger.info(f"Running Tesseract on {image_path}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        # Run Tesseract
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Tesseract failed: {result.stderr}")
        
        # Handle text return
        text_output = None
        if return_text:
            txt_output = Path(f"{out_path}.txt")
            if txt_output.exists():
                with open(txt_output, 'r', encoding='utf-8') as f:
                    text_output = f.read()
            else:
                # If file doesn't exist but we need text, run again with txt output only
                logger.warning(f"Text output not found at {txt_output}, running Tesseract again for text output")
                txt_cmd = [self.tesseract_cmd, str(image_path), str(out_path)]
                # Only add language flag for simplicity
                txt_cmd.extend(["-l", config.lang])
                subprocess.run(txt_cmd, check=True)
                
                # Try reading the text file again
                if txt_output.exists():
                    with open(txt_output, 'r', encoding='utf-8') as f:
                        text_output = f.read()
                else:
                    logger.error(f"Failed to create text output file: {txt_output}")
            
            # Clean up temporary directory if we created one and don't need to keep files
            if not output_dir and os.path.exists(os.path.dirname(out_path)):
                try:
                    # Clean up temporary txt file if it exists and we only needed it for return_text
                    if txt_output.exists() and not output_dir:
                        txt_output.unlink()
                    
                    # If the directory still exists (e.g., we're in a temporary directory)
                    tmp_path = os.path.dirname(out_path)
                    if os.path.exists(tmp_path) and tmp_path.startswith(tempfile.gettempdir()):
                        import shutil
                        shutil.rmtree(tmp_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary files: {e}")
                
        return text_output
    
    def _process_pdf(
        self,
        pdf_path: Path,
        output_dir: Optional[Path],
        config: TesseractConfig,
        output_filename_base: Optional[str] = None,
        return_text: bool = False,
        combine_output: bool = False
    ) -> Optional[str]:
        """Process a PDF file by first converting it to images."""
        if not PDF_SUPPORT:
            raise RuntimeError(
                "PDF support requires the pdf2image package. "
                "Install with: pip install pdf2image"
            )
        
        # Convert PDF to images
        logger.info(f"Converting PDF to images: {pdf_path}")
        images = pdf2image.convert_from_path(
            pdf_path, 
            dpi=config.dpi
        )
        
        # Skip processing if no pages found
        if not images:
            logger.warning(f"No pages found in PDF: {pdf_path}")
            return None
        
        # Determine output paths and create directories
        base_name = output_filename_base or pdf_path.stem
        
        # Path for individual page files
        pages_dir = None
        if output_dir and combine_output:
            pages_dir = output_dir / "pages" / base_name
            os.makedirs(pages_dir, exist_ok=True)
        
        # Create temporary directory for images
        with tempfile.TemporaryDirectory() as tmp_dir:
            image_paths = []
            
            # Save images to temporary directory
            for i, image in enumerate(images):
                img_path = Path(tmp_dir) / f"page_{i+1}.png"
                image.save(str(img_path), "PNG")
                image_paths.append(img_path)
            
            # Process each image
            all_text = []
            output_files = {"pdf": [], "txt": []}
            
            for i, img_path in enumerate(image_paths):
                page_number = i + 1
                if output_filename_base:
                    page_filename = f"{output_filename_base}_page_{page_number}"
                else:
                    page_filename = f"{pdf_path.stem}_page_{page_number}"
                
                # Use the pages directory if specified, otherwise use the main output directory
                current_output_dir = pages_dir if pages_dir else output_dir
                
                text = self._process_image(
                    img_path,
                    current_output_dir,
                    config,
                    page_filename,
                    return_text or combine_output  # We need the text if combine_output is True
                )
                
                if text:
                    all_text.append(text)
                    
                    # Keep track of output files for combining later
                    if combine_output and current_output_dir:
                        # Note the output files that were created
                        if config.output_pdf:
                            pdf_file = current_output_dir / f"{page_filename}.pdf"
                            if pdf_file.exists():
                                output_files["pdf"].append(pdf_file)
                        
                        txt_file = current_output_dir / f"{page_filename}.txt"
                        if txt_file.exists():
                            output_files["txt"].append(txt_file)
            
            # Create combined output files if requested and output_dir is provided
            if combine_output and output_dir and all_text:
                # Create combined text file
                combined_txt_path = output_dir / f"{base_name}.txt"
                with open(combined_txt_path, 'w', encoding='utf-8') as f:
                    f.write("\n\n".join(all_text))
                logger.info(f"Created combined text file: {combined_txt_path}")
                
                # If PDF output was requested, try to combine the PDFs
                if config.output_pdf and output_files["pdf"]:
                    try:
                        # Check if PyPDF2 is available
                        import importlib.util
                        if importlib.util.find_spec("PyPDF2"):
                            import PyPDF2
                            combined_pdf_path = output_dir / f"{base_name}.pdf"
                            
                            merger = PyPDF2.PdfMerger()
                            for pdf_file in output_files["pdf"]:
                                merger.append(str(pdf_file))
                            
                            with open(combined_pdf_path, 'wb') as f:
                                merger.write(f)
                                
                            logger.info(f"Created combined PDF file: {combined_pdf_path}")
                        else:
                            logger.warning("PyPDF2 package not found. Cannot create combined PDF.")
                            logger.warning("Install with: pip install PyPDF2")
                    except Exception as e:
                        logger.error(f"Failed to create combined PDF: {e}")
            
            # Combine text from all pages
            if return_text:
                return "\n\n".join(all_text)
            
        return None
    
    def process_directory(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        config: Optional[TesseractConfig] = None,
        recursive: bool = False,
        file_extensions: Optional[Set[str]] = None,
        return_text: bool = False,
        combine_output: bool = False
    ) -> Dict[str, Optional[str]]:
        """
        Process all supported files in a directory.
        
        Args:
            input_dir: Directory containing files to process
            output_dir: Directory to save output files
            config: Tesseract configuration
            recursive: Whether to search subdirectories
            file_extensions: Set of file extensions to process
            return_text: Whether to return extracted text
            combine_output: For multi-page documents, whether to create a combined output file
            
        Returns:
            Dictionary mapping filenames to extracted text (if return_text is True)
        """
        input_path = Path(input_dir)
        
        if not input_path.is_dir():
            raise ValueError(f"Input path is not a directory: {input_path}")
        
        # Determine file extensions to process
        extensions = file_extensions or self.SUPPORTED_IMAGE_FORMATS.union({".pdf"})
        
        # Collect files
        files_to_process = []
        
        if recursive:
            for root, _, files in os.walk(input_path):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in extensions:
                        files_to_process.append(file_path)
        else:
            files_to_process = [
                f for f in input_path.iterdir()
                if f.is_file() and f.suffix.lower() in extensions
            ]
        
        # Process files
        results = {}
        for file_path in files_to_process:
            try:
                text = self.process_file(
                    file_path,
                    output_dir,
                    config,
                    return_text=return_text,
                    combine_output=combine_output
                )
                
                if return_text:
                    results[str(file_path)] = text
                
                logger.info(f"Processed: {file_path}")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results[str(file_path)] = None
        
        return results
    
    def process_file_list(
        self,
        file_list_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        config: Optional[TesseractConfig] = None,
        return_text: bool = False,
        combine_output: bool = False
    ) -> Dict[str, Optional[str]]:
        """
        Process files listed in a text file.
        
        Args:
            file_list_path: Path to a text file containing file paths (one per line)
            output_dir: Directory to save output files
            config: Tesseract configuration
            return_text: Whether to return extracted text
            combine_output: For multi-page documents, whether to create a combined output file
            
        Returns:
            Dictionary mapping filenames to extracted text (if return_text is True)
        """
        with open(file_list_path, 'r', encoding='utf-8') as f:
            file_paths = [line.strip() for line in f if line.strip()]
        
        results = {}
        for file_path in file_paths:
            try:
                text = self.process_file(
                    file_path,
                    output_dir,
                    config,
                    return_text=return_text,
                    combine_output=combine_output
                )
                
                if return_text:
                    results[file_path] = text
                
                logger.info(f"Processed: {file_path}")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results[file_path] = None
        
        return results
    
    @staticmethod
    def config_from_string(config_string: str) -> TesseractConfig:
        """
        Create a TesseractConfig object from a command-line style string.
        
        Args:
            config_string: String with Tesseract options in command-line format
                           Example: "-l eng+deu --psm 3 --oem 1"
                           
        Returns:
            TesseractConfig object with parsed options
        """
        config = TesseractConfig()
        parts = config_string.split()
        
        i = 0
        while i < len(parts):
            if parts[i] == "-l" and i + 1 < len(parts):
                config.lang = parts[i + 1]
                i += 2
            elif parts[i] == "--psm" and i + 1 < len(parts):
                config.psm = int(parts[i + 1])
                i += 2
            elif parts[i] == "--oem" and i + 1 < len(parts):
                config.oem = int(parts[i + 1])
                i += 2
            elif parts[i] == "--tessdata-dir" and i + 1 < len(parts):
                config.tessdata_dir = parts[i + 1]
                i += 2
            elif parts[i] == "pdf":
                config.output_pdf = True
                i += 1
            else:
                # Add to custom config string
                if config.config_string:
                    config.config_string += " "
                config.config_string += parts[i]
                i += 1
                
        return config
    
    @staticmethod
    def config_from_kwargs(**kwargs) -> TesseractConfig:
        """
        Create a TesseractConfig object from keyword arguments.
        
        Args:
            **kwargs: Keyword arguments corresponding to TesseractConfig fields
            
        Returns:
            TesseractConfig object with specified options
        """
        valid_fields = {field.name for field in fields(TesseractConfig)}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return TesseractConfig(**filtered_kwargs)