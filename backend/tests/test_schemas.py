import uuid
from datetime import datetime
from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserResponse
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.template import PromptTemplateCreate, PromptTemplateResponse
from app.schemas.usage import AIUsageRecordCreate, AIUsageRecordResponse


def test_user_schema_validation():
    # Valid UserCreate
    user_in = UserCreate(email="user@example.com", password="securepassword123")
    assert user_in.email == "user@example.com"

    # Invalid email fails
    with pytest.raises(ValidationError):
        UserCreate(email="invalid-email", password="securepassword123")

    # Short password fails
    with pytest.raises(ValidationError):
        UserCreate(email="user@example.com", password="short")


def test_user_response_excludes_password_hash():
    user_data = {
        "id": uuid.uuid4(),
        "email": "user@example.com",
        "password_hash": "secret_hash_value_that_must_never_be_leaked",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    res = UserResponse.model_validate(user_data)
    dumped = res.model_dump()
    assert "password_hash" not in dumped
    assert "password" not in dumped
    assert dumped["email"] == "user@example.com"


def test_message_schema_role_validation():
    # Valid roles
    for role in ["user", "assistant", "system"]:
        msg = MessageCreate(
            conversation_id=uuid.uuid4(),
            role=role,
            content="Hello AI",
        )
        assert msg.role == role

    # Invalid role fails
    with pytest.raises(ValidationError):
        MessageCreate(
            conversation_id=uuid.uuid4(),
            role="unsupported_role",
            content="Hello AI",
        )


def test_usage_schema_nonnegative_constraints():
    # Valid record
    rec = AIUsageRecordCreate(
        user_id=uuid.uuid4(),
        provider="openai",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        latency_ms=250,
        estimated_cost=Decimal("0.0015"),
    )
    assert rec.total_tokens == 150

    # Negative tokens fail
    with pytest.raises(ValidationError):
        AIUsageRecordCreate(
            user_id=uuid.uuid4(),
            provider="openai",
            model="gpt-4o",
            input_tokens=-5,
        )

    # Negative cost fails
    with pytest.raises(ValidationError):
        AIUsageRecordCreate(
            user_id=uuid.uuid4(),
            provider="openai",
            model="gpt-4o",
            estimated_cost=Decimal("-0.01"),
        )
