FROM continuumio/miniconda3:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (including Tesseract)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    software-properties-common \
    git \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install additional language packs
RUN apt-get update && apt-get install -y \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install mamba for faster dependency resolution
RUN conda install -y -c conda-forge mamba

# Install all conda packages as root
RUN mamba install -y -c conda-forge \
    python=3.10 \
    pip \
    pytesseract \
    pdf2image \
    pillow \
    numpy \
    opencv \
    pandas \
    poppler \
    jupyter \
    ipykernel \
    ipywidgets \
    matplotlib \
    black \
    pylint \
    mypy \
    && mamba clean -afy

# Install pip packages
RUN pip install pytest pytest-cov

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Fix permissions for the conda directories
RUN mkdir -p /opt/conda/pkgs \
    && chown -R $USERNAME:$USERNAME /opt/conda/pkgs \
    && chmod -R 775 /opt/conda

# Set working directory
WORKDIR /workspace
USER $USERNAME