# ---------------------------------------------------------
# 🐍 Dockerfile for Claims Processor (spaCy Fix + Stable)
# ---------------------------------------------------------
FROM python:3.10-slim AS base

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for OCR and PDF handling
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install spaCy model explicitly (works in all environments)
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz

# Copy project files
COPY src/ ./src/
COPY configs/ ./configs/
COPY data/ ./data/
COPY logs/ ./logs/
COPY db/ ./db/
COPY .env .env

# Ensure folders exist
RUN mkdir -p data/raw data/processed logs db

# Default command
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["--input", "data/test/mock_claim.txt"]
