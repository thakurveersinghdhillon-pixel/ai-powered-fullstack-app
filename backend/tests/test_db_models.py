import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.template import PromptTemplate
from app.models.usage import AIUsageRecord


@pytest.mark.asyncio
async def test_user_creation_and_unique_email(db_session):
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="pbkdf2_sha256$hashedpasswordvalue",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    assert user.id is not None
    assert user.email == unique_email
    assert user.password_hash == "pbkdf2_sha256$hashedpasswordvalue"

    # Verify duplicate email fails with IntegrityError
    duplicate_user = User(
        email=unique_email,
        password_hash="anotherhash",
    )
    db_session.add(duplicate_user)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_conversation_and_message_relationship(db_session):
    user = User(
        email=f"user_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Test AI Conversation")
    db_session.add(conv)
    await db_session.flush()

    assert conv.id is not None
    assert conv.user_id == user.id

    # Add messages (user + assistant with structured_output JSONB)
    msg_user = Message(
        conversation_id=conv.id,
        role="user",
        content="What is quantum computing?",
    )
    msg_assistant = Message(
        conversation_id=conv.id,
        role="assistant",
        content="Quantum computing is...",
        structured_output={"topic": "Quantum", "confidence": 0.98, "tags": ["physics", "tech"]},
    )
    db_session.add_all([msg_user, msg_assistant])
    await db_session.flush()

    # Query back conversation with messages
    result = await db_session.execute(
        select(Conversation).where(Conversation.id == conv.id)
    )
    fetched_conv = result.scalar_one()
    assert len(fetched_conv.messages) == 2
    assert fetched_conv.messages[1].structured_output["topic"] == "Quantum"


@pytest.mark.asyncio
async def test_message_role_constraint(db_session):
    user = User(email=f"user_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Invalid Role Conv")
    db_session.add(conv)
    await db_session.flush()

    invalid_msg = Message(
        conversation_id=conv.id,
        role="invalid_role",
        content="Hello",
    )
    db_session.add(invalid_msg)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_prompt_template_model(db_session):
    user = User(email=f"user_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    tmpl = PromptTemplate(
        user_id=user.id,
        name="Summary Template",
        description="Summarizes text into 3 bullet points",
        template_content="Summarize the following text: {{text}}",
        version=1,
    )
    db_session.add(tmpl)
    await db_session.flush()

    assert tmpl.id is not None
    assert tmpl.owner.email == user.email


@pytest.mark.asyncio
async def test_ai_usage_record_model(db_session):
    user = User(email=f"user_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    usage = AIUsageRecord(
        user_id=user.id,
        provider="openai",
        model="gpt-4o",
        input_tokens=150,
        output_tokens=50,
        total_tokens=200,
        latency_ms=320,
        estimated_cost=0.002500,
        execution_status="success",
    )
    db_session.add(usage)
    await db_session.flush()

    assert usage.id is not None
    assert usage.total_tokens == 200
    assert float(usage.estimated_cost) == 0.0025


@pytest.mark.asyncio
async def test_transaction_rollback_on_failure(db_session):
    user = User(email=f"rollback_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    # Attempt adding an invalid record to trigger exception
    invalid_usage = AIUsageRecord(
        user_id=user.id,
        provider="openai",
        model="gpt-4o",
        input_tokens=-10,  # Fails CheckConstraint
    )
    db_session.add(invalid_usage)
    with pytest.raises(IntegrityError):
        await db_session.flush()

    # Rollback transaction cleanly
    await db_session.rollback()

    # Verify session recovers and can execute new valid transaction
    new_user = User(email=f"post_rollback_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(new_user)
    await db_session.flush()
    assert new_user.id is not None
