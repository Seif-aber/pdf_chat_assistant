import sys
import os
from typing import List, Dict, Optional, Iterator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.embedding_service import EmbeddingService
from src.services.gemini_client import GeminiClient

class RAGService:
    """Combine retrieval + generation workflow."""

    def __init__(self, embedding_service: EmbeddingService, gemini_client: GeminiClient) -> None:
        """
        Init RAG service.

        Args:
            embedding_service: EmbeddingService instance.
            gemini_client: GeminiClient instance.
        """
        self.embedding_service = embedding_service
        self.gemini_client = gemini_client

    def get_response(self, user_query: str, pdf_id: str, chat_history: Optional[List[Dict]] = None) -> str:
        """
        Retrieve context & generate answer.

        Args:
            user_query: User question.
            pdf_id: PDF identifier.
            chat_history: Prior messages.

        Returns:
            Assistant answer text.
        """
        chunks = self.embedding_service.find_similar_chunks(user_query, pdf_id=pdf_id, top_k=3)
        context = self._format_context(chunks)
        return self.gemini_client.generate_response(user_query, context=context, chat_history=chat_history)

    def stream_response(self, user_query: str, pdf_id: str, chat_history: Optional[List[Dict]] = None) -> Iterator[str]:
        """
        Retrieve context then stream model output.
        """
        chunks = self.embedding_service.find_similar_chunks(user_query, pdf_id=pdf_id, top_k=3)
        context = self._format_context(chunks)
        return self.gemini_client.stream_response(user_query, context=context, chat_history=chat_history)

    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks for prompt.

        Args:
            chunks: Retrieval result list.

        Returns:
            Joined context string.
        """
        if not chunks:
            return ""
        lines: List[str] = []
        for idx, c in enumerate(chunks, start=1):
            if c.get("similarity", 0) > 0.05:
                lines.append(f"[Chunk {idx} sim={c['similarity']:.2f}]\n{c.get('text','')}")
        return "\n\n".join(lines)
    
    def retrieve_relevant_chunks(self, user_prompt: str, pdf_id: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant chunks based on user prompt
        """
        return self.embedding_service.find_similar_chunks(
            query=user_prompt,
            pdf_id=pdf_id,
            top_k=top_k
        )
    
    def generate_response_with_sources(self, user_query: str, pdf_id: str, chat_history: List[Dict] = None) -> Dict:
        """
        Generate response with source information
        """
        try:
            # Retrieve relevant chunks
            relevant_chunks = self.retrieve_relevant_chunks(user_query, pdf_id)
            
            # Prepare context
            context = self._format_context(relevant_chunks)
            
            # Generate response
            response = self.gemini_client.generate_response(
                prompt=user_query,
                context=context,
                chat_history=chat_history
            )
            
            return {
                "response": response,
                "sources": relevant_chunks,
                "context_used": context
            }
            
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "sources": [],
                "context_used": ""
            }