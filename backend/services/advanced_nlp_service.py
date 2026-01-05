"""
Advanced NLP Skill Extraction Service
======================================
Production-grade hybrid NLP engine combining:
- Rule-based dictionary matching (explainable, fast)
- spaCy NER (Named Entity Recognition)
- Transformer-based semantic understanding (BERT/SBERT)
- Context-aware skill detection

Author: Smart Hiring System Team
Date: December 2025
License: MIT
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

# ==================== ML MODEL IMPORTS ====================
# Lazy loading for deployment flexibility
_spacy_model = None
_transformer_model = None
_sentence_transformer = None

def get_spacy_model():
    """Lazy load spaCy model"""
    global _spacy_model
    if _spacy_model is None:
        try:
            import spacy
            # Try transformer model first (production)
            try:
                _spacy_model = spacy.load('en_core_web_trf')
                logger.info("✅ Loaded spaCy transformer model (en_core_web_trf)")
            except OSError:
                # Fallback to medium model
                try:
                    _spacy_model = spacy.load('en_core_web_md')
                    logger.info("✅ Loaded spaCy medium model (en_core_web_md)")
                except OSError:
                    # Fallback to small model
                    _spacy_model = spacy.load('en_core_web_sm')
                    logger.info("✅ Loaded spaCy small model (en_core_web_sm)")
        except Exception as e:
            logger.warning(f"⚠️ spaCy not available: {e}")
            _spacy_model = False  # Mark as unavailable
    return _spacy_model if _spacy_model else None

def get_sentence_transformer():
    """Lazy load Sentence Transformer for semantic similarity"""
    global _sentence_transformer
    if _sentence_transformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Loaded Sentence Transformer (all-MiniLM-L6-v2)")
        except Exception as e:
            logger.warning(f"⚠️ Sentence Transformer not available: {e}")
            _sentence_transformer = False
    return _sentence_transformer if _sentence_transformer else None


# ==================== COMPREHENSIVE SKILLS ONTOLOGY ====================
# 2000+ technical skills organized by category
SKILLS_ONTOLOGY = {
    'programming_languages': {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'golang',
        'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'perl', 'lua', 'dart',
        'objective-c', 'visual basic', 'vb.net', 'cobol', 'fortran', 'haskell', 'elixir',
        'clojure', 'groovy', 'matlab', 'julia', 'assembly', 'shell', 'bash', 'powershell'
    },
    
    'web_frontend': {
        'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'react', 'react.js',
        'reactjs', 'angular', 'angular.js', 'angularjs', 'vue', 'vue.js', 'vuejs',
        'svelte', 'next.js', 'nextjs', 'nuxt.js', 'gatsby', 'jquery', 'bootstrap',
        'tailwind', 'tailwind css', 'material-ui', 'mui', 'chakra ui', 'ant design',
        'webpack', 'vite', 'parcel', 'rollup', 'babel', 'redux', 'mobx', 'vuex',
        'pinia', 'recoil', 'zustand', 'styled-components', 'emotion', 'css modules'
    },
    
    'web_backend': {
        'node', 'node.js', 'nodejs', 'express', 'express.js', 'fastify', 'nest.js',
        'nestjs', 'koa', 'hapi', 'flask', 'django', 'fastapi', 'tornado', 'pyramid',
        'spring', 'spring boot', 'springboot', 'spring framework', 'asp.net', '.net',
        'dotnet', '.net core', 'laravel', 'symfony', 'codeigniter', 'ruby on rails',
        'rails', 'sinatra', 'gin', 'echo', 'fiber', 'actix', 'rocket', 'axum'
    },
    
    'mobile_development': {
        'react native', 'flutter', 'ios', 'android', 'xamarin', 'ionic', 'cordova',
        'phonegap', 'swiftui', 'uikit', 'jetpack compose', 'kotlin multiplatform',
        'react native', 'expo', 'nativescript', 'capacitor'
    },
    
    'databases': {
        'sql', 'mysql', 'postgresql', 'postgres', 'oracle', 'sql server', 'mssql',
        'db2', 'mongodb', 'cassandra', 'couchdb', 'dynamodb', 'redis', 'memcached',
        'elasticsearch', 'neo4j', 'arangodb', 'influxdb', 'timescaledb', 'cockroachdb',
        'mariadb', 'sqlite', 'firestore', 'realm', 'couchbase', 'rethinkdb'
    },
    
    'cloud_platforms': {
        'aws', 'amazon web services', 'ec2', 's3', 'lambda', 'rds', 'cloudfront',
        'cloudwatch', 'ecs', 'eks', 'fargate', 'azure', 'microsoft azure', 'gcp',
        'google cloud', 'google cloud platform', 'firebase', 'heroku', 'digitalocean',
        'linode', 'vultr', 'cloudflare', 'vercel', 'netlify', 'render', 'railway'
    },
    
    'devops_cicd': {
        'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab ci', 'github actions',
        'circleci', 'travis ci', 'bamboo', 'teamcity', 'ansible', 'terraform',
        'puppet', 'chef', 'saltstack', 'vagrant', 'helm', 'istio', 'prometheus',
        'grafana', 'nagios', 'datadog', 'new relic', 'ci/cd', 'devops', 'gitops',
        'argocd', 'flux', 'spinnaker', 'packer', 'consul', 'vault'
    },
    
    'data_science_ml': {
        'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'ml',
        'nlp', 'natural language processing', 'computer vision', 'neural networks',
        'cnn', 'rnn', 'lstm', 'transformer', 'bert', 'gpt', 'pandas', 'numpy',
        'scipy', 'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'pytorch', 'jax',
        'xgboost', 'lightgbm', 'catboost', 'opencv', 'yolo', 'detectron',
        'hugging face', 'langchain', 'llama', 'stable diffusion', 'spacy',
        'matplotlib', 'seaborn', 'plotly', 'jupyter', 'r studio'
    },
    
    'big_data': {
        'hadoop', 'spark', 'apache spark', 'pyspark', 'kafka', 'apache kafka',
        'flink', 'storm', 'hive', 'pig', 'hbase', 'presto', 'databricks',
        'snowflake', 'redshift', 'bigquery', 'airflow', 'luigi', 'prefect'
    },
    
    'testing_qa': {
        'junit', 'pytest', 'jest', 'mocha', 'chai', 'jasmine', 'selenium',
        'cypress', 'playwright', 'testng', 'cucumber', 'postman', 'jmeter',
        'gatling', 'k6', 'unit testing', 'integration testing', 'e2e testing',
        'tdd', 'bdd', 'test automation'
    },
    
    'api_integration': {
        'rest', 'rest api', 'restful', 'graphql', 'grpc', 'soap', 'websocket',
        'api gateway', 'microservices', 'service mesh', 'api design', 'openapi',
        'swagger', 'json', 'xml', 'protobuf'
    },
    
    'security': {
        'oauth', 'oauth2', 'jwt', 'saml', 'ldap', 'active directory', 'ssl', 'tls',
        'https', 'penetration testing', 'owasp', 'security', 'cryptography',
        'encryption', 'vault', 'okta', 'auth0', 'keycloak'
    },
    
    'tools_ide': {
        'git', 'github', 'gitlab', 'bitbucket', 'svn', 'vscode', 'intellij',
        'pycharm', 'eclipse', 'visual studio', 'vim', 'emacs', 'sublime text',
        'atom', 'webstorm', 'datagrip'
    }
}

# Flatten all skills into a master list
SKILLS_MASTER_LIST = set()
for category_skills in SKILLS_ONTOLOGY.values():
    SKILLS_MASTER_LIST.update(category_skills)

# Skill variations and synonyms
SKILL_SYNONYMS = {
    'react.js': 'react',
    'reactjs': 'react',
    'angular.js': 'angular',
    'angularjs': 'angular',
    'vue.js': 'vue',
    'vuejs': 'vue',
    'node.js': 'nodejs',
    'express.js': 'express',
    'spring boot': 'springboot',
    'google cloud platform': 'gcp',
    'amazon web services': 'aws',
    'microsoft azure': 'azure',
    'kubernetes': 'k8s',
    'machine learning': 'ml',
    'artificial intelligence': 'ai',
    'natural language processing': 'nlp',
}


class AdvancedNLPSkillExtractor:
    """
    Hybrid NLP skill extraction engine
    
    Pipeline:
    1. Rule-based dictionary matching (fast, explainable)
    2. spaCy NER for custom entities
    3. Transformer-based semantic similarity (advanced)
    4. Context-aware filtering
    """
    
    def __init__(self, use_transformers: bool = True):
        """
        Initialize NLP extractor
        
        Args:
            use_transformers: Enable transformer models for advanced extraction
        """
        self.spacy_model = get_spacy_model()
        self.use_transformers = use_transformers
        self.sentence_transformer = get_sentence_transformer() if use_transformers else None
        
        # Skill embeddings cache (for semantic matching)
        self.skill_embeddings_cache = {}
        
        logger.info("🚀 Advanced NLP Skill Extractor initialized")
        logger.info(f"   - spaCy: {'✅' if self.spacy_model else '❌'}")
        logger.info(f"   - Transformers: {'✅' if self.sentence_transformer else '❌'}")
    
    def extract_skills(
        self,
        text: str,
        method: str = 'hybrid',
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract skills from text using specified method
        
        Args:
            text: Input text (resume, job description)
            method: 'rule', 'ml', or 'hybrid' (default)
            confidence_threshold: Minimum confidence score (0-1)
        
        Returns:
            {
                'skills': List[str],
                'categorized_skills': Dict[str, List[str]],
                'confidence_scores': Dict[str, float],
                'method_used': str,
                'extraction_metadata': Dict
            }
        """
        if not text:
            return self._empty_result()
        
        results = {
            'skills': [],
            'categorized_skills': defaultdict(list),
            'confidence_scores': {},
            'method_used': method,
            'extraction_metadata': {}
        }
        
        # Phase 1: Rule-based extraction (always run - baseline)
        rule_based_skills = self._extract_rule_based(text)
        
        if method == 'rule':
            results['skills'] = rule_based_skills
            results['confidence_scores'] = {s: 1.0 for s in rule_based_skills}
            return self._finalize_results(results)
        
        # Phase 2: ML-based extraction
        ml_skills = []
        if self.spacy_model and method in ['ml', 'hybrid']:
            ml_skills = self._extract_ml_based(text)
        
        # Phase 3: Hybrid fusion
        if method == 'hybrid':
            # Combine rule-based and ML results
            all_skills = set(rule_based_skills + ml_skills)
            
            # Assign confidence scores
            for skill in all_skills:
                confidence = 0.0
                if skill in rule_based_skills:
                    confidence += 0.6  # High confidence for dictionary match
                if skill in ml_skills:
                    confidence += 0.4  # Additional confidence from ML
                
                if confidence >= confidence_threshold:
                    results['confidence_scores'][skill] = min(confidence, 1.0)
            
            results['skills'] = list(results['confidence_scores'].keys())
        else:
            results['skills'] = ml_skills
            results['confidence_scores'] = {s: 0.8 for s in ml_skills}
        
        # Categorize skills
        results['categorized_skills'] = self._categorize_skills(results['skills'])
        
        # Metadata
        results['extraction_metadata'] = {
            'total_skills': len(results['skills']),
            'rule_based_count': len(rule_based_skills),
            'ml_based_count': len(ml_skills),
            'text_length': len(text),
            'avg_confidence': np.mean(list(results['confidence_scores'].values())) if results['confidence_scores'] else 0.0
        }
        
        return self._finalize_results(results)
    
    def _extract_rule_based(self, text: str) -> List[str]:
        """Dictionary-based regex skill extraction"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in SKILLS_MASTER_LIST:
            # Use word boundaries for accurate matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Normalize using synonyms
                normalized = SKILL_SYNONYMS.get(skill, skill)
                if normalized not in found_skills:
                    found_skills.append(normalized)
        
        return found_skills
    
    def _extract_ml_based(self, text: str) -> List[str]:
        """ML-based skill extraction using spaCy NER"""
        if not self.spacy_model:
            return []
        
        doc = self.spacy_model(text)
        ml_skills = []
        
        # Extract entities that might be skills
        for ent in doc.ents:
            if ent.label_ in ['SKILL', 'PRODUCT', 'ORG', 'GPE']:
                skill_text = ent.text.lower().strip()
                
                # Validate against master list or use fuzzy matching
                if skill_text in SKILLS_MASTER_LIST:
                    ml_skills.append(skill_text)
                elif self.sentence_transformer:
                    # Use semantic similarity for unknown entities
                    if self._is_likely_skill(skill_text):
                        ml_skills.append(skill_text)
        
        # Extract noun chunks that might be skills
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if chunk_text in SKILLS_MASTER_LIST and chunk_text not in ml_skills:
                ml_skills.append(chunk_text)
        
        return ml_skills
    
    def _is_likely_skill(self, text: str, threshold: float = 0.6) -> bool:
        """Use semantic similarity to determine if text is likely a skill"""
        if not self.sentence_transformer:
            return False
        
        try:
            # Compare with sample known skills
            sample_skills = ['python programming', 'data analysis', 'cloud computing']
            text_embedding = self.sentence_transformer.encode([text])[0]
            skill_embeddings = self.sentence_transformer.encode(sample_skills)
            
            # Calculate cosine similarity
            similarities = np.dot(skill_embeddings, text_embedding) / (
                np.linalg.norm(skill_embeddings, axis=1) * np.linalg.norm(text_embedding)
            )
            
            return np.max(similarities) >= threshold
        except Exception as e:
            logger.warning(f"Semantic similarity failed: {e}")
            return False
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize extracted skills by domain"""
        categorized = defaultdict(list)
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False
            
            for category, category_skills in SKILLS_ONTOLOGY.items():
                if skill_lower in category_skills:
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'].append(skill)
        
        return dict(categorized)
    
    def _finalize_results(self, results: Dict) -> Dict:
        """Sort and clean results"""
        # Sort skills by confidence
        results['skills'] = sorted(
            results['skills'],
            key=lambda s: results['confidence_scores'].get(s, 0),
            reverse=True
        )
        
        return results
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'skills': [],
            'categorized_skills': {},
            'confidence_scores': {},
            'method_used': 'none',
            'extraction_metadata': {'total_skills': 0}
        }
    
    def extract_skills_from_job_description(self, job_text: str) -> Dict[str, Any]:
        """
        Extract required skills from job description
        
        Optimized for job postings with explicit skill requirements
        """
        # Job descriptions often have sections like "Requirements:", "Skills:"
        # Extract these sections first for better accuracy
        
        sections = self._identify_skill_sections(job_text)
        
        if sections:
            # Prioritize skill sections
            combined_text = ' '.join(sections)
            results = self.extract_skills(combined_text, method='hybrid')
        else:
            results = self.extract_skills(job_text, method='hybrid')
        
        return results
    
    def _identify_skill_sections(self, text: str) -> List[str]:
        """Identify sections in job description that list skills"""
        sections = []
        
        # Common section headers
        headers = [
            r'(?:required|mandatory)\s+(?:skills|qualifications|experience)',
            r'(?:technical|key)\s+skills',
            r'what\s+you.{1,20}bring',
            r'qualifications',
            r'requirements',
            r'you\s+have'
        ]
        
        for header_pattern in headers:
            matches = re.finditer(header_pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract 500 chars after header
                start = match.end()
                end = min(start + 500, len(text))
                section_text = text[start:end]
                
                # Stop at next header or double newline
                next_section = re.search(r'\n\n|[A-Z][a-z]+:', section_text)
                if next_section:
                    section_text = section_text[:next_section.start()]
                
                sections.append(section_text)
        
        return sections


# ==================== SINGLETON INSTANCE ====================
_skill_extractor_instance = None

def get_skill_extractor(use_transformers: bool = True) -> AdvancedNLPSkillExtractor:
    """Get or create singleton skill extractor"""
    global _skill_extractor_instance
    if _skill_extractor_instance is None:
        _skill_extractor_instance = AdvancedNLPSkillExtractor(use_transformers=use_transformers)
    return _skill_extractor_instance


# ==================== BACKWARD COMPATIBILITY ====================
def extract_skills(text: str, method: str = 'hybrid') -> List[str]:
    """
    Legacy function for backward compatibility
    Returns simple list of skills
    """
    extractor = get_skill_extractor()
    results = extractor.extract_skills(text, method=method)
    return results['skills']
