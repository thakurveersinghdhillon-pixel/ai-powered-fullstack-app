import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.template import PromptTemplate
    from app.models.usage import AIUsageRecord
    from app.models.session import RefreshSession


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    templates: Mapped[List["PromptTemplate"]] = relationship(
        "PromptTemplate", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )
    usage_records: Mapped[List["AIUsageRecord"]] = relationship(
        "AIUsageRecord", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    sessions: Mapped[List["RefreshSession"]] = relationship(
        "RefreshSession", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
