"""Central application configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DOTENV_PATH = _PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=_DOTENV_PATH, override=False)

class Config:
    """Holds application configuration values loaded from .env only (no silent fallbacks)."""

    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str | None = os.getenv("GEMINI_MODEL")
    EMBEDDING_MODEL: str | None = os.getenv("EMBEDDING_MODEL")

    STREAMLIT_PORT: str | None = os.getenv("STREAMLIT_PORT")
    MAX_PDF_SIZE_MB: str | None = os.getenv("MAX_PDF_SIZE_MB")
    CHUNK_SIZE: str | None = os.getenv("CHUNK_SIZE")
    CHUNK_OVERLAP: str | None = os.getenv("CHUNK_OVERLAP")

    UPLOAD_FOLDER: str | None = os.getenv("UPLOAD_FOLDER")
    EMBEDDINGS_FOLDER: str | None = os.getenv("EMBEDDINGS_FOLDER")


    EMBEDDING_STORAGE_PATH: str | None = None

    @classmethod
    def validate(cls) -> None:
        """Validate required variables & finalize derived values."""
        required = {
            "GEMINI_API_KEY": cls.GEMINI_API_KEY,
            "GEMINI_MODEL": cls.GEMINI_MODEL,
            "EMBEDDING_MODEL": cls.EMBEDDING_MODEL,
            "STREAMLIT_PORT": cls.STREAMLIT_PORT,
            "MAX_PDF_SIZE_MB": cls.MAX_PDF_SIZE_MB,
            "CHUNK_SIZE": cls.CHUNK_SIZE,
            "CHUNK_OVERLAP": cls.CHUNK_OVERLAP,
            "UPLOAD_FOLDER": cls.UPLOAD_FOLDER,
            "EMBEDDINGS_FOLDER": cls.EMBEDDINGS_FOLDER,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables in .env: {', '.join(missing)}")


        cls.STREAMLIT_PORT = int(cls.STREAMLIT_PORT)     
        cls.MAX_PDF_SIZE_MB = int(cls.MAX_PDF_SIZE_MB)   
        cls.CHUNK_SIZE = int(cls.CHUNK_SIZE)             
        cls.CHUNK_OVERLAP = int(cls.CHUNK_OVERLAP)       


        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)    
        os.makedirs(cls.EMBEDDINGS_FOLDER, exist_ok=True)


        cls.EMBEDDING_STORAGE_PATH = os.path.join(cls.EMBEDDINGS_FOLDER, "pdf_embeddings.pkl")  # type: ignore