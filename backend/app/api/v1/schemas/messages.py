"""Pydantic schemas for messages."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import MessagePriority, MessageStatus, MessageType


# ============================================================================
# Base Schemas
# ============================================================================


class MessageBase(BaseModel):
    """Base message schema."""

    message_type: MessageType = MessageType.DIRECT
    priority: MessagePriority = MessagePriority.NORMAL
    subject: Optional[str] = Field(None, max_length=255)
    body: str = Field(..., min_length=1)
    recipient_user_id: Optional[UUID] = None
    recipient_patient_id: Optional[UUID] = None
    thread_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None
    is_system_message: bool = False
    requires_acknowledgment: bool = False
    is_encrypted: bool = False
    attachment_document_ids: Optional[list[UUID]] = None
    metadata: Optional[dict] = None


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    pass


class MessageUpdate(BaseModel):
    """Schema for updating a message."""

    status: Optional[MessageStatus] = None
    metadata: Optional[dict] = None


# ============================================================================
# Response Schemas
# ============================================================================


class Message(MessageBase):
    """Complete message schema."""

    id: UUID
    practice_id: UUID
    sender_id: Optional[UUID]
    status: MessageStatus
    read_at: Optional[str] = None
    read_by: Optional[UUID] = None
    delivered_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[UUID] = None
    created_at: str
    updated_at: str
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class MessageWithComputedFields(Message):
    """Message with computed properties."""

    is_read: bool
    is_delivered: bool
    is_acknowledged: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Thread Schemas
# ============================================================================


class MessageThread(BaseModel):
    """Message thread summary."""

    thread_id: UUID
    subject: Optional[str]
    message_count: int
    participant_count: int
    last_message_at: str
    unread_count: int


class ThreadMessage(BaseModel):
    """Message in a thread."""

    id: UUID
    sender_id: Optional[UUID]
    body: str
    created_at: str
    read_at: Optional[str]
    is_system_message: bool


class ThreadDetail(BaseModel):
    """Detailed thread information."""

    thread_id: UUID
    subject: Optional[str]
    messages: list[ThreadMessage]
    participants: list[UUID]


# ============================================================================
# Action Schemas
# ============================================================================


class MarkMessageReadRequest(BaseModel):
    """Request to mark message as read."""

    pass


class MarkMessageReadResponse(BaseModel):
    """Response after marking message as read."""

    message_id: UUID
    status: MessageStatus
    read_at: Optional[str]
    message: str = "Message marked as read"


class AcknowledgeMessageRequest(BaseModel):
    """Request to acknowledge a message."""

    pass


class AcknowledgeMessageResponse(BaseModel):
    """Response after acknowledging a message."""

    message_id: UUID
    status: MessageStatus
    acknowledged_at: Optional[str]
    message: str = "Message acknowledged"


# ============================================================================
# Query Schemas
# ============================================================================


class MessageSummary(BaseModel):
    """Summary of message for listings."""

    id: UUID
    message_type: MessageType
    priority: MessagePriority
    subject: Optional[str]
    body: str
    sender_id: Optional[UUID]
    recipient_user_id: Optional[UUID]
    recipient_patient_id: Optional[UUID]
    status: MessageStatus
    is_read: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class UnreadMessageCount(BaseModel):
    """Unread message count."""

    user_id: UUID
    unread_count: int


class MessageStats(BaseModel):
    """Message statistics."""

    total_sent: int
    total_received: int
    unread_count: int
    pending_acknowledgment: int
