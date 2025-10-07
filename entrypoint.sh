#!/bin/bash
set -e  # Exit immediately on error

echo "🚀 Starting Intelligent Claims Processor..."

# Check if .env file exists
if [ -f ".env" ]; then
  echo "📦 Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️  No .env file found! Using default environment variables."
fi

# Print current environment (for debugging)
echo "🔧 Environment Summary:"
echo " - DATABASE_URL: ${DATABASE_URL}"
echo " - LOG_LEVEL: ${LOG_LEVEL}"
echo " - DATA_DIR: ${DATA_DIR}"
echo " - CONFIDENCE_THRESHOLD: ${CONFIDENCE_THRESHOLD}"

# Run main pipeline
echo "🧠 Running Claims Processing Pipeline..."
python src/main.py "$@"

# After successful run
echo "✅ Claims processing completed successfully."
