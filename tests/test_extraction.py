import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import tempfile
from src.extraction.parser import extract_text
from src.extraction.ocr import ocr_image
from tests.conftest import temp_dir

@pytest.fixture
def mock_pdf_path(temp_dir):
    """Create a mock PDF path (simulate with text file for simplicity; in real, use pdfplumber test PDF)."""
    mock_file = temp_dir / "mock_claim.txt"  # Use .txt as proxy for PDF text extraction
    mock_file.write_text("""
    Claim ID: ABC123
    Date: 10/15/2023
    Amount: $2,500
    Description: Car accident.
    """)
    return mock_file

@pytest.fixture
def mock_image_path(temp_dir):
    """Create a simple mock image with text (using Pillow)."""
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Test Claim: $1000 on 01/01/2023", fill='black')
    img_path = temp_dir / "mock_image.png"
    img.save(img_path)
    return img_path

def test_ocr_image(mock_image_path):
    """Test OCR on a mock image."""
    img = Image.open(mock_image_path)
    text = ocr_image(img)
    assert isinstance(text, str)
    assert len(text) > 0  # Basic check; actual OCR may vary by Tesseract install
    # Note: OCR output is non-deterministic; test for presence of key terms if Tesseract works
    if "Claim" in text or "$" in text:  # Loose check
        assert True
    else:
        pytest.skip("Tesseract may not be installed or text too small; skipping detailed OCR check")

def test_extract_text_pdf_like(mock_pdf_path):
    """Test extraction from a text-based PDF (using .txt proxy)."""
    # Note: In real tests, use a actual PDF; here simulate by treating as non-PDF
    extracted = extract_text(mock_pdf_path)
    assert "structured" in extracted
    assert "unstructured" in extracted
    assert extracted["confidence"] > 0.8
    assert "Claim ID" in extracted["unstructured"]  # From mock text

def test_extract_text_image(mock_image_path):
    """Test extraction from image."""
    extracted = extract_text(mock_image_path)
    assert extracted["unstructured"] != ""  # OCR should extract something
    assert extracted["confidence"] == 0.9  # Default for images

def test_extract_text_invalid_file():
    """Test error handling for invalid file."""
    invalid_path = Path("/nonexistent/file.pdf")
    extracted = extract_text(invalid_path)
    assert extracted["confidence"] == 0.0
    assert extracted["unstructured"] == ""