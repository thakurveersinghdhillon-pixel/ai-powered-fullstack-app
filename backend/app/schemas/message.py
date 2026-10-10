import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Role must be one of 'user', 'assistant', or 'system'"
    )
    content: str = Field(..., min_length=1, description="Text content of the message")
    structured_output: Optional[Dict[str, Any]] = Field(
        None, description="Optional structured JSON output from LLM"
    )


class MessageCreate(MessageBase):
    conversation_id: uuid.UUID


class MessageResponse(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
