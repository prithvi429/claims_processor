"""
src/processing/genai.py
--------------------------------
Handles Generative AI–based summarization and normalization.

Key features:
- Uses OpenAI API with a shared httpx.Client to avoid proxy issues
- Skips API calls gracefully if key is missing or quota exceeded
- Handles both new (responses.create) and old (chat.completions.create) client methods
- Logs clearly at every stage
"""

import atexit
import json
import httpx
from typing import Dict, Any

from openai import OpenAI
from src.config import OPENAI_API_KEY, PROMPTS
from src.processing.nlp import extract_entities
from src.utils.logging import logger

# ----------------------------------------------------------------------
# Setup shared HTTP client for OpenAI to avoid "proxies" argument issues
# ----------------------------------------------------------------------
_httpx_client = httpx.Client()
atexit.register(lambda: _httpx_client.close())

# Initialize OpenAI client safely
try:
    client = OpenAI(api_key=OPENAI_API_KEY, http_client=_httpx_client)
    logger.info("✅ OpenAI client created with custom httpx client.")
except Exception as e:
    logger.warning(f"⚠️ OpenAI client initialization failed ({e}). Using default init.")
    client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------------------------------------------------
# Main Function
# ----------------------------------------------------------------------
def process_with_genai(extracted: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process extracted text/fields using OpenAI (if key available),
    summarize or normalize data, and return structured output.
    """

    text_snippet = extracted.get("text", "") if isinstance(extracted, dict) else str(extracted)

    # Skip GenAI processing if API key is missing
    if not OPENAI_API_KEY:
        logger.warning("⚠️ No OPENAI_API_KEY found — skipping Generative AI processing.")
        return {
            "summary": "GenAI skipped (no API key provided).",
            "raw_output": text_snippet,
            "extracted": extracted,
        }

    prompt = PROMPTS + "\n\nExtracted text:\n" + text_snippet
    logger.info("🤖 Calling OpenAI for summarization/normalization...")

    try:
        # ---- Prefer new Responses API ----
        if hasattr(client, "responses") and hasattr(client.responses, "create"):
            response = client.responses.create(model="gpt-4o-mini", input=prompt)
            out_text = ""

            if hasattr(response, "output") and response.output:
                try:
                    out_text = response.output[0].content[0].text
                except Exception:
                    out_text = str(response.output)
            elif isinstance(response, dict) and "output_text" in response:
                out_text = response["output_text"]
            else:
                out_text = str(response)

        # ---- Fallback: old Chat Completions API ----
        elif hasattr(client, "chat"):
            chat_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            out_text = chat_response.choices[0].message.content

        # ---- Final fallback ----
        else:
            logger.error("❌ No valid response method found on OpenAI client — returning raw text.")
            out_text = text_snippet

        # ---- Try parsing JSON output ----
        try:
            parsed_json = json.loads(out_text)
            logger.info("🧩 OpenAI output successfully parsed as JSON.")
            return {"normalized": parsed_json, "raw_output": out_text}

        except json.JSONDecodeError:
            logger.debug("ℹ️ OpenAI output is not JSON — returning summary text.")
            return {"summary": out_text, "raw_output": out_text}

    # ---- Handle rate limits, quota errors, etc. ----
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "quota" in err_str.lower():
            logger.error("🚫 OpenAI quota exceeded or rate-limited — skipping GenAI output.")
            return {
                "error": "RateLimitError or insufficient quota",
                "summary": "OpenAI quota exceeded or rate-limited. Skipping GenAI step.",
                "raw_output": text_snippet,
            }

        logger.exception(f"GenAI processing error: {e}")
        return {
            "error": str(e),
            "summary": "GenAI step failed.",
            "extracted": extracted,
        }
