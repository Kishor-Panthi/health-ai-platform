"""Service for notification operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.notifications import NotificationCreate, NotificationUpdate
from app.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)


class NotificationService:
    """Service for managing notifications."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ============================================================================
    # CRUD Operations
    # ============================================================================

    async def create_notification(
        self,
        notification_in: NotificationCreate,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            practice_id=self.practice_id,
            notification_type=notification_in.notification_type,
            priority=notification_in.priority,
            channels=notification_in.channels,
            title=notification_in.title,
            body=notification_in.body,
            action_url=notification_in.action_url,
            user_id=notification_in.user_id,
            patient_id=notification_in.patient_id,
            appointment_id=notification_in.appointment_id,
            message_id=notification_in.message_id,
            document_id=notification_in.document_id,
            task_id=notification_in.task_id,
            claim_id=notification_in.claim_id,
            scheduled_for=notification_in.scheduled_for,
            expires_at=notification_in.expires_at,
            max_retries=notification_in.max_retries,
            metadata=notification_in.metadata,
            status=NotificationStatus.PENDING,
            retry_count=0,
        )

        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def get_notification(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID."""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.practice_id == self.practice_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_notification(
        self, notification_id: UUID, notification_in: NotificationUpdate
    ) -> Optional[Notification]:
        """Update notification."""
        notification = await self.get_notification(notification_id)
        if not notification:
            return None

        update_data = notification_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notification, field, value)

        notification.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def delete_notification(self, notification_id: UUID) -> bool:
        """Delete notification (hard delete since no soft delete on notifications)."""
        notification = await self.get_notification(notification_id)
        if not notification:
            return False

        await self.db.delete(notification)
        await self.db.flush()
        return True

    # ============================================================================
    # Notification Actions
    # ============================================================================

    async def send_notification(self, notification_id: UUID) -> Optional[Notification]:
        """Send a notification immediately."""
        notification = await self.get_notification(notification_id)
        if not notification:
            return None

        if notification.status == NotificationStatus.PENDING:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow().isoformat()
            notification.updated_at = datetime.utcnow().isoformat()

            # Initialize delivery attempts dict
            if not notification.delivery_attempts:
                notification.delivery_attempts = {}

            # Record delivery attempt for each channel
            for channel in notification.channels:
                if isinstance(channel, NotificationChannel):
                    channel_name = channel.value
                else:
                    channel_name = str(channel)

                notification.delivery_attempts[channel_name] = {
                    "attempted_at": datetime.utcnow().isoformat(),
                    "status": "sent",
                }

            # Mark as delivered (in production, this would be async)
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.utcnow().isoformat()

            await self.db.flush()
            await self.db.refresh(notification)

        return notification

    async def mark_as_read(
        self, notification_id: UUID, user_id: UUID
    ) -> Optional[Notification]:
        """Mark notification as read."""
        notification = await self.get_notification(notification_id)
        if not notification:
            return None

        # Verify notification belongs to user
        if notification.user_id != user_id:
            raise ValueError("Notification does not belong to user")

        if notification.status != NotificationStatus.READ:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow().isoformat()
            notification.updated_at = datetime.utcnow().isoformat()
            await self.db.flush()
            await self.db.refresh(notification)

        return notification

    async def retry_notification(self, notification_id: UUID) -> Optional[Notification]:
        """Retry a failed notification."""
        notification = await self.get_notification(notification_id)
        if not notification:
            return None

        if not notification.can_retry:
            raise ValueError("Cannot retry notification: max retries reached or not in failed status")

        notification.retry_count += 1
        notification.status = NotificationStatus.PENDING
        notification.failed_at = None
        notification.error_message = None
        notification.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(notification)

        # Attempt to send again
        return await self.send_notification(notification_id)

    async def mark_as_failed(
        self, notification_id: UUID, error_message: str
    ) -> Optional[Notification]:
        """Mark notification as failed."""
        notification = await self.get_notification(notification_id)
        if not notification:
            return None

        notification.status = NotificationStatus.FAILED
        notification.failed_at = datetime.utcnow().isoformat()
        notification.error_message = error_message
        notification.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    # ============================================================================
    # Query Operations
    # ============================================================================

    async def list_user_notifications(
        self,
        user_id: UUID,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Notification], int]:
        """List notifications for a user."""
        conditions = [
            Notification.practice_id == self.practice_id,
            Notification.user_id == user_id,
        ]

        if status:
            conditions.append(Notification.status == status)
        if notification_type:
            conditions.append(Notification.notification_type == notification_type)
        if unread_only:
            conditions.append(Notification.status != NotificationStatus.READ)

        # Count query
        count_query = select(func.count()).select_from(Notification).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Notification)
            .where(and_(*conditions))
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        notifications = result.scalars().all()
        return list(notifications), total

    async def get_pending_notifications(
        self, limit: int = 100
    ) -> list[Notification]:
        """Get pending notifications ready to be sent."""
        now = datetime.utcnow().isoformat()

        query = (
            select(Notification)
            .where(
                and_(
                    Notification.practice_id == self.practice_id,
                    Notification.status == NotificationStatus.PENDING,
                    or_(
                        Notification.scheduled_for.is_(None),
                        Notification.scheduled_for <= now,
                    ),
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > now,
                    ),
                )
            )
            .order_by(Notification.priority.desc(), Notification.created_at.asc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_failed_notifications(
        self, limit: int = 100
    ) -> list[Notification]:
        """Get failed notifications that can be retried."""
        query = (
            select(Notification)
            .where(
                and_(
                    Notification.practice_id == self.practice_id,
                    Notification.status == NotificationStatus.FAILED,
                    Notification.retry_count < Notification.max_retries,
                )
            )
            .order_by(Notification.failed_at.asc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_appointment_notifications(
        self, appointment_id: UUID
    ) -> list[Notification]:
        """Get all notifications for an appointment."""
        query = select(Notification).where(
            and_(
                Notification.appointment_id == appointment_id,
                Notification.practice_id == self.practice_id,
            )
        ).order_by(Notification.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_patient_notifications(
        self, patient_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Notification], int]:
        """Get all notifications related to a patient."""
        conditions = [
            Notification.practice_id == self.practice_id,
            Notification.patient_id == patient_id,
        ]

        # Count query
        count_query = select(func.count()).select_from(Notification).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Notification)
            .where(and_(*conditions))
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        notifications = result.scalars().all()
        return list(notifications), total

    # ============================================================================
    # Statistics
    # ============================================================================

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for user."""
        query = select(func.count()).select_from(Notification).where(
            and_(
                Notification.practice_id == self.practice_id,
                Notification.user_id == user_id,
                Notification.status != NotificationStatus.READ,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_notification_stats(self, user_id: UUID) -> dict:
        """Get notification statistics for user."""
        # Total by status
        status_query = (
            select(
                Notification.status,
                func.count().label("count")
            )
            .where(
                and_(
                    Notification.practice_id == self.practice_id,
                    Notification.user_id == user_id,
                )
            )
            .group_by(Notification.status)
        )
        status_result = await self.db.execute(status_query)
        status_counts = {row.status.value: row.count for row in status_result}

        # By notification type
        type_query = (
            select(
                Notification.notification_type,
                func.count().label("count")
            )
            .where(
                and_(
                    Notification.practice_id == self.practice_id,
                    Notification.user_id == user_id,
                )
            )
            .group_by(Notification.notification_type)
        )
        type_result = await self.db.execute(type_query)
        type_counts = {row.notification_type.value: row.count for row in type_result}

        unread_count = await self.get_unread_count(user_id)

        return {
            "total_sent": status_counts.get("sent", 0),
            "total_delivered": status_counts.get("delivered", 0),
            "total_failed": status_counts.get("failed", 0),
            "total_pending": status_counts.get("pending", 0),
            "unread_count": unread_count,
            "by_type": type_counts,
        }

    # ============================================================================
    # Batch Operations
    # ============================================================================

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user."""
        query = select(Notification).where(
            and_(
                Notification.practice_id == self.practice_id,
                Notification.user_id == user_id,
                Notification.status != NotificationStatus.READ,
            )
        )
        result = await self.db.execute(query)
        notifications = result.scalars().all()

        count = 0
        now = datetime.utcnow().isoformat()
        for notification in notifications:
            notification.status = NotificationStatus.READ
            notification.read_at = now
            notification.updated_at = now
            count += 1

        await self.db.flush()
        return count

    async def delete_old_notifications(self, days: int = 90) -> int:
        """Delete notifications older than specified days."""
        from datetime import timedelta

        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        query = select(Notification).where(
            and_(
                Notification.practice_id == self.practice_id,
                Notification.created_at < cutoff_date,
                Notification.status.in_([
                    NotificationStatus.READ,
                    NotificationStatus.DELIVERED,
                ]),
            )
        )
        result = await self.db.execute(query)
        notifications = result.scalars().all()

        count = len(notifications)
        for notification in notifications:
            await self.db.delete(notification)

        await self.db.flush()
        return count
