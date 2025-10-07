from src.extraction import ocr, parser

def test_ocr_and_parse():
    txt = ocr.run_ocr('data/test/mock_claim.txt')
    parsed = parser.parse_claim(txt)
    assert 'raw_text_preview' in parsed
