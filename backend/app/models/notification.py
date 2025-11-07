"""Notification model for system notifications and alerts."""

from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class NotificationType(str, enum.Enum):
    """Notification type enumeration."""

    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    MESSAGE_RECEIVED = "message_received"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_REVIEWED = "document_reviewed"
    LAB_RESULT_AVAILABLE = "lab_result_available"
    PRESCRIPTION_READY = "prescription_ready"
    INSURANCE_EXPIRING = "insurance_expiring"
    PAYMENT_DUE = "payment_due"
    PAYMENT_RECEIVED = "payment_received"
    CLAIM_PROCESSED = "claim_processed"
    NOTE_UNSIGNED = "note_unsigned"
    TASK_ASSIGNED = "task_assigned"
    TASK_DUE = "task_due"
    SYSTEM_ALERT = "system_alert"
    CUSTOM = "custom"


class NotificationPriority(str, enum.Enum):
    """Notification priority enumeration."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(str, enum.Enum):
    """Notification delivery channel enumeration."""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, enum.Enum):
    """Notification status enumeration."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    DISMISSED = "dismissed"


class Notification(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """System notifications and alerts."""

    __tablename__ = "notifications"

    # Recipient (user or patient)
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        comment="User recipient",
    )
    patient_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        index=True,
        comment="Patient recipient",
    )

    # Notification details
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False, index=True
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        Enum(NotificationPriority), default=NotificationPriority.NORMAL, nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False, index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Notification title")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="Notification message")

    # Delivery
    channels: Mapped[list] = mapped_column(
        JSONB, nullable=False, comment="Array of delivery channels"
    )

    # Links and actions
    action_url: Mapped[str | None] = mapped_column(
        String(500), comment="URL to navigate to when notification is clicked"
    )
    action_text: Mapped[str | None] = mapped_column(
        String(100), comment="Text for action button"
    )

    # Related entities (for context)
    related_appointment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        comment="Related appointment",
    )
    related_message_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        comment="Related message",
    )
    related_document_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        comment="Related document",
    )
    related_task_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        comment="Related task/workflow ID",
    )

    # Tracking
    read_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when notification was read (ISO 8601)"
    )
    sent_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when notification was sent (ISO 8601)"
    )
    delivered_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when notification was delivered (ISO 8601)"
    )
    dismissed_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when notification was dismissed (ISO 8601)"
    )

    # Scheduling
    scheduled_for: Mapped[str | None] = mapped_column(
        String(29), comment="Scheduled delivery time (ISO 8601)"
    )
    expires_at: Mapped[str | None] = mapped_column(
        String(29), comment="Expiration timestamp (ISO 8601)"
    )

    # Retry logic
    retry_count: Mapped[int] = mapped_column(default=0, comment="Number of delivery attempts")
    max_retries: Mapped[int] = mapped_column(default=3, comment="Maximum retry attempts")
    last_retry_at: Mapped[str | None] = mapped_column(
        String(29), comment="Last retry timestamp (ISO 8601)"
    )
    failure_reason: Mapped[str | None] = mapped_column(
        Text, comment="Reason for delivery failure"
    )

    # Metadata
    metadata: Mapped[dict | None] = mapped_column(
        JSONB, comment="Additional notification metadata"
    )

    # Relationships
    user = relationship("User", back_populates="notifications")
    patient = relationship("Patient")
    related_appointment = relationship("Appointment")
    related_message = relationship("Message")
    related_document = relationship("Document")

    def __repr__(self) -> str:
        return f"<Notification(type={self.notification_type}, status={self.status}, priority={self.priority})>"

    @property
    def is_read(self) -> bool:
        """Check if notification has been read."""
        return self.status == NotificationStatus.READ or self.read_at is not None

    @property
    def is_delivered(self) -> bool:
        """Check if notification has been delivered."""
        return self.status in (
            NotificationStatus.DELIVERED,
            NotificationStatus.READ,
        )

    @property
    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return (
            self.status == NotificationStatus.FAILED
            and self.retry_count < self.max_retries
        )
