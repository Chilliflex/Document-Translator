"""
Configuration settings for NLP Document Translator
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# File upload settings
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
OUTPUT_FOLDER = BASE_DIR / "output" / "translated_documents"
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

# Translation settings
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi', 
    'mr': 'Marathi',
    'sa': 'Sanskrit'  # Note: Limited support
}

# Translation backends (ordered by preference)
TRANSLATION_BACKENDS = [
    'google',
    'microsoft', 
    'libre',
    'mymemory'
]

# Default translation settings
DEFAULT_SOURCE_LANG = 'auto'
DEFAULT_TARGET_LANG = 'en'
CHUNK_SIZE = 5000  # Characters per translation chunk

# Streamlit settings
STREAMLIT_CONFIG = {
    'page_title': 'NLP Document Translator',
    'page_icon': '🌍',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Create directories
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)