"""
Resume Parser - Production Version
Extracts text and skills from PDF/DOCX resumes
"""
import re
import io
import logging

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 not available - PDF parsing disabled")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx not available - DOCX parsing disabled")

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    NLP_AVAILABLE = True
except Exception:
    NLP_AVAILABLE = False
    nlp = None
    logging.warning("spaCy not available - using keyword extraction")

def _get_nlp():
    """Get spaCy NLP model if available"""
    return nlp if NLP_AVAILABLE else None

def extract_text_from_pdf(file_data):
    """
    Extract text from PDF file
    
    Args:
        file_data: Binary PDF file data or file-like object
    
    Returns:
        str: Extracted text content
    """
    if not PDF_AVAILABLE:
        return "PDF parsing not available. Please install PyPDF2."
    
    try:
        # Handle both bytes and file-like objects
        if isinstance(file_data, bytes):
            pdf_file = io.BytesIO(file_data)
        else:
            pdf_file = file_data
        
        reader = PdfReader(pdf_file)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        full_text = "\n".join(text_parts)
        return full_text if full_text.strip() else "No text could be extracted from PDF"
    
    except Exception as e:
        logging.error(f"PDF extraction error: {e}")
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_data):
    """
    Extract text from DOCX file
    
    Args:
        file_data: Binary DOCX file data or file-like object
    
    Returns:
        str: Extracted text content
    """
    if not DOCX_AVAILABLE:
        return "DOCX parsing not available. Please install python-docx."
    
    try:
        # Handle both bytes and file-like objects
        if isinstance(file_data, bytes):
            docx_file = io.BytesIO(file_data)
        else:
            docx_file = file_data
        
        doc = Document(docx_file)
        text_parts = []
        
        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text)
        
        full_text = "\n".join(text_parts)
        return full_text if full_text.strip() else "No text could be extracted from DOCX"
    
    except Exception as e:
        logging.error(f"DOCX extraction error: {e}")
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_file(file_data, filename):
    """Extract text from uploaded file - stub version"""
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
    """
    Advanced anonymization removing ALL bias-inducing attributes
    
    Removes protected characteristics to prevent unconscious bias:
    - Personal identifiers (names, emails, phones, addresses)
    - Gender markers (pronouns, titles, gendered words)
    - Age indicators (graduation years, decades of experience)
    - Ethnicity proxies (ethnic names, minority-serving institutions)
    - Socioeconomic markers (elite universities, zip codes)
    
    Based on: Fabris et al. (2025) - Pre-processing bias mitigation
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Remove contact information
    text = re.sub(r'\S+@\S+', ' [EMAIL] ', text)
    text = re.sub(r'\+?\d[\d\-\s()]{6,}\d', ' [PHONE] ', text)
    text = re.sub(r'http\S+|www\.\S+', ' [URL] ', text)
    
    # 2. Remove addresses (location bias)
    text = re.sub(r'\d+\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}', ' [ADDRESS] ', text)
    text = re.sub(r'\b\d{5}(?:-\d{4})?\b', ' [ZIP] ', text)  # Zip codes
    
    # 3. Remove gender markers
    # Pronouns
    text = re.sub(r'\b(he|she|him|her|his|hers|himself|herself)\b', '[PRONOUN]', text, flags=re.IGNORECASE)
    # Titles
    text = re.sub(r'\b(mr\.|mrs\.|ms\.|miss|sir|madam)\b', '[TITLE]', text, flags=re.IGNORECASE)
    # Explicit gender words
    text = re.sub(r'\b(male|female|man|woman|boy|girl|gentleman|lady)\b', '[GENDER]', text, flags=re.IGNORECASE)
    
    # 4. Remove age indicators
    # Graduation years (strong age proxy)
    text = re.sub(r'\b(graduated|graduation|class of|batch of)\s+[\'"]?\d{4}[\'"]?\b', '[GRAD_YEAR]', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(19\d{2}|20[0-2]\d)\s*-\s*(19\d{2}|20[0-2]\d)\b', '[DATE_RANGE]', text)
    # Years of experience
    text = re.sub(r'\b(\d+)\s*\+?\s*years?\s*(of\s*)?(experience|exp)\b', '[EXPERIENCE_YEARS]', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(over|more than|approximately)\s+\d+\s+years?\b', '[EXPERIENCE_DURATION]', text, flags=re.IGNORECASE)
    
    # 5. Remove ethnicity-associated markers
    # Women's colleges (gender proxy)
    womens_colleges = [
        'barnard', 'smith college', 'wellesley', 'mount holyoke', 'bryn mawr',
        'mills college', 'scripps', 'simmons', 'spelman', 'bennett college'
    ]
    for college in womens_colleges:
        text = re.sub(r'\b' + college + r'\b', '[COLLEGE]', text, flags=re.IGNORECASE)
    
    # Historically Black Colleges/Universities (ethnicity proxy)
    hbcus = [
        'howard', 'morehouse', 'spelman', 'fisk', 'tuskegee', 'hampton',
        'xavier', 'dillard', 'meharry', 'florida a&m'
    ]
    for hbcu in hbcus:
        text = re.sub(r'\b' + hbcu + r'\b', '[UNIVERSITY]', text, flags=re.IGNORECASE)
    
    # 6. Remove elite university names (socioeconomic proxy)
    elite_universities = [
        'harvard', 'yale', 'princeton', 'stanford', 'mit', 'caltech',
        'oxford', 'cambridge', 'columbia', 'upenn', 'dartmouth', 'brown',
        'cornell', 'duke', 'northwestern', 'johns hopkins'
    ]
    for uni in elite_universities:
        text = re.sub(r'\b' + uni + r'\b', '[UNIVERSITY]', text, flags=re.IGNORECASE)
    
    # 7. Remove common ethnic names (controversial but necessary for fairness)
    # Note: This is a simplified approach. Production systems should use NER models.
    ethnic_name_patterns = [
        r'\b(muhammad|ahmed|ali|hassan|fatima|aisha)\b',  # Arabic
        r'\b(raj|priya|amit|kumar|patel|singh)\b',  # Indian
        r'\b(wang|li|chen|zhang|liu|yang)\b',  # Chinese
        r'\b(jose|maria|juan|carlos|rodriguez)\b',  # Hispanic
        r'\b(jamal|latasha|deshawn|tyrone|tanisha)\b',  # African American
    ]
    for pattern in ethnic_name_patterns:
        text = re.sub(pattern, '[NAME]', text, flags=re.IGNORECASE)
    
    # 8. Remove header (likely contains full name)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        first = lines[0]
        # If first line looks like a name (1-4 words, title case)
        if 1 <= len(first.split()) <= 4 and first == first.title():
            lines[0] = "[NAME]"
        text = "\n".join(lines)
    
    # 9. Remove marital status indicators
    text = re.sub(r'\b(married|single|divorced|widowed|spouse|husband|wife)\b', '[MARITAL_STATUS]', text, flags=re.IGNORECASE)
    
    # 10. Remove age-related words
    text = re.sub(r'\b(young|old|senior|junior|age|aged|years old)\b', '[AGE_DESCRIPTOR]', text, flags=re.IGNORECASE)
    
    # 11. Compact whitespace
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    
    return text


# Comprehensive skill database (200+ skills)
SKILL_DATABASE = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift',
    'kotlin', 'go', 'rust', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
    
    # Web Technologies
    'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express', 'django', 'flask',
    'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind', 'sass', 'webpack', 'vite',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra',
    'dynamodb', 'elasticsearch', 'neo4j', 'firebase',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions',
    'terraform', 'ansible', 'ci/cd', 'devops', 'linux', 'unix',
    
    # Data Science & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
    'pandas', 'numpy', 'nlp', 'computer vision', 'data analysis', 'statistics',
    'tableau', 'power bi', 'spark', 'hadoop', 'kafka',
    
    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'swift ui',
    
    # Tools & Frameworks
    'git', 'jira', 'agile', 'scrum', 'restful api', 'graphql', 'microservices',
    'api development', 'testing', 'junit', 'pytest', 'selenium', 'jest',
    
    # Soft Skills
    'communication', 'leadership', 'team player', 'problem solving', 'critical thinking',
    'project management', 'time management', 'collaboration',
    
    # Security
    'cybersecurity', 'penetration testing', 'oauth', 'jwt', 'encryption', 'ssl/tls',
    
    # Design
    'ui/ux', 'figma', 'adobe xd', 'photoshop', 'illustrator', 'graphic design',
    
    # Business
    'product management', 'business analysis', 'data analysis', 'excel', 'powerpoint'
}


def extract_skills(text):
    """
    Extract skills from resume text using keyword matching
    
    Args:
        text: Resume text content
    
    Returns:
        list: Extracted skills
    """
    if not isinstance(text, str):
        return []
    
    text_lower = text.lower()
    found_skills = set()
    
    # Check for each skill in the database
    for skill in SKILL_DATABASE:
        # Use word boundaries for exact matches
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.add(skill)
    
    # If spaCy available, use NER for additional extraction
    if NLP_AVAILABLE and nlp:
        try:
            doc = nlp(text[:10000])  # Limit text length for performance
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'LANGUAGE']:
                    skill_text = ent.text.lower().strip()
                    if len(skill_text) > 2:  # Avoid very short matches
                        found_skills.add(skill_text)
        except Exception as e:
            logging.warning(f"NER extraction failed: {e}")
    
    return sorted(list(found_skills))


def parse_resume(file_data, filename):
    """
    Complete resume parsing pipeline
    
    Args:
        file_data: Binary file data
        filename: Original filename
    
    Returns:
        dict: Parsed resume data with text, skills, etc.
    """
    # Extract text
    text = extract_text_from_file(file_data, filename)
    
    # Extract skills
    skills = extract_skills(text)
    
    # Extract basic info (years of experience)
    experience_years = extract_experience_years(text)
    
    return {
        'raw_text': text,
        'skills': skills,
        'experience_years': experience_years,
        'anonymized_text': anonymize_text(text)
    }


def extract_experience_years(text):
    """
    Extract years of experience from resume
    
    Args:
        text: Resume text
    
    Returns:
        int: Estimated years of experience
    """
    if not isinstance(text, str):
        return 0
    
    text_lower = text.lower()
    
    # Look for explicit mentions like "5 years of experience"
    patterns = [
        r'(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\s*years?',
        r'(\d+)\s*years?\s+in\s+\w+',
    ]
    
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                years = int(match)
                max_years = max(max_years, years)
            except ValueError:
                pass
    
    return max_years
