"""
Test OCR Fallback for Scanned PDFs — Gap 9
============================================
Verifies that:
1. OCR import attempt is present in resume_parser_service.py
2. _extract_pdf_ocr function exists
3. extract_text_from_pdf pipeline includes OCR as strategy 3
4. OCR gracefully degrades when pytesseract is not installed
"""

import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _read_source() -> str:
    return (ROOT / 'backend' / 'services' / 'resume_parser_service.py').read_text(encoding='utf-8')


def test_ocr_import_block_present():
    """resume_parser_service.py must attempt to import pytesseract + pdf2image."""
    src = _read_source()
    assert 'import pytesseract' in src
    assert 'from pdf2image import convert_from_bytes' in src
    assert 'OCR_AVAILABLE' in src


def test_ocr_extraction_function_exists():
    """_extract_pdf_ocr must be defined."""
    src = _read_source()
    assert 'def _extract_pdf_ocr(' in src


def test_extract_text_from_pdf_calls_ocr():
    """extract_text_from_pdf must include OCR as Strategy 3."""
    src = _read_source()
    # Find the extract_text_from_pdf function body
    start = src.index('def extract_text_from_pdf(')
    # Find the next top-level def
    end = src.index('\ndef ', start + 1)
    body = src[start:end]

    assert '_extract_pdf_ocr' in body, \
        "extract_text_from_pdf must call _extract_pdf_ocr as a fallback strategy"
    assert 'Strategy 3' in body or 'OCR' in body, \
        "extract_text_from_pdf should document OCR as strategy 3"


def test_ocr_module_import_graceful():
    """Importing resume_parser_service must not crash even if pytesseract is missing."""
    # This test verifies the try/except around the OCR import
    from backend.services import resume_parser_service
    # OCR_AVAILABLE may be True or False — just must not crash
    assert hasattr(resume_parser_service, 'OCR_AVAILABLE')
    assert hasattr(resume_parser_service, '_extract_pdf_ocr')


def test_ocr_returns_none_when_unavailable():
    """_extract_pdf_ocr must return None gracefully when OCR is not installed."""
    from backend.services.resume_parser_service import _extract_pdf_ocr, OCR_AVAILABLE
    if not OCR_AVAILABLE:
        assert _extract_pdf_ocr(b'%PDF-fake-data') is None


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
