# Multi-stage build for efficiency (optional; single-stage works too)
FROM python:3.10-slim AS builder

# Install system dependencies for OCR and PDF handling
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Final stage: Copy app code
FROM python:3.10-slim AS runtime

# Install runtime system deps (minimal)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy project files
COPY src/ ./src/
COPY configs/ ./configs/
COPY data/ ./data/  # Includes samples; in prod, mount as volume
COPY requirements.txt .  # Already installed, but for reference

# Copy entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose port if adding web UI later (e.g., Streamlit on 8501)
# EXPOSE 8501

# Default command: Run the main script with --help
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "src/main.py", "--help"]