from src.japanese_ocr.tesseract_ocr import TesseractOCR, TesseractConfig

# Basic usage
ocr = TesseractOCR()

config = TesseractConfig(
    lang="jpn+eng",
    psm=6,  # Uniform block of text
    # psm=3,  # Fully automatic page segmentation, but no OSD. (Default)
    oem=3,  # Default OCR Engine Mode (based on what is available)
    output_pdf=True,
)

# Process a PDF file with combined output
text = ocr.process_file(
    input_file="input/Lesson34.pdf",
    output_dir="output",
    config=config,
    return_text=True,
    combine_output=True  # This will create a combined output file
)
print("Text: ", text)

# # Process a directory with combined output for multi-page documents
# results = ocr.process_directory(
#     "input",
#     "output",
#     config=config,
#     return_text=True,
#     combine_output=True
# )

# # Other usage examples...
# # Process a single image file
# text = ocr.process_file("image.png", return_text=True)
# print(text)

# # Process a PDF file
# ocr.process_file("document.pdf", output_dir="output")

# # Process with custom configuration
# config = TesseractConfig(
#     lang="eng+jpn",
#     psm=6,
#     oem=1,
#     output_pdf=True
# )

# ocr.process_file("document.jpg", config=config)

# # Alternative way to create config from string
# config = TesseractOCR.config_from_string("-l eng+jpn --psm 6 --oem 1 pdf")

# # Process all files in a directory
# results = ocr.process_directory(
#     "input_folder",
#     "output_folder",
#     recursive=True,
#     return_text=True
# )

# # Use the new dynamic process function
# # It will automatically determine the input type
# result = ocr.process(
#     "input/document.pdf",  # Could be a file, directory, or file list
#     "output",
#     return_text=True,
#     combine_output=True
# )

# # Create config with filtered kwargs
# config = TesseractOCR.config_from_kwargs(
#     lang="eng+fra",
#     psm=6,
#     oem=1,
#     unknown_param=123  # This will be silently ignored
# )
