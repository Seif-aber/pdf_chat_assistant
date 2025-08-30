"""Streamlit component: PDF file uploader."""
import streamlit as st
from typing import Optional

UploadedFile = "UploadedFile"  

class FileUploader:
    """Encapsulates upload widget usage."""

    def __init__(self) -> None:
        """Initialize with no uploaded file."""
        self.uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None

    def upload_file(self) -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
        """
        Render uploader and return uploaded file.
        """
        self.uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if self.uploaded_file:
            return self.uploaded_file
        return None

    def get_file_content(self) -> Optional[bytes]:
        """
        Return raw bytes of uploaded file.
        """
        return self.uploaded_file.getvalue() if self.uploaded_file else None