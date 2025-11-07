"""Pydantic schemas for notifications."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)


# ============================================================================
# Base Schemas
# ============================================================================


class NotificationBase(BaseModel):
    """Base notification schema."""

    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: list[NotificationChannel] = Field(..., min_length=1)
    title: str = Field(..., max_length=255)
    body: str
    action_url: Optional[str] = Field(None, max_length=500)
    user_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    message_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    claim_id: Optional[UUID] = None
    scheduled_for: Optional[str] = None
    expires_at: Optional[str] = None
    max_retries: int = Field(3, ge=0, le=10)
    metadata: Optional[dict] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""

    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""

    status: Optional[NotificationStatus] = None
    metadata: Optional[dict] = None


# ============================================================================
# Response Schemas
# ============================================================================


class Notification(NotificationBase):
    """Complete notification schema."""

    id: UUID
    practice_id: UUID
    status: NotificationStatus
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    read_at: Optional[str] = None
    failed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    delivery_attempts: Optional[dict] = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class NotificationWithComputedFields(Notification):
    """Notification with computed properties."""

    is_sent: bool
    is_delivered: bool
    is_read: bool
    is_expired: bool
    can_retry: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Action Schemas
# ============================================================================


class MarkNotificationReadRequest(BaseModel):
    """Request to mark notification as read."""

    pass


class MarkNotificationReadResponse(BaseModel):
    """Response after marking notification as read."""

    notification_id: UUID
    status: NotificationStatus
    read_at: Optional[str]
    message: str = "Notification marked as read"


class SendNotificationRequest(BaseModel):
    """Request to send a notification immediately."""

    pass


class SendNotificationResponse(BaseModel):
    """Response after sending notification."""

    notification_id: UUID
    status: NotificationStatus
    sent_at: Optional[str]
    delivered_at: Optional[str]
    message: str


class RetryNotificationRequest(BaseModel):
    """Request to retry failed notification."""

    pass


class RetryNotificationResponse(BaseModel):
    """Response after retrying notification."""

    notification_id: UUID
    status: NotificationStatus
    retry_count: int
    message: str


# ============================================================================
# Delivery Schemas
# ============================================================================


class DeliveryStatus(BaseModel):
    """Delivery status for a specific channel."""

    channel: NotificationChannel
    status: NotificationStatus
    sent_at: Optional[str]
    delivered_at: Optional[str]
    error_message: Optional[str]


class NotificationDeliveryReport(BaseModel):
    """Detailed delivery report."""

    notification_id: UUID
    overall_status: NotificationStatus
    channels: list[DeliveryStatus]
    retry_count: int
    max_retries: int


# ============================================================================
# Preferences Schemas
# ============================================================================


class NotificationPreferences(BaseModel):
    """User notification preferences."""

    user_id: UUID
    enabled_channels: list[NotificationChannel]
    enabled_types: list[NotificationType]
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    timezone: str = "UTC"


class UpdateNotificationPreferencesRequest(BaseModel):
    """Request to update notification preferences."""

    enabled_channels: Optional[list[NotificationChannel]] = None
    enabled_types: Optional[list[NotificationType]] = None
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    timezone: Optional[str] = None


# ============================================================================
# Query Schemas
# ============================================================================


class NotificationSummary(BaseModel):
    """Summary of notification for listings."""

    id: UUID
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    body: str
    status: NotificationStatus
    channels: list[NotificationChannel]
    is_read: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class UnreadNotificationCount(BaseModel):
    """Unread notification count."""

    user_id: UUID
    unread_count: int
    by_priority: dict[str, int]


class NotificationStats(BaseModel):
    """Notification statistics."""

    total_sent: int
    total_delivered: int
    total_failed: int
    total_pending: int
    unread_count: int
    by_channel: dict[str, int]
    by_type: dict[str, int]
