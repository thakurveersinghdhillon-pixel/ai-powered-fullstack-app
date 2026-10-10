import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.usage import AIUsageRecord

VALID_MESSAGE_ROLES = ("user", "assistant", "system")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            f"role IN ('user', 'assistant', 'system')",
            name="check_valid_message_role",
        ),
    )

    # Relationships with selectin lazy loading for Async SQLAlchemy
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages", lazy="selectin"
    )
    usage_records: Mapped[List["AIUsageRecord"]] = relationship(
        "AIUsageRecord", back_populates="message", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} role={self.role}>"
