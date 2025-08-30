from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    user_id: str
    content: str
    timestamp: str

class ChatContext(BaseModel):
    messages: List[Message]
    pdf_id: Optional[str] = None

class UserPrompt(BaseModel):
    user_id: str
    prompt: str
    context: ChatContext

class AssistantResponse(BaseModel):
    response: str
    context: ChatContext
    pdf_id: Optional[str] = None