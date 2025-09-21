"""
NLP Document Translator - Main Streamlit Application
"""
import streamlit as st
import sys
from pathlib import Path
import io
import time
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.document_processor import DocumentProcessor
from src.translator import DocumentTranslator
from src.utils import DocumentUtils, LogManager
from config import *

# Initialize components
@st.cache_resource
def init_components():
    """Initialize document processor and translator"""
    return {
        'processor': DocumentProcessor(),
        'translator': DocumentTranslator(),
        'utils': DocumentUtils(),
        'logger': LogManager()
    }

def main():
    """Main application function"""
    # Configure page
    st.set_page_config(
        page_title=STREAMLIT_CONFIG['page_title'],
        page_icon=STREAMLIT_CONFIG['page_icon'],
        layout=STREAMLIT_CONFIG['layout'],
        initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
    )

    # Initialize components
    components = init_components()
    processor = components['processor']
    translator = components['translator']
    doc_utils = components['utils']
    log_manager = components['logger']

    # Application header
    st.title("🌍 Document Translator")
    st.markdown("### Upload documents (PDF, DOCX, TXT) and translate them to different languages")

    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        st.subheader("Translation Settings")

        available_languages = translator.get_available_languages()
        lang_options = [f"{code} - {name}" for code, name in available_languages.items()]

        target_language = st.selectbox(
            "Target Language:",
            options=lang_options,
            index=0,
            help="Select the language to translate to"
        )
        # FIX: Handle possible list return and conversion to code
        if isinstance(target_language, list):
            target_language = target_language[0] if target_language else "en - English"
        try:
            target_lang_code = str(target_language).split(" - ")[0].strip()
        except (AttributeError, IndexError):
            target_lang_code = "en"  # Default fallback

        source_language = st.selectbox(
            "Source Language:",
            options=["auto - Auto Detect"] + lang_options,
            index=0,
            help="Select source language or use auto-detect"
        )
        # FIX: Handle possible list return and conversion to code
        if isinstance(source_language, list):
            source_language = source_language[0] if source_language else "auto - Auto Detect"

        try:
            if str(source_language).startswith("auto"):
                source_lang_code = "auto"
            else:
                source_lang_code = str(source_language).split(" - ")[0].strip()
        except (AttributeError, IndexError):
            source_lang_code = "auto"  # Default fallback

        st.subheader("Advanced Settings")
        backend = st.selectbox(
            "Translation Backend:",
            options=['google', 'microsoft', 'libre', 'mymemory'],
            index=0,
            help="Choose translation service"
        )

        chunk_size = st.slider(
            "Chunk Size (characters):",
            min_value=1000,
            max_value=10000,
            value=5000,
            step=500,
            help="Size of text chunks for translation"
        )

        st.info(f"📋 **File Limits**\n- Max size: {MAX_FILE_SIZE // (1024*1024)}MB\n- Formats: PDF, DOCX, TXT")

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 Document Upload")
        uploaded_file = st.file_uploader(
            "Choose a document file",
            type=['pdf', 'docx', 'txt'],
            help="Upload a PDF, DOCX, or TXT file to translate"
        )
        if uploaded_file is not None:
            file_details = {
                "Filename": uploaded_file.name,
                "File Size": doc_utils.format_file_size(uploaded_file.size),
                "File Type": uploaded_file.type
            }
            st.success("✅ File uploaded successfully!")
            with st.expander("📋 File Details", expanded=False):
                for key, value in file_details.items():
                    st.write(f"**{key}:** {value}")

        if uploaded_file is not None:
            translate_button = st.button(
                "🚀 Translate Document",
                type="primary",
                use_container_width=True
            )
        else:
            translate_button = False
            st.info("👆 Please upload a document to begin translation")

    with col2:
        st.subheader("🔄 Translation Results")
        if uploaded_file is not None and translate_button:
            with st.spinner("Processing document..."):
                try:
                    file_content = uploaded_file.read()
                    uploaded_file.seek(0)
                    validation = doc_utils.validate_file(file_content, uploaded_file.name)
                    if not validation['valid']:
                        st.error(f"❌ {validation['error']}")
                        return
                    st.info("📖 Extracting text from document...")
                    file_extension = Path(uploaded_file.name).suffix.lower()
                    extraction_result = processor.extract_text(
                        io.BytesIO(file_content),
                        file_extension
                    )
                    if extraction_result['error']:
                        st.error(f"❌ Text extraction failed: {extraction_result['error']}")
                        return
                    extracted_text = extraction_result['text']
                    if not extracted_text.strip():
                        st.warning("⚠️ No text found in document")
                        return
                    # Display extraction info
                    with st.expander("📄 Extracted Text Preview", expanded=False):
                        st.text_area(
                            "Text Preview:",
                            doc_utils.truncate_text(extracted_text, 500),
                            height=150,
                            disabled=True
                        )
                        st.write(f"**Characters:** {len(extracted_text)}")
                        st.write(f"**Extraction Method:** {extraction_result.get('method', 'unknown')}")
                    # Detect language if auto
                    if source_lang_code == 'auto':
                        st.info("🔍 Detecting source language...")
                        detection_result = translator.detect_language(extracted_text)
                        if detection_result['error']:
                            st.warning(f"⚠️ Language detection failed: {detection_result['error']}")
                            detected_lang = 'en'
                        else:
                            detected_lang = detection_result['language']
                            st.success(f"✅ Detected language: {doc_utils.get_language_display_name(detected_lang)} "
                                    f"(Confidence: {detection_result['confidence']:.2f})")
                    else:
                        detected_lang = source_lang_code
                    if detected_lang == target_lang_code:
                        st.info("ℹ️ Source and target languages are the same. No translation needed.")
                        st.text_area("Original Text:", extracted_text, height=300, disabled=True)
                        return
                    st.info(f"🔄 Translating from {doc_utils.get_language_display_name(detected_lang)} "
                        f"to {doc_utils.get_language_display_name(target_lang_code)}...")
                    translation_result = translator.translate_text(
                        extracted_text,
                        target_lang_code,
                        detected_lang,
                        backend,
                        chunk_size
                    )
                    if translation_result['error']:
                        st.error(f"❌ Translation failed: {translation_result['error']}")
                        log_manager.log_translation(
                            uploaded_file.name, detected_lang, target_lang_code,
                            False, translation_result['error']
                        )
                        return
                    translated_text = translation_result['translated_text']
                    st.success(f"✅ Translation completed!")
                    # Translation info
                    with st.expander("ℹ️ Translation Details", expanded=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Source:** {doc_utils.get_language_display_name(translation_result['source_language'])}")
                            st.write(f"**Target:** {doc_utils.get_language_display_name(translation_result['target_language'])}")
                        with col_b:
                            st.write(f"**Backend:** {translation_result['backend_used']}")
                            st.write(f"**Chunks:** {translation_result['chunks_processed']}")
                    # Display translated text
                    st.subheader("📝 Translated Text")
                    st.text_area(
                        "Translation Result:",
                        translated_text,
                        height=400,
                        help="You can copy this text from here"
                    )
                    # Download options
                    st.subheader("💾 Download Options")
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        txt_download = st.download_button(
                            label="📄 Download as TXT",
                            data=translated_text.encode('utf-8'),
                            file_name=f"translated_{Path(uploaded_file.name).stem}_{target_lang_code}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with col_dl2:
                        try:
                            pdf_content = doc_utils.create_translated_pdf(
                                uploaded_file.name,
                                translated_text,
                                translation_result['source_language'],
                                translation_result['target_language']
                            )
                            pdf_download = st.download_button(
                                label="📑 Download as PDF",
                                data=pdf_content,
                                file_name=f"translated_{Path(uploaded_file.name).stem}_{target_lang_code}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"❌ PDF generation failed: {str(e)}")
                    log_manager.log_translation(
                        uploaded_file.name, 
                        translation_result['source_language'], 
                        translation_result['target_language'],
                        True
                    )
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    log_manager.log_translation(
                        uploaded_file.name if uploaded_file else "unknown",
                        source_lang_code, target_lang_code,
                        False, str(e)
                    )
        elif not uploaded_file:
            st.info("👈 Upload a document to see translation results here")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>Built with ❤️ using Streamlit | Supports English, Hindi, Marathi & Sanskrit</p>
        <p><small>⚠️ Note: Sanskrit support may be limited depending on translation backend</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
