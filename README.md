# DocX English Remover

A Django web app that removes English paragraphs from `.docx` files.

## Local Setup

### 1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the development server
```bash
python manage.py runserver
```

### 4. Open in browser
Go to: http://127.0.0.1:8000

## How it works
- Upload a `.docx` file
- The app reads each paragraph and detects its language using `langdetect`
- English paragraphs are removed
- Short paragraphs under ~20 characters are kept (too short to detect reliably)
- Download the cleaned file

## Notes
- Short snippets like "Ah!" cannot be reliably language-detected and are kept by default
- Paragraph structure is preserved (empty paragraphs remain as blank lines)
