import os
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Define key directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))

# Initialize and load CLAIM_SCHEMA from configs/schema.json if available
CLAIM_SCHEMA = {}
schema_path = os.path.join(CONFIG_DIR, "schema.json")
try:
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            CLAIM_SCHEMA = json.load(f)
    else:
        CLAIM_SCHEMA = {}
except Exception:
    CLAIM_SCHEMA = {}

# Load prompts if present
PROMPTS_PATH = os.path.join(CONFIG_DIR, "prompts.yaml")
if os.path.exists(PROMPTS_PATH):
    with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
        PROMPTS = f.read()
else:
    PROMPTS = "Summarize and normalize extracted insurance claim data."

# Environment-backed config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db/claims.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
try:
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.8))
except (TypeError, ValueError):
    CONFIDENCE_THRESHOLD = 0.8

__all__ = [
    "BASE_DIR",
    "CONFIG_DIR",
    "DATA_DIR",
    "CLAIM_SCHEMA",
    "PROMPTS",
    "OPENAI_API_KEY",
    "DATABASE_URL",
    "LOG_LEVEL",
    "CONFIDENCE_THRESHOLD",
]
