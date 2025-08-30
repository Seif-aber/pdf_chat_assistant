"""Embed a PDF file in the Streamlit UI (base64 iframe fallback)."""
import streamlit as st
import base64
import os
from PyPDF2 import PdfReader  

class PdfViewer:
    """Display a PDF document inside the app."""

    def display_pdf(self, pdf_path: str) -> None:
        """
        Render only the PDF iframe (metrics removed).

        Args:
            pdf_path: Path to local PDF file.
        """
        try:
            self._iframe(pdf_path)
        except Exception as e:
            st.error(f"PDF preview error: {e}")

    def _iframe(self, pdf_path: str) -> None:
        """
        Create a base64 iframe embed.

        Args:
            pdf_path: Path to PDF.
        """
        try:
            with open(pdf_path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("utf-8")
            html = f"""
            <div style="width:100%; height:600px; border:1px solid #ddd; border-radius:4px; overflow:hidden;">
              <iframe src="data:application/pdf;base64,{b64}" width="100%" height="100%" style="border:none;"></iframe>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            st.download_button("📥 Download PDF", data, file_name=os.path.basename(pdf_path), mime="application/pdf")
        except Exception as e:
            st.warning(f"Inline PDF display failed: {e}")

    def _info(self, pdf_path: str) -> dict:
        """
        Collect minimal PDF info (retained for potential future use).

        Args:
            pdf_path: Path to PDF.

        Returns:
            Dict with num_pages & encrypted flag.
        """
        try:
            reader = PdfReader(pdf_path)
            return {"num_pages": len(reader.pages), "encrypted": reader.is_encrypted}
        except Exception:
            return {"num_pages": 0, "encrypted": False}