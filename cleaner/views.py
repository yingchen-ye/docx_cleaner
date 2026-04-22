import io
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from docx import Document
from langdetect import detect, LangDetectException


def is_english(text):
    """
    Returns True if the text is detected as English.
    Short texts (under 20 chars) are skipped — cannot be reliably detected.
    Returns None for short/ambiguous text so the caller can decide what to do.
    """
    text = text.strip()
    if not text:
        return False
    if len(text) < 40:
        # Too short to detect reliably — return None (ambiguous)
        return None
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return None


def remove_english_paragraphs(doc):
    """
    Removes paragraphs detected as English from a Document object.
    Short/ambiguous paragraphs are kept by default.
    Returns (cleaned_doc, stats) where stats is a dict with counts.
    """
    stats = {'total': 0, 'removed': 0, 'kept': 0, 'ambiguous': 0}

    for para in doc.paragraphs:
        stats['total'] += 1
        text = para.text.strip()

        result = is_english(text)

        if result is True:
            # Clear the paragraph content but keep the paragraph node
            # (removing nodes entirely can break document structure)
            for run in para.runs:
                run.text = ''
            stats['removed'] += 1
        elif result is None:
            stats['ambiguous'] += 1
            stats['kept'] += 1
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
        # Read the uploaded file into memory
        file_bytes = uploaded_file.read()
        doc = Document(io.BytesIO(file_bytes))

        # Process the document
        cleaned_doc, stats = remove_english_paragraphs(doc)

        # Save to a BytesIO buffer
        output = io.BytesIO()
        cleaned_doc.save(output)
        output.seek(0)

        # Return the cleaned file as a download
        original_name = uploaded_file.name.rsplit('.', 1)[0]
        download_name = f"{original_name}_cleaned.docx"

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{download_name}"'
        response['X-Stats'] = str(stats)  # Optional: pass stats in header
        return response

    except Exception as e:
        return JsonResponse({'error': f'Failed to process file: {str(e)}'}, status=500)
