"""API endpoints for message management."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.messages import (
    AcknowledgeMessageResponse,
    MarkMessageReadResponse,
    Message,
    MessageCreate,
    MessageStats,
    MessageSummary,
    MessageUpdate,
    MessageWithComputedFields,
    ThreadDetail,
    ThreadMessage,
    UnreadMessageCount,
)
from app.models.message import MessageStatus, MessageType
from app.models.user import User
from app.services.message_service import MessageService

router = APIRouter()


# ============================================================================
# CRUD Endpoints
# ============================================================================


@router.get("/inbox", response_model=PaginatedResponse[MessageSummary])
async def list_inbox_messages(
    status: Optional[MessageStatus] = None,
    message_type: Optional[MessageType] = None,
    unread_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get inbox messages for current user."""
    service = MessageService(db, current_user.practice_id)
    messages, total = await service.list_inbox_messages(
        user_id=current_user.id,
        status=status,
        message_type=message_type,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )

    # Convert to summary
    message_summaries = [
        MessageSummary(
            id=m.id,
            message_type=m.message_type,
            priority=m.priority,
            subject=m.subject,
            body=m.body,
            sender_id=m.sender_id,
            recipient_user_id=m.recipient_user_id,
            recipient_patient_id=m.recipient_patient_id,
            status=m.status,
            is_read=m.is_read,
            created_at=m.created_at,
        )
        for m in messages
    ]

    return PaginatedResponse(
        items=message_summaries,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/sent", response_model=PaginatedResponse[MessageSummary])
async def list_sent_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get sent messages for current user."""
    service = MessageService(db, current_user.practice_id)
    messages, total = await service.list_sent_messages(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    message_summaries = [
        MessageSummary(
            id=m.id,
            message_type=m.message_type,
            priority=m.priority,
            subject=m.subject,
            body=m.body,
            sender_id=m.sender_id,
            recipient_user_id=m.recipient_user_id,
            recipient_patient_id=m.recipient_patient_id,
            status=m.status,
            is_read=m.is_read,
            created_at=m.created_at,
        )
        for m in messages
    ]

    return PaginatedResponse(
        items=message_summaries,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post("/", response_model=Message, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_in: MessageCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create and send a new message."""
    service = MessageService(db, current_user.practice_id)

    try:
        message = await service.create_message(message_in, sender_id=current_user.id)
        await db.commit()
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{message_id}", response_model=MessageWithComputedFields)
async def get_message(
    message_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific message by ID."""
    service = MessageService(db, current_user.practice_id)
    message = await service.get_message(message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify access (sender or recipient)
    if message.sender_id != current_user.id and message.recipient_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return MessageWithComputedFields(
        **message.__dict__,
        is_read=message.is_read,
        is_delivered=message.is_delivered,
        is_acknowledged=message.is_acknowledged,
    )


@router.patch("/{message_id}", response_model=Message)
async def update_message(
    message_id: UUID,
    message_in: MessageUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update message."""
    service = MessageService(db, current_user.practice_id)
    message = await service.get_message(message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only sender can update
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only sender can update message")

    message = await service.update_message(message_id, message_in)
    await db.commit()
    return message


@router.delete("/{message_id}", response_model=SuccessResponse)
async def delete_message(
    message_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a message (soft delete)."""
    service = MessageService(db, current_user.practice_id)
    message = await service.get_message(message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only sender can delete
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only sender can delete message")

    deleted = await service.delete_message(message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")

    await db.commit()
    return SuccessResponse(message="Message deleted successfully")


# ============================================================================
# Action Endpoints
# ============================================================================


@router.post("/{message_id}/read", response_model=MarkMessageReadResponse)
async def mark_message_as_read(
    message_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark message as read."""
    service = MessageService(db, current_user.practice_id)
    message = await service.get_message(message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only recipient can mark as read
    if message.recipient_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only recipient can mark as read")

    message = await service.mark_as_read(message_id, current_user.id)
    await db.commit()

    return MarkMessageReadResponse(
        message_id=message.id,
        status=message.status,
        read_at=message.read_at,
    )


@router.post("/{message_id}/acknowledge", response_model=AcknowledgeMessageResponse)
async def acknowledge_message(
    message_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Acknowledge a message that requires acknowledgment."""
    service = MessageService(db, current_user.practice_id)
    message = await service.get_message(message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only recipient can acknowledge
    if message.recipient_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only recipient can acknowledge")

    try:
        message = await service.acknowledge_message(message_id, current_user.id)
        await db.commit()

        return AcknowledgeMessageResponse(
            message_id=message.id,
            status=message.status,
            acknowledged_at=message.acknowledged_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Thread Endpoints
# ============================================================================


@router.get("/threads/{thread_id}/messages", response_model=PaginatedResponse[Message])
async def get_thread_messages(
    thread_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all messages in a thread."""
    service = MessageService(db, current_user.practice_id)
    messages, total = await service.get_thread_messages(thread_id, skip, limit)

    return PaginatedResponse(
        items=messages,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/threads", response_model=list[dict])
async def list_user_threads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all message threads for current user."""
    service = MessageService(db, current_user.practice_id)
    threads = await service.get_user_threads(current_user.id, skip, limit)
    return threads


# ============================================================================
# Query Endpoints
# ============================================================================


@router.get("/patients/{patient_id}/messages", response_model=PaginatedResponse[Message])
async def get_patient_messages(
    patient_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all messages related to a patient."""
    service = MessageService(db, current_user.practice_id)
    messages, total = await service.get_patient_messages(patient_id, skip, limit)

    return PaginatedResponse(
        items=messages,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/appointments/{appointment_id}/messages", response_model=list[Message])
async def get_appointment_messages(
    appointment_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all messages for an appointment."""
    service = MessageService(db, current_user.practice_id)
    messages = await service.get_appointment_messages(appointment_id)
    return messages


# ============================================================================
# Statistics Endpoints
# ============================================================================


@router.get("/stats/unread-count", response_model=UnreadMessageCount)
async def get_unread_count(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get count of unread messages."""
    service = MessageService(db, current_user.practice_id)
    count = await service.get_unread_count(current_user.id)

    return UnreadMessageCount(
        user_id=current_user.id,
        unread_count=count,
    )


@router.get("/stats/summary", response_model=MessageStats)
async def get_message_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get message statistics for current user."""
    service = MessageService(db, current_user.practice_id)
    stats = await service.get_message_stats(current_user.id)

    return MessageStats(
        total_sent=stats["total_sent"],
        total_received=stats["total_received"],
        unread_count=stats["unread_count"],
        pending_acknowledgment=stats["pending_acknowledgment"],
    )
