
# 🌍 NLP Document Translator

The **NLP Document Translator** is a Streamlit-based application that allows users to upload documents (PDF, DOCX, TXT), automatically extract the text, detect the language, and translate it into another language.  
It supports **Hindi, Marathi, Sanskrit, and English**, and provides multiple translation backends with fallbacks to ensure reliability.

---

## 🚀 Features
- 📂 Upload and process **PDF, DOCX, TXT** documents.  
- 🔎 Automatic **language detection** with `langdetect`.  
- 🌐 Multiple translation backends with fallbacks:
  - Google Translator
  - Microsoft Translator
  - Libre Translator
  - MyMemory Translator  
- ✂️ Smart **chunking system** for handling large documents.  
- 📑 Download translated results as **TXT or PDF**.  
- 📝 Logging of translations for debugging and monitoring.  
- 🎨 User-friendly **Streamlit interface**.

---

## 🛠️ Technologies & Libraries Used

### Core NLP & Translation
- **[deep-translator](https://github.com/nidhaloff/deep-translator)** → Provides access to Google, Microsoft, Libre, and MyMemory translators.
- **[langdetect](https://pypi.org/project/langdetect/)** → Detects source language.
- **[nltk](https://www.nltk.org/)** → For sentence splitting during chunking.

### Document Processing
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** → PDF text extraction.
- **[pypdf](https://pypdf.readthedocs.io/)** → Backup PDF text extractor.
- **[python-docx](https://python-docx.readthedocs.io/)** → DOCX text extraction.
- **[docx2python](https://github.com/shaypal5/docx2python)** → Alternative DOCX extractor.

### Output Generation
- **[fpdf](https://pyfpdf.readthedocs.io/)** → Create translated PDF downloads.

### Web App
- **[Streamlit](https://streamlit.io/)** → Frontend for uploading, previewing, and downloading.

### Utilities
- **hashlib, tempfile, pathlib** → File handling and hashing.
- **logging** → Translation logs.

---

## 📂 Project Structure

```

nlp-document-translator/
├── app.py                     # Main Streamlit application
├── config.py                  # Global configuration (languages, backends, limits)
├── requirements.txt           # Python dependencies
├── environment.yml            # Conda environment file
├── README.md                  # Project documentation
├── setup.py                   # Setup script (env + deps installation)
├── run.bat                    # Windows run script
├── run.sh                     # Linux/Mac run script
├── test_installation.py       # Test environment installation
├── src/
│   ├── __init__.py
│   ├── document_processor.py  # Handles PDF/DOCX/TXT text extraction
│   ├── translator.py          # Translation pipeline & language detection
│   └── utils.py               # File utils, PDF creator, logging manager
├── static/
│   └── uploads/               # Uploaded files stored here
├── output/
│   └── translated_documents/  # Translated output stored here
└── sample_documents/
└── sample.txt             # Example input document

````

---

## 📖 File-by-File Explanation

- **`app.py`** → Entry point. Streamlit app where users upload files, select source/target languages, and download translated results.  
- **`config.py`** → Centralized configuration for supported languages, backends, file size limits, and default settings.  
- **`requirements.txt`** → Python dependencies for the project.  
- **`environment.yml`** → Conda environment specification (Python 3.10 + dependencies).  
- **`setup.py`** → Automates environment setup and installation.  
- **`run.bat` / `run.sh`** → Shortcuts to run the app on Windows/Linux.  
- **`test_installation.py`** → Quick test to check installation and dependency setup.  

### Inside `src/`
- **`document_processor.py`**  
  - Extracts text from PDF (PyMuPDF / PyPDF), DOCX (python-docx / docx2python), and TXT files.  
  - Handles encoding issues.  
  - Provides file metadata (page count, paragraphs, extraction method).  

- **`translator.py`**  
  - Detects source language (`langdetect`).  
  - Splits large text into **chunks** (default: 5000 chars).  
  - Uses **deep-translator** to translate each chunk.  
  - Supports multiple backends (Google, Microsoft, Libre, MyMemory) with automatic fallback.  

- **`utils.py`**  
  - File validation (size, extension, content).  
  - Temporary file management (save/delete).  
  - Create **translated PDFs** via FPDF.  
  - Logging system (`LogManager`) for tracking translations.  
  - Helper functions (clean filenames, truncate previews, language name display with emoji).  

---

## ⚡ Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/chilliflex/nlp-document-translator.git
cd nlp-document-translator
````

### 2. Create Conda environment

```bash
conda create -p venv python=3.10
conda activate ./venv
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 🧪 Example Workflow

1. Upload a **Hindi PDF**.
2. System detects language → `"hi"` (Hindi).
3. Select **target language** → `"en"` (English).
4. Text is chunked, translated via Google Translator (fallback to Microsoft if needed).
5. Download result as **English PDF or TXT**.

---

## 📊 Translation Backends

* **Google Translator** → Default & most reliable.
* **Microsoft Translator** → Alternative with good Indic support.
* **Libre Translator** → Free/open-source, slower.
* **MyMemory Translator** → Backup option.

---

## ✨ Future Improvements

* Add support for more Indic languages (Bengali, Tamil, Telugu, etc.).
* Integrate OCR for scanned PDFs.
* Improve UI with side-by-side translation preview.
* GPU-based translation (using HuggingFace Transformers).

---

