"""API endpoints for notification management."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.notifications import (
    MarkNotificationReadResponse,
    Notification,
    NotificationCreate,
    NotificationStats,
    NotificationSummary,
    NotificationUpdate,
    NotificationWithComputedFields,
    RetryNotificationResponse,
    SendNotificationResponse,
    UnreadNotificationCount,
)
from app.models.notification import NotificationStatus, NotificationType
from app.models.user import User
from app.services.notification_service import NotificationService

router = APIRouter()


# ============================================================================
# CRUD Endpoints
# ============================================================================


@router.get("/", response_model=PaginatedResponse[NotificationSummary])
async def list_user_notifications(
    status: Optional[NotificationStatus] = None,
    notification_type: Optional[NotificationType] = None,
    unread_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get notifications for current user."""
    service = NotificationService(db, current_user.practice_id)
    notifications, total = await service.list_user_notifications(
        user_id=current_user.id,
        status=status,
        notification_type=notification_type,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )

    # Convert to summary
    notification_summaries = [
        NotificationSummary(
            id=n.id,
            notification_type=n.notification_type,
            priority=n.priority,
            title=n.title,
            body=n.body,
            status=n.status,
            channels=n.channels,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in notifications
    ]

    return PaginatedResponse(
        items=notification_summaries,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post("/", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_in: NotificationCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new notification."""
    service = NotificationService(db, current_user.practice_id)
    notification = await service.create_notification(notification_in)
    await db.commit()
    return notification


@router.get("/{notification_id}", response_model=NotificationWithComputedFields)
async def get_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific notification by ID."""
    service = NotificationService(db, current_user.practice_id)
    notification = await service.get_notification(notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Verify access
    if notification.user_id and notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return NotificationWithComputedFields(
        **notification.__dict__,
        is_sent=notification.is_sent,
        is_delivered=notification.is_delivered,
        is_read=notification.is_read,
        is_expired=notification.is_expired,
        can_retry=notification.can_retry,
    )


@router.patch("/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: UUID,
    notification_in: NotificationUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update notification."""
    service = NotificationService(db, current_user.practice_id)
    notification = await service.update_notification(notification_id, notification_in)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.commit()
    return notification


@router.delete("/{notification_id}", response_model=SuccessResponse)
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a notification."""
    service = NotificationService(db, current_user.practice_id)
    deleted = await service.delete_notification(notification_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.commit()
    return SuccessResponse(message="Notification deleted successfully")


# ============================================================================
# Action Endpoints
# ============================================================================


@router.post("/{notification_id}/read", response_model=MarkNotificationReadResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark notification as read."""
    service = NotificationService(db, current_user.practice_id)

    try:
        notification = await service.mark_as_read(notification_id, current_user.id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        await db.commit()

        return MarkNotificationReadResponse(
            notification_id=notification.id,
            status=notification.status,
            read_at=notification.read_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/mark-all-read", response_model=SuccessResponse)
async def mark_all_as_read(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark all notifications as read for current user."""
    service = NotificationService(db, current_user.practice_id)
    count = await service.mark_all_as_read(current_user.id)
    await db.commit()

    return SuccessResponse(message=f"Marked {count} notifications as read")


@router.post("/{notification_id}/send", response_model=SendNotificationResponse)
async def send_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Send a notification immediately."""
    service = NotificationService(db, current_user.practice_id)
    notification = await service.send_notification(notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.commit()

    return SendNotificationResponse(
        notification_id=notification.id,
        status=notification.status,
        sent_at=notification.sent_at,
        delivered_at=notification.delivered_at,
        message="Notification sent successfully",
    )


@router.post("/{notification_id}/retry", response_model=RetryNotificationResponse)
async def retry_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retry a failed notification."""
    service = NotificationService(db, current_user.practice_id)

    try:
        notification = await service.retry_notification(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        await db.commit()

        return RetryNotificationResponse(
            notification_id=notification.id,
            status=notification.status,
            retry_count=notification.retry_count,
            message="Notification retry initiated",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Query Endpoints
# ============================================================================


@router.get("/pending", response_model=list[Notification])
async def get_pending_notifications(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get pending notifications ready to be sent."""
    service = NotificationService(db, current_user.practice_id)
    notifications = await service.get_pending_notifications(limit)
    return notifications


@router.get("/failed", response_model=list[Notification])
async def get_failed_notifications(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get failed notifications that can be retried."""
    service = NotificationService(db, current_user.practice_id)
    notifications = await service.get_failed_notifications(limit)
    return notifications


@router.get("/appointments/{appointment_id}/notifications", response_model=list[Notification])
async def get_appointment_notifications(
    appointment_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all notifications for an appointment."""
    service = NotificationService(db, current_user.practice_id)
    notifications = await service.get_appointment_notifications(appointment_id)
    return notifications


@router.get("/patients/{patient_id}/notifications", response_model=PaginatedResponse[Notification])
async def get_patient_notifications(
    patient_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all notifications related to a patient."""
    service = NotificationService(db, current_user.practice_id)
    notifications, total = await service.get_patient_notifications(patient_id, skip, limit)

    return PaginatedResponse(
        items=notifications,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


# ============================================================================
# Statistics Endpoints
# ============================================================================


@router.get("/stats/unread-count", response_model=UnreadNotificationCount)
async def get_unread_count(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get count of unread notifications."""
    service = NotificationService(db, current_user.practice_id)
    count = await service.get_unread_count(current_user.id)

    # Get count by priority
    notifications, _ = await service.list_user_notifications(
        user_id=current_user.id,
        unread_only=True,
        limit=1000,
    )

    by_priority = {}
    for n in notifications:
        priority_key = n.priority.value
        by_priority[priority_key] = by_priority.get(priority_key, 0) + 1

    return UnreadNotificationCount(
        user_id=current_user.id,
        unread_count=count,
        by_priority=by_priority,
    )


@router.get("/stats/summary", response_model=NotificationStats)
async def get_notification_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get notification statistics for current user."""
    service = NotificationService(db, current_user.practice_id)
    stats = await service.get_notification_stats(current_user.id)

    # Channel breakdown (from delivered notifications)
    notifications, _ = await service.list_user_notifications(
        user_id=current_user.id,
        status=NotificationStatus.DELIVERED,
        limit=1000,
    )

    by_channel = {}
    for n in notifications:
        for channel in n.channels:
            channel_key = channel.value if hasattr(channel, 'value') else str(channel)
            by_channel[channel_key] = by_channel.get(channel_key, 0) + 1

    return NotificationStats(
        total_sent=stats["total_sent"],
        total_delivered=stats["total_delivered"],
        total_failed=stats["total_failed"],
        total_pending=stats["total_pending"],
        unread_count=stats["unread_count"],
        by_channel=by_channel,
        by_type=stats["by_type"],
    )
