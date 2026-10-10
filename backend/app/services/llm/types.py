from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class LLMChunk(BaseModel):
    content: str = ""
    is_done: bool = False
    usage: Optional[Dict[str, int]] = None
    structured_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class LLMResult(BaseModel):
    content: str
    structured_output: Optional[Dict[str, Any]] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str
    provider: str
