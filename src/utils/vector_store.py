"""Lightweight on-disk key → embedding store (pickle-based)."""
from __future__ import annotations
from typing import List, Dict, Optional, Any
import pickle
import os

class VectorStore:
    """Persist simple embedding entries (vector + metadata) to a pickle file."""

    def __init__(self, storage_path: str) -> None:
        """
        Initialize the vector store.

        Args:
            storage_path: Path to pickle file used for persistence.
        """
        self.storage_path = storage_path
        self.embeddings: Dict[str, Dict[str, Any]] = {}
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.load_embeddings()

    def load_embeddings(self) -> None:
        """Load embeddings from disk if file exists."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "rb") as f:
                    self.embeddings = pickle.load(f)
            except Exception as e:
                print(f"[VectorStore] Error loading embeddings: {e}")
                self.embeddings = {}

    def save_embeddings(self) -> None:
        """Persist current embeddings to disk."""
        try:
            with open(self.storage_path, "wb") as f:
                pickle.dump(self.embeddings, f)
        except Exception as e:
            print(f"[VectorStore] Error saving embeddings: {e}")

    def add_embedding(self, key: str, vector: List[float], metadata: Optional[Dict] = None) -> None:
        """
        Add or overwrite an embedding entry.

        Args:
            key: Unique identifier (e.g. 'pdf1_chunk_0')
            vector: Embedding vector as list of floats
            metadata: Optional metadata dictionary
        """
        self.embeddings[key] = {"vector": vector, "metadata": metadata or {}}
        self.save_embeddings()

    def get_embedding_data(self, key: str) -> Optional[Dict]:
        """
        Retrieve full embedding entry.

        Args:
            key: Embedding key

        Returns:
            Dict with 'vector' and 'metadata' or None.
        """
        return self.embeddings.get(key)

    def get_embedding_vector(self, key: str) -> Optional[List[float]]:
        """
        Retrieve only the vector.

        Args:
            key: Embedding key

        Returns:
            Vector list or None.
        """
        entry = self.embeddings.get(key)
        return entry["vector"] if entry else None

    def get_all_embeddings(self) -> List[str]:
        """
        List all embedding keys.

        Returns:
            List of keys.
        """
        return list(self.embeddings.keys())

    def clear_embeddings(self) -> None:
        """Remove all embeddings."""
        self.embeddings = {}
        self.save_embeddings()

    def remove_embeddings_by_prefix(self, prefix: str) -> None:
        """
        Remove embeddings whose keys start with prefix.

        Args:
            prefix: Key prefix filter.
        """
        to_remove = [k for k in self.embeddings if k.startswith(prefix)]
        for k in to_remove:
            del self.embeddings[k]
        self.save_embeddings()