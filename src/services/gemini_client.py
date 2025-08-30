import sys
import os
import google.generativeai as genai
from typing import List, Dict, Optional, Iterator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config.settings import Config

class GeminiClient:
    """Generate responses (full or streaming) using Gemini with optional context & history."""

    def __init__(self) -> None:
        """Configure model instance."""
        Config.validate()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    def generate_response(self, prompt: str, context: str = "", chat_history: Optional[List[Dict]] = None) -> str:
        """
        Produce a model response.

        Args:
            prompt: User question.
            context: Retrieved PDF context.
            chat_history: Prior messages list.

        Returns:
            Response string (or error message).
        """
        try:
            full_prompt = self._build_prompt(prompt, context, chat_history)
            resp = self.model.generate_content(full_prompt)
            return getattr(resp, "text", "").strip() or "No response generated."
        except Exception as e:
            return f"Error generating response: {e}"

    def stream_response(self, prompt: str, context: str = "", chat_history: Optional[List[Dict]] = None) -> Iterator[str]:
        """
        Stream model tokens/chunks. Yields incremental text fragments.
        """
        try:
            full_prompt = self._build_prompt(prompt, context, chat_history)
            for chunk in self.model.generate_content(full_prompt, stream=True):
                txt = getattr(chunk, "text", "")
                if txt:
                    yield txt
        except Exception as e:
            yield f"[Error] {e}"

    def _build_prompt(self, user_prompt: str, context: str, chat_history: Optional[List[Dict]]) -> str:
        """
        Construct final prompt sent to LLM.

        Args:
            user_prompt: Current question.
            context: Retrieved context text.
            chat_history: List of previous user/assistant dicts.

        Returns:
            Combined prompt string.
        """
        system = (
            "You are an assistant answering questions about an uploaded PDF. "
            "Base answers only on provided context. If unknown, say you lack the info."
        )
        parts = [system]
        if context:
            parts.append(f"\nContext:\n{context}")
        if chat_history:
            parts.append("\nRecent conversation:")
            for m in chat_history[-5:]:
                role = m.get("role", "user")
                content = m.get("content", "")
                parts.append(f"{role}: {content}")
        parts.append(f"\nQuestion: {user_prompt}\nAnswer:")
        return "\n".join(parts)