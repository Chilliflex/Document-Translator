## Welcome to the NLP Document Translator!

This is a sample document that demonstrates the capabilities of our translation system.

### Key features:
- Support for multiple file formats (PDF, DOCX, TXT)
- Multi-language translation (English, Hindi, Marathi, Sanskrit)
- Automatic language detection
- Multiple translation backends for reliability

You can use this file to test the translation functionality.

### Sample sentences for testing:
1. Good morning, how are you today?
2. The weather is beautiful today.
3. I would like to learn new languages.
4. Technology helps us communicate better.
5. Education is the key to success.

This document contains enough text for the language detection algorithm to work accurately.

### Project Structure
```

nlp-document-translator/
├── app.py
├── config.py
├── requirements.txt
├── environment.yml
├── README.md
├── setup.py
├── run.bat
├── run.sh
├── test_installation.py
├── src/
│   ├── __init__.py
│   ├── document_processor.py
│   ├── translator.py
│   └── utils.py
├── static/
│   └── uploads/
├── output/
│   └── translated_documents/
└── sample_documents/
    └── sample.txt

```
### Create conda environment with Python 3.10
```
conda create -p venv python=3.10
```
### Activate environment
```
conda activate ./venv
```

### Install dependencies
```
pip install -r requirements.txt
```
### Run the application
```
streamlit run app.py

```

