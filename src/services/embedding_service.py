"""Generate, store, and query embeddings via Gemini API."""
import numpy as np
import google.generativeai as genai
from typing import List, Dict, Optional
from config.settings import Config
from src.utils.vector_store import VectorStore

class EmbeddingService:
    """Handles embedding generation, storage, and similarity search."""

    def __init__(self) -> None:
        """Configure Gemini and initialize vector store."""
        Config.validate()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.embedding_model = Config.EMBEDDING_MODEL
        self.vector_store = VectorStore(storage_path=Config.EMBEDDING_STORAGE_PATH)

    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Embed a list of document texts.

        Args:
            texts: List of strings.

        Returns:
            List of embedding vectors (np.ndarray).
        """
        embeddings: List[np.ndarray] = []
        for i, text in enumerate(texts):
            try:
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document",
                )
                embeddings.append(np.array(result["embedding"]))
            except Exception as e:
                print(f"[EmbeddingService] Doc embed error idx {i}: {e}")
                embeddings.append(np.zeros(768))
        return embeddings

    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Create an embedding for a query.

        Args:
            query: User query text.

        Returns:
            Query embedding vector.
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query",
            )
            return np.array(result["embedding"])
        except Exception as e:
            print(f"[EmbeddingService] Query embed error: {e}")
            return np.zeros(768)

    def store_pdf_embeddings(self, pdf_id: str, chunks: List[str]) -> None:
        """
        Embed and store all chunks for a PDF (replacing previous).

        Args:
            pdf_id: Unique PDF identifier.
            chunks: List of chunk strings.
        """
        self.clear_pdf_embeddings(pdf_id)
        for idx, (chunk, vec) in enumerate(zip(chunks, self.generate_embeddings(chunks))):
            key = f"{pdf_id}_chunk_{idx}"
            self.vector_store.add_embedding(
                key=key,
                vector=vec.tolist(),
                metadata={"pdf_id": pdf_id, "chunk_index": idx, "text": chunk},
            )

    def find_similar_chunks(self, query: str, pdf_id: Optional[str] = None, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top_k most similar stored chunks.

        Args:
            query: User query string.
            pdf_id: Restrict to given PDF id if set.
            top_k: Number of results.

        Returns:
            List of similarity result dicts.
        """
        q_vec = self.generate_query_embedding(query)
        results = []
        for key in self.vector_store.get_all_embeddings():
            if pdf_id and not key.startswith(f"{pdf_id}_"):
                continue
            data = self.vector_store.get_embedding_data(key)
            if not data:
                continue
            vec = np.array(data["vector"])
            sim = self._cosine_similarity(q_vec, vec)
            md = data.get("metadata", {})
            results.append(
                {
                    "key": key,
                    "similarity": sim,
                    "text": md.get("text", ""),
                    "chunk_index": md.get("chunk_index", 0),
                    "pdf_id": md.get("pdf_id", ""),
                }
            )
        results.sort(key=lambda r: r["similarity"], reverse=True)
        return results[:top_k]

    def clear_pdf_embeddings(self, pdf_id: str) -> None:
        """
        Remove all embeddings tied to a PDF.

        Args:
            pdf_id: Identifier.
        """
        self.vector_store.remove_embeddings_by_prefix(f"{pdf_id}_")

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity.

        Args:
            a: Vector A
            b: Vector B

        Returns:
            Cosine similarity or 0.0 on failure.
        """
        if not a.any() or not b.any():
            return 0.0
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)