"""
src/config.py

Central configuration loader for the claims_processor project.

This module:
- Loads environment variables from a .env file (if present)
- Determines project directories (BASE_DIR, CONFIG_DIR, DATA_DIR)
- Loads schema.json into CLAIM_SCHEMA (safe fallback to empty dict)
- Loads prompts.yaml and rules.yaml into PROMPTS and RULES (safe fallbacks)
- Exposes runtime constants (OPENAI_API_KEY, DATABASE_URL, LOG_LEVEL, etc.)

Design choices:
- Avoids raising on missing optional files so imports remain safe during development.
- Prints clear diagnostics to the console to aid local debugging.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

# Try to import yaml (pyyaml). If unavailable, we'll fallback gracefully.
try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # type: ignore

# Load .env early
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # If python-dotenv is not available, environment variables must be set externally.
    pass

# -------------------------
# Directories & paths
# -------------------------
# BASE_DIR is the project root (two levels up from this file: src/)
BASE_DIR = Path(__file__).resolve().parents[1]  # project root (..)
CONFIG_DIR = BASE_DIR / "configs"
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))

# Ensure DATA_DIR exists when possible (safe to create)
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # If we cannot create (permissions), that's ok — caller will handle
    pass

# -------------------------
# Load JSON schema (CLAIM_SCHEMA)
# -------------------------
CLAIM_SCHEMA: Dict[str, Any] = {}
_schema_path = CONFIG_DIR / "schema.json"

if _schema_path.exists():
    try:
        with _schema_path.open("r", encoding="utf-8") as f:
            CLAIM_SCHEMA = json.load(f)
        print(f"✅ [CONFIG] Loaded claim schema from: {_schema_path} ({len(CLAIM_SCHEMA)} fields).")
    except json.JSONDecodeError as e:
        print(f"❌ [CONFIG] Invalid JSON in schema.json: {_schema_path} — {e}")
        CLAIM_SCHEMA = {}
    except Exception as e:
        print(f"❌ [CONFIG] Unexpected error loading schema.json: {_schema_path} — {e}")
        CLAIM_SCHEMA = {}
else:
    print(f"⚠️ [CONFIG] schema.json not found at: {_schema_path}. Continuing with empty CLAIM_SCHEMA.")

# -------------------------
# Load prompts.yaml (text prompts for GenAI) — optional
# -------------------------
PROMPTS: str = ""
_prompts_path = CONFIG_DIR / "prompts.yaml"
if _prompts_path.exists():
    try:
        if yaml:
            with _prompts_path.open("r", encoding="utf-8") as f:
                # If YAML file contains mapping, keep raw text; else read as string
                loaded = yaml.safe_load(f)
                # If the YAML is a mapping with a "default" key, use it; otherwise, stringify
                if isinstance(loaded, dict) and "default" in loaded:
                    PROMPTS = str(loaded["default"])
                else:
                    # Keep raw file text for maximum flexibility
                    PROMPTS = _prompts_path.read_text(encoding="utf-8")
        else:
            # No yaml lib: read as plain text
            PROMPTS = _prompts_path.read_text(encoding="utf-8")
        print(f"✅ [CONFIG] Loaded prompts from: {_prompts_path}")
    except Exception as e:
        print(f"⚠️ [CONFIG] Failed to load prompts.yaml: {_prompts_path} — {e}")
        PROMPTS = ""
else:
    PROMPTS = ""  # empty default; callers should handle empty prompts
    print(f"ℹ️ [CONFIG] No prompts.yaml found at: {_prompts_path}. Using empty PROMPTS.")

# -------------------------
# Load rules.yaml (business rules) — optional
# -------------------------
RULES: Dict[str, Any] = {}
_rules_path = CONFIG_DIR / "rules.yaml"
if _rules_path.exists():
    try:
        if yaml:
            with _rules_path.open("r", encoding="utf-8") as f:
                RULES = yaml.safe_load(f) or {}
        else:
            # If no yaml available, try to parse as JSON as a fallback
            try:
                with _rules_path.open("r", encoding="utf-8") as f:
                    RULES = json.load(f)
            except Exception:
                RULES = {}
        print(f"✅ [CONFIG] Loaded rules from: {_rules_path}")
    except Exception as e:
        print(f"⚠️ [CONFIG] Failed to load rules.yaml: {_rules_path} — {e}")
        RULES = {}
else:
    RULES = {}
    print(f"ℹ️ [CONFIG] No rules.yaml found at: {_rules_path}. Using empty RULES.")

# -------------------------
# Environment-driven values & defaults
# -------------------------
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ [CONFIG] OPENAI_API_KEY not set. Add it to your .env or environment variables if using GenAI features.")

DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{str(BASE_DIR / 'db' / 'claims.db')}")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
try:
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.8"))
except ValueError:
    print("⚠️ [CONFIG] CONFIDENCE_THRESHOLD invalid in environment; defaulting to 0.8")
    CONFIDENCE_THRESHOLD = 0.8

# Business limits (safe defaults; override via .env)
try:
    MAX_CLAIM_AMOUNT: float = float(os.getenv("MAX_CLAIM_AMOUNT", "100000.0"))
except ValueError:
    print("⚠️ [CONFIG] MAX_CLAIM_AMOUNT invalid in .env; using 100000.0")
    MAX_CLAIM_AMOUNT = 100000.0

try:
    MIN_CLAIM_AMOUNT: float = float(os.getenv("MIN_CLAIM_AMOUNT", "0.0"))
except ValueError:
    MIN_CLAIM_AMOUNT = 0.0

# -------------------------
# Helper utilities
# -------------------------
def get_schema_field(field_name: str, default: Any = None) -> Any:
    """
    Return the value for a field in the loaded CLAIM_SCHEMA, or default if not present.
    This is a convenience utility used by validators and other components.
    """
    return CLAIM_SCHEMA.get(field_name, default)


def is_schema_loaded() -> bool:
    """Return True if CLAIM_SCHEMA appears to contain fields."""
    return bool(CLAIM_SCHEMA)


# -------------------------
# Debug / info dump when run directly
# -------------------------
if __name__ == "__main__":
    print("---- CONFIG DIAGNOSTIC ----")
    print("BASE_DIR:", BASE_DIR)
    print("CONFIG_DIR:", CONFIG_DIR)
    print("DATA_DIR:", DATA_DIR)
    print("CLAIM_SCHEMA keys:", list(CLAIM_SCHEMA.keys())[:20])
    print("PROMPTS present:", bool(PROMPTS))
    print("RULES present:", bool(RULES))
    print("OPENAI_API_KEY present:", bool(OPENAI_API_KEY))
    print("DATABASE_URL:", DATABASE_URL)
    print("LOG_LEVEL:", LOG_LEVEL)
    print("CONFIDENCE_THRESHOLD:", CONFIDENCE_THRESHOLD)
    print("MAX_CLAIM_AMOUNT:", MAX_CLAIM_AMOUNT)
    print("MIN_CLAIM_AMOUNT:", MIN_CLAIM_AMOUNT)
    print("---------------------------")
