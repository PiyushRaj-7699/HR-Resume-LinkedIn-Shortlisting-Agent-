"""
File reader utilities for extracting text from PDF and DOCX resume files.
"""

import logging
import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract plain text from a PDF file using PyMuPDF.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string. Returns empty string if extraction fails.
    """
    try:
        pdf = fitz.open(file_path)
        text = ""
        for page in pdf:
            text += page.get_text()
        pdf.close()
        return text
    except Exception as e:
        logger.warning(f"Failed to extract text from PDF {file_path}: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract plain text from a DOCX file using python-docx.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        Extracted text as a string with paragraphs separated by newlines.
        Returns empty string if extraction fails.
    """
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.warning(f"Failed to extract text from DOCX {file_path}: {e}")
        return ""


def extract_text(file_path: str) -> str:
    """
    Extract text from a resume file (PDF or DOCX).

    Args:
        file_path: Path to the resume file.

    Returns:
        Extracted text as a string.

    Raises:
        ValueError: If the file format is not supported (must be .pdf or .docx).
    """
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format. Supported formats: .pdf, .docx. Received: {file_path}")
