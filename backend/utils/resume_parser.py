import re
import io
import docx
from PyPDF2 import PdfReader

# Lazy load spaCy
def _get_nlp():
    try:
        import spacy
        return spacy.load("en_core_web_sm")
    except Exception:
        return None

def extract_text_from_pdf(file_data):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(io.BytesIO(file_data))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_text_from_docx(file_data):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(file_data))
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return "\n".join(fullText)
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

def extract_text_from_file(file_data, filename):
    """Extract text from uploaded file based on extension"""
    name = filename.lower()
    
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_data)
    elif name.endswith(".docx") or name.endswith(".doc"):
        return extract_text_from_docx(file_data)
    else:
        # Treat as plain text
        try:
            return file_data.decode('utf-8', errors='ignore')
        except Exception:
            return str(file_data)

def anonymize_text(text):
    """Remove PII from text using regex and NER"""
    if not isinstance(text, str):
        return ""
    
    # Remove emails
    text = re.sub(r'\S+@\S+', ' [EMAIL] ', text)
    
    # Remove phone numbers (various formats)
    text = re.sub(r'\+?\d[\d\-\s()]{6,}\d', ' [PHONE] ', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', ' [URL] ', text)
    
    # Mask gender words
    text = re.sub(r'\b(Male|Female|male|female|M|F|Man|Woman|man|woman)\b', ' [GENDER] ', text)
    
    # Use spaCy NER if available (lazy load)
    nlp = _get_nlp()
    if nlp:
        try:
            doc = nlp(text)
            ents = list(doc.ents)
            # Process from end to start to maintain positions
            for ent in reversed(ents):
                if ent.label_ in ("PERSON", "GPE", "LOC", "NORP", "ORG", "DATE"):
                    start = ent.start_char
                    end = ent.end_char
                    text = text[:start] + " [REDACTED] " + text[end:]
        except Exception as e:
            print(f"NER error: {e}")
    else:
        # Fallback: simple header removal
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines:
            first = lines[0]
            if 1 <= len(first.split()) <= 4 and first == first.title():
                lines[0] = "[REDACTED HEADER]"
            text = "\n".join(lines)
    
    # Compact whitespace
    text = re.sub(r'\s{2,}', ' ', text)
    return text
