# extractor.py
import fitz  # PyMuPDF

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text
