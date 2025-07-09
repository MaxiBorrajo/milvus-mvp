from typing import List
import fitz
import docx
import os
import io

def extract_text_from_file(content: bytes, filename: str) -> List[str]:
    ext = os.path.splitext(filename)[-1].lower()
    text = ""

    if ext == ".pdf":
        doc = fitz.open(stream=content, filetype="pdf")
        for page in doc:
            text += page.get_text()
    elif ext == ".txt":
        text = content.decode("utf-8")
    elif ext == ".docx":
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return [frag.strip() for frag in text.split("\n") if frag.strip()]

def split_text_by_paragraph(text: str) -> List[str]:
    return [p.strip() for p in text.split("\n") if p.strip()]