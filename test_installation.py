"""
Test installation and imports
"""
import sys
sys.path.append("src")

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
        
        import deep_translator
        print("✅ Deep-translator imported successfully")
        
        import pypdf
        print("✅ pypdf imported successfully")
        
        import fitz  # PyMuPDF
        print("✅ PyMuPDF imported successfully")
        
        import docx
        print("✅ python-docx imported successfully")
        
        import langdetect
        print("✅ langdetect imported successfully")
        
        from src.document_processor import DocumentProcessor
        print("✅ DocumentProcessor imported successfully")
        
        from src.translator import DocumentTranslator
        print("✅ DocumentTranslator imported successfully")
        
        from src.utils import DocumentUtils
        print("✅ DocumentUtils imported successfully")
        
        print("\n🎉 All imports successful! System is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing NLP Document Translator Installation")
    print("=" * 50)
    test_imports()