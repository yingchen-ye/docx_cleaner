# DocX English Remover

A Django web app that removes English paragraphs from `.docx` files.

## Local Setup

### 1. Create a virtual environment or conda env
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

conda create -n docx_cleaner python=3.11
conda activate docx_cleaner
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the development server
```bash
python manage.py collectstatic --no-input
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


## Render

The app is served on Render web service.

If you need to reproduce the creation, you need in `.env`:

```
SECRET_KEY=replace-this-with-a-random-secret-key
DEBUG=False
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
```

You can create the key by:
```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- The build command:`./build.sh`
- Start command=: `gunicorn docx_cleaner.wsgi:application`
