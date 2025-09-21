"""
Utility functions for the document translator
"""
import os
import hashlib
import tempfile
from pathlib import Path
from typing import Union, Dict, Any, Optional
import logging
from datetime import datetime
from fpdf import FPDF
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentUtils:
    """Utility functions for document operations"""
    
    @staticmethod
    def validate_file(file_content: bytes, filename: str, max_size_mb: int = 16) -> Dict[str, Any]:
        """
        Validate uploaded file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            max_size_mb: Maximum allowed file size in MB
            
        Returns:
            Dict with validation results
        """
        try:
            # Check file size
            size_mb = len(file_content) / (1024 * 1024)
            if size_mb > max_size_mb:
                return {
                    'valid': False,
                    'error': f'File too large. Maximum size: {max_size_mb}MB, your file: {size_mb:.2f}MB'
                }
            
            # Check file extension
            file_path = Path(filename)
            extension = file_path.suffix.lower()
            supported_formats = {'.pdf', '.docx', '.txt'}
            
            if extension not in supported_formats:
                return {
                    'valid': False,
                    'error': f'Unsupported file format. Supported: {", ".join(supported_formats)}'
                }
            
            # Check if file content is not empty
            if len(file_content) == 0:
                return {
                    'valid': False,
                    'error': 'File is empty'
                }
            
            return {
                'valid': True,
                'size_mb': round(size_mb, 2),
                'extension': extension,
                'error': None
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'File validation error: {str(e)}'
            }
    
    @staticmethod
    def generate_file_hash(content: bytes) -> str:
        """Generate MD5 hash of file content"""
        return hashlib.md5(content).hexdigest()
    
    @staticmethod
    def save_temp_file(content: bytes, filename: str) -> str:
        """
        Save content to temporary file
        
        Args:
            content: File content as bytes
            filename: Original filename (used for extension)
            
        Returns:
            Path to temporary file
        """
        try:
            file_path = Path(filename)
            extension = file_path.suffix
            
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp_file:
                tmp_file.write(content)
                return tmp_file.name
                
        except Exception as e:
            logger.error(f"Error saving temp file: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Remove temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Could not remove temp file {file_path}: {str(e)}")
    
    @staticmethod
    def create_translated_pdf(original_filename: str, translated_text: str, 
                             source_lang: str, target_lang: str) -> bytes:
        """
        Create a PDF with translated text
        
        Args:
            original_filename: Original file name
            translated_text: Translated text content
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            PDF content as bytes
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Add title
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f'Translation: {original_filename}', ln=True, align='C')
            pdf.ln(5)
            
            # Add translation info
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 5, f'Translated from {source_lang} to {target_lang}', ln=True)
            pdf.cell(0, 5, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
            pdf.ln(10)
            
            # Add translated text
            pdf.set_font('Arial', '', 12)
            
            # Split text into lines and add to PDF
            lines = translated_text.split('\n')
            for line in lines:
                if line.strip():
                    # Handle long lines by wrapping
                    if len(line) > 80:
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word + ' ') > 80:
                                if current_line:
                                    pdf.cell(0, 6, current_line.strip(), ln=True)
                                current_line = word + ' '
                            else:
                                current_line += word + ' '
                        if current_line:
                            pdf.cell(0, 6, current_line.strip(), ln=True)
                    else:
                        pdf.cell(0, 6, line, ln=True)
                else:
                    pdf.ln(3)  # Empty line spacing
            
            # Get PDF content
            pdf_content = bytes(pdf.output(dest='S'))
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error creating PDF: {str(e)}")
            # Create a simple error PDF
            error_pdf = FPDF()
            error_pdf.add_page()
            error_pdf.set_font('Arial', 'B', 16)
            error_pdf.cell(0, 10, 'Translation Error', ln=True, align='C')
            error_pdf.set_font('Arial', '', 12)
            error_pdf.cell(0, 10, f'Error creating translated PDF: {str(e)}', ln=True)
            return bytes(error_pdf.output(dest='S'))

    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename for safe saving"""
        # Remove or replace invalid characters
        import re
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return cleaned.strip()
    
    @staticmethod
    def get_language_display_name(lang_code: Union[str, list, None]) -> str:
        """
        Get display name for language code - FIXED VERSION
        """
        try:
            # Fix: Handle different input types
            if isinstance(lang_code, list):
                # If it's a list, take the first element
                lang_code = lang_code[0] if lang_code else 'unknown'
            elif lang_code is None:
                lang_code = 'unknown'
            
            # Ensure it's a string
            lang_code = str(lang_code).strip().lower()
            
            language_names = {
                'en': 'English 🇺🇸',
                'hi': 'Hindi 🇮🇳', 
                'mr': 'Marathi 🇮🇳',
                'sa': 'Sanskrit 🕉️',
                'fr': 'French 🇫🇷',
                'es': 'Spanish 🇪🇸',
                'de': 'German 🇩🇪',
                'it': 'Italian 🇮🇹',
                'pt': 'Portuguese 🇵🇹',
                'ru': 'Russian 🇷🇺',
                'ja': 'Japanese 🇯🇵',
                'ko': 'Korean 🇰🇷',
                'zh': 'Chinese 🇨🇳',
                'ar': 'Arabic 🇸🇦',
                'unknown': 'Unknown Language 🌐',
                'auto': 'Auto Detect 🔍'
            }
            
            return language_names.get(lang_code, f'{lang_code.upper()} 🌐')
            
        except Exception as e:
            logger.error(f"Error in get_language_display_name: {str(e)}")
            return 'Unknown Language 🌐'


class LogManager:
    """Simple logging manager for the application"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        
    def log_translation(self, filename: str, source_lang: str, target_lang: str, 
                       success: bool, error: str = None) -> None:
        """Log translation attempt"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        
        log_entry = f"{timestamp} | {status} | {filename} | {source_lang}→{target_lang}"
        if error:
            log_entry += f" | Error: {error}"
        
        logger.info(log_entry)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except Exception as e:
                logger.warning(f"Could not write to log file: {str(e)}")