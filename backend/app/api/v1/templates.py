import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.template import PromptTemplate
from app.schemas.template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    PromptTemplateListResponse,
)

router = APIRouter(prefix="/templates", tags=["Prompt Templates"])


@router.post("", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: PromptTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates a reusable prompt template owned by the authenticated user."""
    tmpl = PromptTemplate(
        user_id=current_user.id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        template_content=payload.template_content.strip(),
        version=payload.version,
    )
    db.add(tmpl)
    await db.flush()
    await db.refresh(tmpl)
    return tmpl


@router.get("", response_model=PromptTemplateListResponse)
async def list_templates(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists the authenticated user's prompt templates with pagination."""
    count_query = select(func.count()).select_from(PromptTemplate).where(
        PromptTemplate.user_id == current_user.id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = (
        select(PromptTemplate)
        .where(PromptTemplate.user_id == current_user.id)
        .order_by(PromptTemplate.created_at.desc(), PromptTemplate.id.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return PromptTemplateListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{template_id}", response_model=PromptTemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a single prompt template owned by the authenticated user."""
    query = select(PromptTemplate).where(
        PromptTemplate.id == template_id,
        PromptTemplate.user_id == current_user.id,
    )
    result = await db.execute(query)
    tmpl = result.scalar_one_or_none()

    if not tmpl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt template not found",
        )
    return tmpl


@router.patch("/{template_id}", response_model=PromptTemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    payload: PromptTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates a prompt template owned by the authenticated user, automatically incrementing version if content changes."""
    query = select(PromptTemplate).where(
        PromptTemplate.id == template_id,
        PromptTemplate.user_id == current_user.id,
    )
    result = await db.execute(query)
    tmpl = result.scalar_one_or_none()

    if not tmpl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt template not found",
        )

    content_or_name_changed = False

    if payload.name is not None and payload.name.strip() != tmpl.name:
        tmpl.name = payload.name.strip()
        content_or_name_changed = True

    if payload.description is not None:
        tmpl.description = payload.description.strip() if payload.description else None

    if payload.template_content is not None and payload.template_content.strip() != tmpl.template_content:
        tmpl.template_content = payload.template_content.strip()
        content_or_name_changed = True

    if payload.version is not None:
        tmpl.version = payload.version
    elif content_or_name_changed:
        tmpl.version = tmpl.version + 1

    tmpl.updated_at = func.now()
    await db.flush()
    await db.refresh(tmpl)
    return tmpl


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a prompt template owned by the authenticated user."""
    query = select(PromptTemplate).where(
        PromptTemplate.id == template_id,
        PromptTemplate.user_id == current_user.id,
    )
    result = await db.execute(query)
    tmpl = result.scalar_one_or_none()

    if not tmpl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt template not found",
        )

    await db.delete(tmpl)
    await db.flush()
    return None
