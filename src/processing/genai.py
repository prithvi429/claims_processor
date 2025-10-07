import json
from openai import OpenAI
from .nlp import extract_entities
from ..config import OPENAI_API_KEY, PROMPTS
from ..utils.logging import logger

client = OpenAI(api_key=OPENAI_API_KEY)

def process_with_genai(extracted):
    """
    Combine NLP entities with GenAI for summarization/normalization.
    Input: extracted dict from extraction.
    Output: processed dict with schema fields.
    """
    unstructured = extracted["unstructured"]
    structured = extracted["structured"]
    
    # Step 1: NLP entities
    entities = extract_entities(unstructured)
    
    # Initial processed dict (merge structured + entities)
    processed = {
        "claim_id": entities.get("PERSON", structured.get("claim_id", "Unknown")),
        "incident_date": "",  # To be normalized
        "claim_amount": 0.0,  # To be normalized
        "damage_description": entities.get("EVENT", unstructured[:200]),
        "summary": "",
        "confidence": extracted["confidence"]
    }
    
    # Step 2: GenAI for summarization/normalization
    if OPENAI_API_KEY:
        try:
            prompt_text = PROMPTS["summarization"].format(text=unstructured[:1000])  # Limit length
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.1  # Low for consistency
            )
            ai_output_str = response.choices[0].message.content.strip()
            
            # Parse JSON from response (assume clean JSON output)
            ai_output = json.loads(ai_output_str)
            
            # Merge (override with AI where possible)
            processed.update({
                k: v for k, v in ai_output.items() if k in processed
            })
            processed["summary"] = ai_output.get("summary", "No summary generated")
            processed["confidence"] = ai_output.get("confidence", processed["confidence"])
            
            logger.info(f"GenAI processed: Confidence {processed['confidence']}")
            
        except json.JSONDecodeError:
            logger.warning("GenAI output not valid JSON; using fallback")
        except Exception as e:
            logger.error(f"GenAI failed: {e}")
    else:
        logger.warning("No OpenAI key; skipping GenAI")
    
    # Fallback normalization (if no AI)
    from ..utils.normalization import normalize_date, normalize_amount
    processed["incident_date"] = normalize_date(processed["incident_date"] or entities.get("DATE", structured.get("date", "")))
    processed["claim_amount"] = normalize_amount(processed["claim_amount"] or entities.get("MONEY", structured.get("amount", "0")))
    
    return processed