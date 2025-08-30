"""Basic text cleaning and fixed-size overlapping chunking utilities."""
from typing import List

def clean_text(text: str) -> str:
    """
    Normalize whitespace in text.

    Args:
        text: Raw text.

    Returns:
        Cleaned single-spaced text.
    """
    return " ".join(text.split())

def chunk_pdf_text(pdf_text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        pdf_text: Full text.
        chunk_size: Max chars per chunk.
        overlap: Overlapping chars between chunks.

    Returns:
        List of chunk strings.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    chunks: List[str] = []
    start = 0
    length = len(pdf_text)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(pdf_text[start:end])
        start += chunk_size - overlap
    return chunks