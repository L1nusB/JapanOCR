from japanese_ocr import TesseractOCR, TesseractConfig

def main():
    # Initialize OCR with Japanese language support
    config = TesseractConfig(lang="jpn")
    ocr = TesseractOCR(default_config=config)
    
    # Basic image processing
    image_path = "path/to/japanese_image.png"  # Replace with actual path
    
    # Process a single image
    try:
        text = ocr.process_file(image_path, return_text=True)
        print("=== Extracted Text ===")
        print(text)
        print("=====================")
    except Exception as e:
        print(f"Error processing image: {e}")
    
    # Processing with custom configuration
    custom_config = TesseractConfig(
        lang="jpn+eng",   # Japanese with English fallback
        psm=6,            # Assume a single uniform block of text
        oem=3,            # Default OCR engine mode
        dpi=400           # Higher DPI for better quality
    )
    
    try:
        text = ocr.process_file(
            image_path,
            config=custom_config,
            output_dir="output",  # Save output to this directory
            return_text=True
        )
        print("\n=== Text with Custom Config ===")
        print(text)
        print("==============================")
    except Exception as e:
        print(f"Error processing with custom config: {e}")
    
    # PDF processing example (requires pdf2image and PyPDF2)
    pdf_path = "path/to/document.pdf"  # Replace with actual path
    
    try:
        pdf_text = ocr.process_file(
            pdf_path,
            output_dir="output",
            combine_output=True,  # Combine all pages into one output
            return_text=True
        )
        print("\n=== PDF Extracted Text (First 500 chars) ===")
        print(f"{pdf_text[:500]}...")
        print("==========================================")
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    main()