"""Message model for secure messaging between users and patients."""

from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class MessageType(str, enum.Enum):
    """Message type enumeration."""

    DIRECT = "direct"  # Direct message between two users
    THREAD = "thread"  # Part of a conversation thread
    APPOINTMENT = "appointment"  # Appointment-related message
    CLINICAL = "clinical"  # Clinical communication
    ADMINISTRATIVE = "administrative"  # Administrative message
    BROADCAST = "broadcast"  # Broadcast to multiple recipients


class MessagePriority(str, enum.Enum):
    """Message priority enumeration."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageStatus(str, enum.Enum):
    """Message status enumeration."""

    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"


class Message(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Secure messaging between users and patients."""

    __tablename__ = "messages"

    # Sender (always a user)
    sender_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who sent the message",
    )

    # Recipient (can be user or patient)
    recipient_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        comment="User recipient",
    )
    recipient_patient_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        index=True,
        comment="Patient recipient",
    )

    # Message details
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.DIRECT, nullable=False, index=True
    )
    priority: Mapped[MessagePriority] = mapped_column(
        Enum(MessagePriority), default=MessagePriority.NORMAL, nullable=False
    )
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus), default=MessageStatus.SENT, nullable=False, index=True
    )

    # Content
    subject: Mapped[str | None] = mapped_column(String(255), comment="Message subject")
    body: Mapped[str] = mapped_column(Text, nullable=False, comment="Message body")

    # Thread/Conversation
    thread_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        index=True,
        comment="Parent message for threading",
    )
    is_thread_starter: Mapped[bool] = mapped_column(
        default=True, comment="Is this the first message in a thread"
    )

    # Related entities
    patient_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        index=True,
        comment="Related patient (for context)",
    )
    appointment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        index=True,
        comment="Related appointment",
    )

    # Read tracking
    read_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when message was read (ISO 8601)"
    )
    delivered_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when message was delivered (ISO 8601)"
    )

    # Security and encryption
    is_encrypted: Mapped[bool] = mapped_column(default=False, comment="Is message encrypted")
    requires_response: Mapped[bool] = mapped_column(
        default=False, comment="Does this message require a response"
    )
    is_urgent: Mapped[bool] = mapped_column(default=False, comment="Is this an urgent message")

    # Attachments
    has_attachments: Mapped[bool] = mapped_column(default=False, comment="Has file attachments")
    attachment_ids: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of document IDs attached to message"
    )

    # Metadata
    tags: Mapped[list | None] = mapped_column(JSONB, comment="Array of tags for organization")
    metadata: Mapped[dict | None] = mapped_column(JSONB, comment="Additional metadata")

    # Expiration (for temporary messages)
    expires_at: Mapped[str | None] = mapped_column(
        String(29), comment="Expiration timestamp (ISO 8601)"
    )

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient_user = relationship(
        "User", foreign_keys=[recipient_user_id], back_populates="received_messages"
    )
    recipient_patient = relationship("Patient")
    patient = relationship("Patient", foreign_keys=[patient_id])
    appointment = relationship("Appointment")
    thread_parent = relationship(
        "Message", remote_side="Message.id", foreign_keys=[thread_id], uselist=False
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, type={self.message_type}, status={self.status})>"

    @property
    def is_read(self) -> bool:
        """Check if message has been read."""
        return self.status == MessageStatus.READ or self.read_at is not None

    @property
    def is_sent(self) -> bool:
        """Check if message has been sent."""
        return self.status in (
            MessageStatus.SENT,
            MessageStatus.DELIVERED,
            MessageStatus.READ,
        )
