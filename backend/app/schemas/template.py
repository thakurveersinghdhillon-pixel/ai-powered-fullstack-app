import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PromptTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Optional description of template purpose")
    template_content: str = Field(..., min_length=1, description="Prompt text template containing placeholders like {{variable}}")
    version: int = Field(1, ge=1, description="Template version number")


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    template_content: Optional[str] = Field(None, min_length=1)
    version: Optional[int] = Field(None, ge=1)


class PromptTemplateResponse(PromptTemplateBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptTemplateListResponse(BaseModel):
    items: List[PromptTemplateResponse]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
