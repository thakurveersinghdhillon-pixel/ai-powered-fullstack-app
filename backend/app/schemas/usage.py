import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AIUsageRecordBase(BaseModel):
    provider: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    input_tokens: int = Field(0, ge=0)
    output_tokens: int = Field(0, ge=0)
    total_tokens: int = Field(0, ge=0)
    latency_ms: Optional[int] = Field(None, ge=0)
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    execution_status: str = Field("success", max_length=50)


class AIUsageRecordCreate(AIUsageRecordBase):
    user_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    message_id: Optional[uuid.UUID] = None


class AIUsageRecordResponse(AIUsageRecordBase):
    id: uuid.UUID
    user_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    message_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
