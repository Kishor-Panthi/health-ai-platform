"""Service for message operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.messages import MessageCreate, MessageUpdate
from app.models.message import Message, MessageStatus, MessageType


class MessageService:
    """Service for managing messages."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ============================================================================
    # CRUD Operations
    # ============================================================================

    async def create_message(
        self,
        message_in: MessageCreate,
        sender_id: UUID,
    ) -> Message:
        """Create a new message."""
        # Validate recipient
        if not message_in.recipient_user_id and not message_in.recipient_patient_id:
            raise ValueError("Must specify either recipient_user_id or recipient_patient_id")

        message = Message(
            practice_id=self.practice_id,
            sender_id=sender_id,
            message_type=message_in.message_type,
            priority=message_in.priority,
            subject=message_in.subject,
            body=message_in.body,
            recipient_user_id=message_in.recipient_user_id,
            recipient_patient_id=message_in.recipient_patient_id,
            thread_id=message_in.thread_id,
            appointment_id=message_in.appointment_id,
            patient_id=message_in.patient_id,
            status=MessageStatus.SENT,
            is_system_message=message_in.is_system_message,
            requires_acknowledgment=message_in.requires_acknowledgment,
            is_encrypted=message_in.is_encrypted,
            attachment_document_ids=message_in.attachment_document_ids,
            metadata=message_in.metadata,
        )

        # If part of thread, update to THREAD type
        if message_in.thread_id:
            message.message_type = MessageType.THREAD

        # Auto-deliver
        message.delivered_at = datetime.utcnow().isoformat()

        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_message(self, message_id: UUID) -> Optional[Message]:
        """Get message by ID."""
        result = await self.db.execute(
            select(Message).where(
                and_(
                    Message.id == message_id,
                    Message.practice_id == self.practice_id,
                    Message.is_deleted == False,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_message(
        self, message_id: UUID, message_in: MessageUpdate
    ) -> Optional[Message]:
        """Update message."""
        message = await self.get_message(message_id)
        if not message:
            return None

        update_data = message_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(message, field, value)

        message.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def delete_message(self, message_id: UUID) -> bool:
        """Soft delete message."""
        message = await self.get_message(message_id)
        if not message:
            return False

        message.is_deleted = True
        message.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        return True

    # ============================================================================
    # Message Actions
    # ============================================================================

    async def mark_as_read(
        self, message_id: UUID, user_id: UUID
    ) -> Optional[Message]:
        """Mark message as read."""
        message = await self.get_message(message_id)
        if not message:
            return None

        if message.status != MessageStatus.READ:
            message.status = MessageStatus.READ
            message.read_at = datetime.utcnow().isoformat()
            message.read_by = user_id
            message.updated_at = datetime.utcnow().isoformat()
            await self.db.flush()
            await self.db.refresh(message)

        return message

    async def acknowledge_message(
        self, message_id: UUID, user_id: UUID
    ) -> Optional[Message]:
        """Acknowledge a message that requires acknowledgment."""
        message = await self.get_message(message_id)
        if not message:
            return None

        if not message.requires_acknowledgment:
            raise ValueError("This message does not require acknowledgment")

        if message.status != MessageStatus.ACKNOWLEDGED:
            message.status = MessageStatus.ACKNOWLEDGED
            message.acknowledged_at = datetime.utcnow().isoformat()
            message.acknowledged_by = user_id
            message.updated_at = datetime.utcnow().isoformat()
            await self.db.flush()
            await self.db.refresh(message)

        return message

    # ============================================================================
    # Thread Operations
    # ============================================================================

    async def get_thread_messages(
        self, thread_id: UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[Message], int]:
        """Get all messages in a thread."""
        # Count query
        count_query = select(func.count()).select_from(Message).where(
            and_(
                Message.thread_id == thread_id,
                Message.practice_id == self.practice_id,
                Message.is_deleted == False,
            )
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Message)
            .where(
                and_(
                    Message.thread_id == thread_id,
                    Message.practice_id == self.practice_id,
                    Message.is_deleted == False,
                )
            )
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = result.scalars().all()
        return list(messages), total

    async def get_user_threads(
        self, user_id: UUID, skip: int = 0, limit: int = 50
    ) -> list[dict]:
        """Get all threads involving a user."""
        # Find all thread IDs for user
        query = (
            select(Message.thread_id, func.max(Message.created_at).label("last_message_at"))
            .where(
                and_(
                    Message.practice_id == self.practice_id,
                    Message.is_deleted == False,
                    Message.thread_id.isnot(None),
                    or_(
                        Message.sender_id == user_id,
                        Message.recipient_user_id == user_id,
                    ),
                )
            )
            .group_by(Message.thread_id)
            .order_by(func.max(Message.created_at).desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        threads = result.all()

        thread_summaries = []
        for thread_id, last_message_at in threads:
            # Get thread details
            thread_query = select(Message).where(
                and_(
                    Message.thread_id == thread_id,
                    Message.practice_id == self.practice_id,
                    Message.is_deleted == False,
                )
            )
            thread_result = await self.db.execute(thread_query)
            thread_messages = thread_result.scalars().all()

            if thread_messages:
                first_message = thread_messages[0]
                unread_count = sum(
                    1 for m in thread_messages
                    if m.recipient_user_id == user_id and m.status != MessageStatus.READ
                )

                thread_summaries.append({
                    "thread_id": thread_id,
                    "subject": first_message.subject,
                    "message_count": len(thread_messages),
                    "last_message_at": last_message_at,
                    "unread_count": unread_count,
                })

        return thread_summaries

    # ============================================================================
    # Query Operations
    # ============================================================================

    async def list_inbox_messages(
        self,
        user_id: UUID,
        status: Optional[MessageStatus] = None,
        message_type: Optional[MessageType] = None,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Message], int]:
        """List messages in user's inbox."""
        conditions = [
            Message.practice_id == self.practice_id,
            Message.is_deleted == False,
            Message.recipient_user_id == user_id,
        ]

        if status:
            conditions.append(Message.status == status)
        if message_type:
            conditions.append(Message.message_type == message_type)
        if unread_only:
            conditions.append(Message.status != MessageStatus.READ)

        # Count query
        count_query = select(func.count()).select_from(Message).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Message)
            .where(and_(*conditions))
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = result.scalars().all()
        return list(messages), total

    async def list_sent_messages(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Message], int]:
        """List messages sent by user."""
        conditions = [
            Message.practice_id == self.practice_id,
            Message.is_deleted == False,
            Message.sender_id == user_id,
        ]

        # Count query
        count_query = select(func.count()).select_from(Message).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Message)
            .where(and_(*conditions))
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = result.scalars().all()
        return list(messages), total

    async def get_patient_messages(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Message], int]:
        """Get all messages related to a patient."""
        conditions = [
            Message.practice_id == self.practice_id,
            Message.is_deleted == False,
            or_(
                Message.patient_id == patient_id,
                Message.recipient_patient_id == patient_id,
            ),
        ]

        # Count query
        count_query = select(func.count()).select_from(Message).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Message)
            .where(and_(*conditions))
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = result.scalars().all()
        return list(messages), total

    async def get_appointment_messages(
        self, appointment_id: UUID
    ) -> list[Message]:
        """Get all messages for an appointment."""
        query = select(Message).where(
            and_(
                Message.appointment_id == appointment_id,
                Message.practice_id == self.practice_id,
                Message.is_deleted == False,
            )
        ).order_by(Message.created_at.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ============================================================================
    # Statistics
    # ============================================================================

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread messages for user."""
        query = select(func.count()).select_from(Message).where(
            and_(
                Message.practice_id == self.practice_id,
                Message.is_deleted == False,
                Message.recipient_user_id == user_id,
                Message.status != MessageStatus.READ,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_pending_acknowledgment_count(self, user_id: UUID) -> int:
        """Get count of messages pending acknowledgment."""
        query = select(func.count()).select_from(Message).where(
            and_(
                Message.practice_id == self.practice_id,
                Message.is_deleted == False,
                Message.recipient_user_id == user_id,
                Message.requires_acknowledgment == True,
                Message.status != MessageStatus.ACKNOWLEDGED,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_message_stats(self, user_id: UUID) -> dict:
        """Get message statistics for user."""
        # Count sent messages
        sent_query = select(func.count()).select_from(Message).where(
            and_(
                Message.practice_id == self.practice_id,
                Message.is_deleted == False,
                Message.sender_id == user_id,
            )
        )
        sent_result = await self.db.execute(sent_query)
        total_sent = sent_result.scalar_one()

        # Count received messages
        received_query = select(func.count()).select_from(Message).where(
            and_(
                Message.practice_id == self.practice_id,
                Message.is_deleted == False,
                Message.recipient_user_id == user_id,
            )
        )
        received_result = await self.db.execute(received_query)
        total_received = received_result.scalar_one()

        unread_count = await self.get_unread_count(user_id)
        pending_ack = await self.get_pending_acknowledgment_count(user_id)

        return {
            "total_sent": total_sent,
            "total_received": total_received,
            "unread_count": unread_count,
            "pending_acknowledgment": pending_ack,
        }
