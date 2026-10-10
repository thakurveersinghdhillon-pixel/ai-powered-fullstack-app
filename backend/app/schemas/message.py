import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Role must be one of 'user', 'assistant', or 'system'"
    )
    content: str = Field(..., min_length=1, max_length=10000, description="Text content of the message")
    structured_output: Optional[Dict[str, Any]] = Field(
        None, description="Optional structured JSON output"
    )


class ClientMessageCreate(BaseModel):
    role: Literal["user"] = Field(
        "user", description="Client message endpoint requires role='user'"
    )
    content: str = Field(..., min_length=1, max_length=10000, description="Message prompt content")
    structured_output: Optional[Dict[str, Any]] = Field(
        None, description="Optional structured JSON data"
    )


class MessageCreate(MessageBase):
    conversation_id: uuid.UUID


class MessageResponse(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
