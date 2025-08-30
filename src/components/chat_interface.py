"""Scrollable + streaming chat interface."""
import streamlit as st
from typing import List, Dict
import html
import time

_CHAT_CSS = """
<style>
#chat-container {
  height: 520px;
  overflow-y: auto;
  padding: 0.5rem 0.75rem 0.25rem 0.75rem;
  border: 1px solid #e3e3e3;
  border-radius: 10px;
  background: #fafafa;
  scroll-behavior: smooth;
}
.chat-msg { margin: 0 0 14px 0; max-width: 85%; }
.chat-row-user { display:flex; justify-content:flex-end; }
.chat-row-assistant { display:flex; justify-content:flex-start; }
.bubble {
  padding:10px 14px;
  border-radius:14px;
  line-height:1.35;
  font-size:0.93rem;
  box-shadow:0 1px 2px rgba(0,0,0,0.08);
  word-wrap:break-word;
  white-space:pre-wrap;
}
.bubble-user {
  background:linear-gradient(135deg,#4b8df8,#2563eb);
  color:#fff;
  border-bottom-right-radius:4px;
}
.bubble-assistant {
  background:#ffffff;
  border:1px solid #ddd;
  border-bottom-left-radius:4px;
}
.meta {
  font-size:0.6rem;
  opacity:0.55;
  margin-top:4px;
  text-align:right;
  user-select:none;
}
</style>
<script>
function scrollChat(){
  const el = window.parent.document.querySelector('#chat-container');
  if(el){ el.scrollTop = el.scrollHeight; }
}
</script>
"""

class ChatInterface:
    """Renders scrollable chat and supports streaming assistant output."""

    def __init__(self):
        self.chat_history = []

    def render(self, chat_history: List[Dict]) -> None:
        st.markdown(_CHAT_CSS, unsafe_allow_html=True)
        if not chat_history:
            st.info("No messages yet. Ask something about the PDF.")
            return
        st.markdown(self._history_to_html(chat_history), unsafe_allow_html=True)

    def stream_assistant(self, chat_history: List[Dict], stream_iter) -> str:
        """
        Render existing messages then stream new assistant message.
        Returns final assistant text.
        """
        st.markdown(_CHAT_CSS, unsafe_allow_html=True)
        placeholder = st.empty()
        assistant_text = ""
        # Re-render on each chunk for smooth streaming
        for chunk in stream_iter:
            assistant_text += chunk
            merged = chat_history + [{"role": "assistant", "content": assistant_text}]
            placeholder.markdown(self._history_to_html(merged), unsafe_allow_html=True)
            time.sleep(0.03) 
        return assistant_text

    def input_box(self, key: str = "chat_input") -> str:
        return st.text_input(
            "Ask a question:",
            key=key,
            placeholder="Type your question and press Enter...",
            label_visibility="collapsed",
        )

    def add_message(self, role: str, content: str):
        """
        Add a message to chat history
        """
        self.chat_history.append({
            "role": role,
            "content": content
        })

    def clear_chat(self):
        """Clear the chat history"""
        self.chat_history = []

    def _history_to_html(self, history: List[Dict]) -> str:
        rows = []
        for m in history:
            role = m.get("role", "user")
            safe = html.escape(m.get("content", ""))
            row_cls = "chat-row-user" if role == "user" else "chat-row-assistant"
            bub_cls = "bubble bubble-user" if role == "user" else "bubble bubble-assistant"
            label = "You" if role == "user" else "Assistant"
            rows.append(
                f'<div class="{row_cls}"><div class="chat-msg">'
                f'<div class="{bub_cls}">{safe}</div>'
                f'<div class="meta">{label}</div>'
                f'</div></div>'
            )
        return f'<div id="chat-container">{"".join(rows)}</div><script>scrollChat();</script>'