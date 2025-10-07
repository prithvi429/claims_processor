from src.processing import nlp, genai

def test_processing_skeleton():
    s = genai.summarize_claim('Some claim text')
    assert isinstance(s, str)
