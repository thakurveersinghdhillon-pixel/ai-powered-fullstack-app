import json
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.usage import AIUsageRecord
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse,
)
from app.schemas.message import (
    ClientMessageCreate,
    StreamMessageRequest,
    MessageResponse,
    MessageListResponse,
)
from app.services.llm import get_llm_provider, LLMMessage

router = APIRouter(prefix="/conversations", tags=["Conversations & Messages"])


def format_sse(event: str, data: dict) -> str:
    """Formats an SSE payload according to W3C Server-Sent Events standard."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# --- Conversation Endpoints ---

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new conversation owned by the authenticated user."""
    conv = Conversation(
        user_id=current_user.id,
        title=payload.title.strip(),
    )
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists the authenticated user's conversations with deterministic pagination."""
    count_query = select(func.count()).select_from(Conversation).where(
        Conversation.user_id == current_user.id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return ConversationListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a single conversation owned by the authenticated user."""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    result = await db.execute(query)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return conv


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates the title of a conversation owned by the authenticated user."""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    result = await db.execute(query)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if payload.title is not None:
        conv.title = payload.title.strip()
        conv.updated_at = func.now()
        await db.flush()
        await db.refresh(conv)

    return conv


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a conversation and its associated messages."""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    result = await db.execute(query)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    await db.delete(conv)
    await db.flush()
    return None


# --- Message & Streaming Endpoints ---

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: uuid.UUID,
    payload: ClientMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Saves a user message under a conversation owned by the authenticated user."""
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    conv_result = await db.execute(conv_query)
    conv = conv_result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    msg = Message(
        conversation_id=conversation_id,
        role=payload.role,
        content=payload.content.strip(),
        structured_output=payload.structured_output,
    )
    db.add(msg)
    
    conv.updated_at = func.now()
    await db.flush()
    await db.refresh(msg)
    return msg


@router.post("/{conversation_id}/messages/stream")
async def stream_message_response(
    conversation_id: uuid.UUID,
    payload: StreamMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Streams AI tokens via Server-Sent Events (SSE), persisting the user message first
    and saving completed assistant responses upon stream finalization.
    """
    # 1. Verify conversation ownership
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    conv_result = await db.execute(conv_query)
    conv = conv_result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # 2. Persist user message first
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=payload.content.strip(),
    )
    db.add(user_msg)
    conv.updated_at = func.now()
    await db.flush()

    user_msg_id = user_msg.id
    assistant_msg_id = uuid.uuid4()

    # 3. Fetch conversation history for LLM context
    history_query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    history_result = await db.execute(history_query)
    history_msgs = [
        LLMMessage(role=m.role, content=m.content)
        for m in history_result.scalars().all()
    ]

    llm_provider = get_llm_provider(model_override=payload.model)

    async def event_generator():
        yield format_sse("start", {
            "user_message_id": str(user_msg_id),
            "assistant_message_id": str(assistant_msg_id),
            "conversation_id": str(conversation_id),
        })

        accumulated_text = ""
        usage_data = None
        structured_data = None

        try:
            async for chunk in llm_provider.generate_stream(
                messages=history_msgs,
                system_prompt=payload.system_prompt,
                model=payload.model,
            ):
                if chunk.error:
                    yield format_sse("error", {"error": chunk.error, "code": "PROVIDER_ERROR"})
                    return

                if chunk.content:
                    accumulated_text += chunk.content
                    yield format_sse("token", {"content": chunk.content})

                if chunk.is_done:
                    usage_data = chunk.usage
                    structured_data = chunk.structured_output
                    break

            yield format_sse("metadata", {
                "provider": llm_provider.provider_name,
                "model": payload.model or llm_provider.default_model,
                "usage": usage_data,
                "structured_output": structured_data,
            })
            yield format_sse("done", {
                "status": "completed",
                "assistant_message_id": str(assistant_msg_id),
            })

            # Save completed assistant response and usage metadata
            asst_msg = Message(
                id=assistant_msg_id,
                conversation_id=conversation_id,
                role="assistant",
                content=accumulated_text,
                structured_output=structured_data,
            )
            db.add(asst_msg)

            if usage_data:
                usage_rec = AIUsageRecord(
                    user_id=current_user.id,
                    conversation_id=conversation_id,
                    message_id=assistant_msg_id,
                    provider=llm_provider.provider_name,
                    model=payload.model or llm_provider.default_model,
                    input_tokens=usage_data.get("prompt_tokens", 0),
                    output_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                    execution_status="success",
                )
                db.add(usage_rec)

            await db.commit()

        except Exception as err:
            await db.rollback()
            yield format_sse("error", {"error": str(err), "code": "STREAM_FAILURE"})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def list_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves paginated message history for a conversation owned by the authenticated user."""
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    conv_result = await db.execute(conv_query)
    conv = conv_result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    count_query = select(func.count()).select_from(Message).where(
        Message.conversation_id == conversation_id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    msg_query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .limit(limit)
        .offset(offset)
    )
    msg_result = await db.execute(msg_query)
    items = msg_result.scalars().all()

    return MessageListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{conversation_id}/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves an individual message from a conversation owned by the authenticated user."""
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    conv_result = await db.execute(conv_query)
    conv = conv_result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    msg_query = select(Message).where(
        Message.id == message_id,
        Message.conversation_id == conversation_id,
    )
    msg_result = await db.execute(msg_query)
    msg = msg_result.scalar_one_or_none()

    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    return msg
