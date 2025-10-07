import os
import json
import yaml
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Paths (relative to project root)
CONFIG_DIR = "../configs"
DATA_DIR = "../data"
LOGS_DIR = "../logs"
DB_DIR = "../db"

# Load schema
with open(os.path.join(CONFIG_DIR, "schema.json"), "r") as f:
    CLAIM_SCHEMA = json.load(f)

# Load prompts
with open(os.path.join(CONFIG_DIR, "prompts.yaml"), "r") as f:
    PROMPTS = yaml.safe_load(f)

# Load rules
with open(os.path.join(CONFIG_DIR, "rules.yaml"), "r") as f:
    RULES = yaml.safe_load(f)

# Environment vars
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", RULES.get("confidence_threshold", 0.8)))
MAX_CLAIM_AMOUNT = float(os.getenv("MAX_CLAIM_AMOUNT", RULES.get("max_amount", 100000)))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR}/claims.db")

# Logging setup (imported from utils)
from .utils.logging import setup_logging
setup_logging()