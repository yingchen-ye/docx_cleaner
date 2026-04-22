import io
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import content_disposition_header
from docx import Document

HAN_RE = re.compile(r'[\u4e00-\u9fff]')
LATIN_RE = re.compile(r'[A-Za-z]')

def classify_paragraph(text: str):
    """
    Classify a paragraph for bilingual EN/ZH documents.

    Returns:
      - 'zh' if it contains Chinese characters
      - 'en' if it has no Chinese chars but contains enough Latin letters
      - 'other' otherwise
    """
    text = text.strip()
    if not text:
        return 'other'

    # Keep anything containing Chinese
    if HAN_RE.search(text):
        return 'zh'

    # If it has Latin letters and no Chinese, treat it as English
    if LATIN_RE.search(text):
        return 'en'

    return 'other'

def delete_paragraph(paragraph):
    """
    Remove a paragraph entirely from the document XML.
    """
    p = paragraph._element
    parent = p.getparent()
    if parent is not None:
        parent.remove(p)


def remove_english_paragraphs(doc):
    """
    Remove English paragraphs from a bilingual EN/ZH .docx.
    Keeps Chinese and unknown paragraphs.
    """
    paragraphs = list(doc.paragraphs)

    stats = {'total': len(paragraphs), 'removed': 0, 'kept': 0}

    # Iterate over a copy because we are deleting from the document
    for para in paragraphs:
        text = para.text.strip()
        kind = classify_paragraph(text)

        if kind == 'en':
            delete_paragraph(para)
            stats['removed'] += 1
        else:
            stats['kept'] += 1

    return doc, stats


def index(request):
    return render(request, 'cleaner/index.html')


@csrf_exempt
def upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    uploaded_file = request.FILES['file']

    if not uploaded_file.name.endswith('.docx'):
        return JsonResponse({'error': 'Only .docx files are supported'}, status=400)

    try:
        file_bytes = uploaded_file.read()
        doc = Document(io.BytesIO(file_bytes))

        cleaned_doc, stats = remove_english_paragraphs(doc)

        output = io.BytesIO()
        cleaned_doc.save(output)
        output.seek(0)

        original_name = uploaded_file.name.rsplit('.', 1)[0]
        download_name = f"{original_name}_cleaned.docx"

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = content_disposition_header(True, download_name)
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        response['X-Stats'] = str(stats)
        return response

    except Exception as e:
        return JsonResponse({'error': f'Failed to process file: {str(e)}'}, status=500)