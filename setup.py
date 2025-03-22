from setuptools import setup, find_packages

setup(
    name="japanese-ocr",
    version="0.1.0",
    author="Linus",
    description="A flexible Python wrapper for Tesseract OCR with Japanese language support",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/L1nusB/japanese-ocr",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytesseract>=0.3.8",
        "pillow>=8.0.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "pdf": ["pdf2image>=1.16.0", "PyPDF2>=2.0.0"],
        "dev": ["pytest>=6.0.0", "black", "flake8"],
    },
)