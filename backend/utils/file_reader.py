# utils/file_reader.py
import fitz  # PyMuPDF
import io
import docx
from typing import Optional

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text")
    return text

def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    bio = io.BytesIO(file_bytes)
    doc = docx.Document(bio)
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs)

def extract_text_from_txt_bytes(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")

def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_from_pdf_bytes(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx_bytes(file_bytes)
    elif ext == "txt":
        return extract_text_from_txt_bytes(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
