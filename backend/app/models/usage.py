import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.conversation import Conversation
    from app.models.message import Message


class AIUsageRecord(Base):
    __tablename__ = "ai_usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True
    )
    execution_status: Mapped[str] = mapped_column(
        String(50), default="success", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("input_tokens >= 0", name="check_input_tokens_nonnegative"),
        CheckConstraint("output_tokens >= 0", name="check_output_tokens_nonnegative"),
        CheckConstraint("total_tokens >= 0", name="check_total_tokens_nonnegative"),
        CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name="check_latency_ms_nonnegative",
        ),
        CheckConstraint(
            "estimated_cost IS NULL OR estimated_cost >= 0",
            name="check_estimated_cost_nonnegative",
        ),
    )

    # Relationships with selectin lazy loading for Async SQLAlchemy
    user: Mapped["User"] = relationship("User", back_populates="usage_records", lazy="selectin")
    conversation: Mapped[Optional["Conversation"]] = relationship(
        "Conversation", back_populates="usage_records", lazy="selectin"
    )
    message: Mapped[Optional["Message"]] = relationship(
        "Message", back_populates="usage_records", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AIUsageRecord id={self.id} model={self.model} total_tokens={self.total_tokens}>"
