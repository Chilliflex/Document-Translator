"""
Translation module using multiple translation backends
"""
import logging
import time
import re
from typing import Dict, List, Optional, Tuple, Any
from deep_translator import GoogleTranslator, MicrosoftTranslator, LibreTranslator, MyMemoryTranslator
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set seed for consistent language detection
DetectorFactory.seed = 0

class DocumentTranslator:
    """
    Handles translation of documents using multiple translation backends
    """
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi', 
            'mr': 'Marathi',
            'sa': 'Sanskrit'  # Limited support
        }
        
        # Translation backends in order of preference
        self.backends = {
            'google': GoogleTranslator,
            'microsoft': MicrosoftTranslator, 
            'libre': LibreTranslator,
            'mymemory': MyMemoryTranslator
        }
        
        # Language code mappings for different backends
        self.language_mappings = {
            'sa': {  # Sanskrit mappings
                'google': 'sa',  # May not be fully supported
                'microsoft': 'sa',
                'libre': 'en',  # Fallback to English
                'mymemory': 'sa'
            }
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of input text
        
        Args:
            text: Input text to detect language
            
        Returns:
            Dict containing detected language info
        """
        try:
            # Clean text for better detection
            clean_text = self._clean_text_for_detection(text)
            
            if len(clean_text.strip()) < 10:
                return {
                    'language': 'unknown',
                    'confidence': 0.0,
                    'language_name': 'Unknown',
                    'error': 'Text too short for reliable detection'
                }
            
            detected_lang = detect(clean_text)
            confidence = self._calculate_confidence(clean_text, detected_lang)
            
            language_name = self.supported_languages.get(detected_lang, 
                                                       self._get_language_name(detected_lang))
            
            return {
                'language': detected_lang,
                'confidence': confidence,
                'language_name': language_name,
                'error': None
            }
            
        except LangDetectException as e:
            logger.error(f"Language detection failed: {str(e)}")
            return {
                'language': 'unknown',
                'confidence': 0.0,
                'language_name': 'Unknown',
                'error': f"Detection failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {str(e)}")
            return {
                'language': 'unknown',
                'confidence': 0.0,
                'language_name': 'Unknown', 
                'error': f"Unexpected error: {str(e)}"
            }
    
    def translate_text(self, text: str, target_lang: str, 
                      source_lang: str = 'auto', 
                      backend: str = 'google',
                      chunk_size: int = 5000) -> Dict[str, Any]:
        """
        Translate text using specified backend
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code ('auto' for detection)
            backend: Translation backend to use
            chunk_size: Size of text chunks for translation
            
        Returns:
            Dict containing translation results
        """
        try:
            if not text.strip():
                return {
                    'translated_text': '',
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'backend_used': backend,
                    'chunks_processed': 0,
                    'error': 'Empty text provided'
                }
            
            # Detect source language if auto
            if source_lang == 'auto':
                detection_result = self.detect_language(text)
                if detection_result['error']:
                    source_lang = 'en'  # Default fallback
                else:
                    source_lang = detection_result['language']
            
            # Check if translation is needed
            if source_lang == target_lang:
                return {
                    'translated_text': text,
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'backend_used': backend,
                    'chunks_processed': 1,
                    'error': None,
                    'note': 'No translation needed - same language'
                }
            
            # Handle Sanskrit special case
            if target_lang == 'sa' and backend == 'google':
                logger.warning("Sanskrit may have limited support in Google Translate")
            
            # Split text into chunks
            chunks = self._split_text_into_chunks(text, chunk_size)
            translated_chunks = []
            
            # Try primary backend first
            backend_success = False
            backend_used = backend
            
            for attempt_backend in [backend, 'google', 'libre', 'mymemory']:
                try:
                    translated_chunks = []
                    for i, chunk in enumerate(chunks):
                        translated_chunk = self._translate_chunk(
                            chunk, target_lang, source_lang, attempt_backend
                        )
                        translated_chunks.append(translated_chunk)
                        
                        # Small delay to avoid rate limiting
                        if i < len(chunks) - 1:
                            time.sleep(0.1)
                    
                    backend_used = attempt_backend
                    backend_success = True
                    break
                    
                except Exception as e:
                    logger.warning(f"Backend {attempt_backend} failed: {str(e)}")
                    continue
            
            if not backend_success:
                return {
                    'translated_text': '',
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'backend_used': None,
                    'chunks_processed': 0,
                    'error': 'All translation backends failed'
                }
            
            # Combine translated chunks
            full_translation = ' '.join(translated_chunks)
            
            return {
                'translated_text': full_translation,
                'source_language': source_lang,
                'target_language': target_lang,
                'backend_used': backend_used,
                'chunks_processed': len(chunks),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return {
                'translated_text': '',
                'source_language': source_lang,
                'target_language': target_lang,
                'backend_used': None,
                'chunks_processed': 0,
                'error': f"Translation failed: {str(e)}"
            }
    
    def _translate_chunk(self, chunk: str, target_lang: str, 
                        source_lang: str, backend: str) -> str:
        """Translate a single chunk of text"""
        try:
            # Get appropriate language codes for backend
            backend_target = self._get_backend_language_code(target_lang, backend)
            backend_source = self._get_backend_language_code(source_lang, backend) if source_lang != 'auto' else source_lang
            
            # Initialize translator based on backend
            if backend == 'google':
                translator = GoogleTranslator(source=backend_source, target=backend_target)
            elif backend == 'microsoft':
                translator = MicrosoftTranslator(source=backend_source, target=backend_target)
            elif backend == 'libre':
                translator = LibreTranslator(source=backend_source, target=backend_target)
            elif backend == 'mymemory':
                translator = MyMemoryTranslator(source=backend_source, target=backend_target)
            else:
                raise ValueError(f"Unsupported backend: {backend}")
            
            # Translate the chunk
            translated = translator.translate(chunk)
            return translated if translated else chunk
            
        except Exception as e:
            logger.error(f"Chunk translation failed with {backend}: {str(e)}")
            # Return original chunk if translation fails
            return chunk
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks for translation"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _clean_text_for_detection(self, text: str) -> str:
        """Clean text for better language detection"""
        # Remove extra whitespace, URLs, emails, etc.
        clean_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        clean_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
    
    def _calculate_confidence(self, text: str, detected_lang: str) -> float:
        """Calculate confidence score for language detection"""
        # This is a simplified confidence calculation
        # In practice, you might use langdetect's probability features
        try:
            from langdetect import detect_langs
            probs = detect_langs(text)
            for prob in probs:
                if prob.lang == detected_lang:
                    return round(prob.prob, 2)
            return 0.5  # Default moderate confidence
        except:
            return 0.5
    
    def _get_language_name(self, lang_code: str) -> str:
        """Get language name from code"""
        # Extended language names
        language_names = {
            'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi', 'sa': 'Sanskrit',
            'fr': 'French', 'es': 'Spanish', 'de': 'German', 'it': 'Italian',
            'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean',
            'zh': 'Chinese', 'ar': 'Arabic', 'th': 'Thai', 'vi': 'Vietnamese'
        }
        return language_names.get(lang_code, f"Language ({lang_code})")
    
    def _get_backend_language_code(self, lang_code: str, backend: str) -> str:
        """Get the appropriate language code for a specific backend"""
        if lang_code in self.language_mappings:
            return self.language_mappings[lang_code].get(backend, lang_code)
        return lang_code
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def batch_translate(self, texts: List[str], target_lang: str, 
                       source_lang: str = 'auto', 
                       backend: str = 'google') -> List[Dict[str, Any]]:
        """
        Translate multiple texts in batch
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
            source_lang: Source language code
            backend: Translation backend
            
        Returns:
            List of translation results
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Translating text {i+1}/{len(texts)}")
            result = self.translate_text(text, target_lang, source_lang, backend)
            results.append(result)
            
            # Small delay between translations
            if i < len(texts) - 1:
                time.sleep(0.2)
        
        return results