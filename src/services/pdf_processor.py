import sys
import os
from typing import List, Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from PyPDF2 import PdfReader
except ImportError:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Error: PDF reading library not found. Please install PyPDF2 or pypdf.")
        PdfReader = None

from src.utils.chunking import chunk_pdf_text, clean_text
from config.settings import Config

class PDFProcessor:
    """Process PDFs into cleaned text chunks."""

    def __init__(self, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> None:
        """
        Initialize processor with chunk parameters.

        Args:
            chunk_size: Characters per chunk (defaults to config).
            overlap: Overlap between chunks (defaults to config).
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.overlap = overlap or Config.CHUNK_OVERLAP

    def process_pdf(self, file_path: str) -> List[str]:
        """
        Read PDF, extract text, clean, and chunk.

        Args:
            file_path: Path to PDF.

        Returns:
            List of chunk strings.
        """
        raw = self._extract_text(file_path)
        if not raw.strip():
            return []
        cleaned = clean_text(raw)
        chunks = chunk_pdf_text(cleaned, self.chunk_size, self.overlap)
        return [c for c in chunks if len(c.strip()) > 50]

    def get_pdf_info(self, file_path: str) -> Dict:
        """
        Retrieve simple info (pages, metadata, encryption).

        Args:
            file_path: Path to PDF.

        Returns:
            Dict of info.
        """
        try:
            reader = PdfReader(file_path)
            return {
                "num_pages": len(reader.pages),
                "metadata": reader.metadata,
                "encrypted": reader.is_encrypted,
            }
        except Exception as e:
            print(f"[PDFProcessor] Info error: {e}")
            return {}

    def _extract_text(self, file_path: str) -> str:
        """
        Extract text from all pages.

        Args:
            file_path: Path to PDF.

        Returns:
            Concatenated text with page separators.
        """
        try:
            reader = PdfReader(file_path)
            out: List[str] = []
            for idx, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        out.append(f"\n--- Page {idx+1} ---\n{text}")
                except Exception as pe:
                    print(f"[PDFProcessor] Page {idx+1} extraction failed: {pe}")
            return "".join(out)
        except Exception as e:
            print(f"[PDFProcessor] Read error: {e}")
            return ""