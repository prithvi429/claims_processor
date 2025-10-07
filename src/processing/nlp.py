import spacy
import subprocess
import sys
from src.utils.logging import logger

def load_spacy_model():
    """
    Loads the spaCy 'en_core_web_sm' model.
    If not found, it automatically installs it via subprocess.
    Works both in Docker and on local Windows.
    """
    try:
        nlp = spacy.load("en_core_web_sm")
        logger.info("✅ spaCy model 'en_core_web_sm' loaded successfully.")
        return nlp
    except OSError:
        logger.warning("⚠️ spaCy model 'en_core_web_sm' not found. Attempting installation...")

        # Attempt to install the model via subprocess
        try:
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
            )
            nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model 'en_core_web_sm' downloaded and loaded successfully.")
            return nlp
        except Exception as e:
            logger.error(f"❌ Failed to download spaCy model automatically: {e}")
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' could not be installed automatically. "
                "Please run manually:\n  python -m spacy download en_core_web_sm"
            )

nlp = load_spacy_model()


def extract_entities(text: str):
    """
    Extracts named entities (dates, amounts, organizations, etc.)
    from unstructured text using spaCy's NER.

    Args:
        text (str): Input text string.
    Returns:
        dict: Entity label -> entity text
    """
    if not text or not isinstance(text, str):
        logger.warning("⚠️ No valid text provided for entity extraction.")
        return {}

    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents}

    if entities:
        logger.debug(f"🧾 Extracted entities: {entities}")
    else:
        logger.info("ℹ️ No entities found in provided text.")

    return entities
