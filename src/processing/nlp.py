import spacy
from ..utils.logging import logger

# Load spaCy model (run once)
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logger.error("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    raise

def extract_entities(text):
    """
    Use spaCy NER to extract key entities from unstructured text.
    Returns dict: {label: text}
    """
    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents}
    logger.debug(f"Extracted entities: {entities}")
    return entities