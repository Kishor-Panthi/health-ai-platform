"""Task model for workflow automation and task management."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class TaskType(str, enum.Enum):
    """Task type enumeration."""

    MANUAL = "manual"  # Manual task requiring user action
    APPOINTMENT_REMINDER = "appointment_reminder"  # Send appointment reminder
    INSURANCE_VERIFICATION = "insurance_verification"  # Verify insurance
    DOCUMENT_REVIEW = "document_review"  # Review document
    LAB_FOLLOWUP = "lab_followup"  # Follow up on lab results
    BILLING_FOLLOWUP = "billing_followup"  # Follow up on billing
    PATIENT_OUTREACH = "patient_outreach"  # Patient outreach/callback
    REFERRAL_FOLLOWUP = "referral_followup"  # Follow up on referral
    PRESCRIPTION_REFILL = "prescription_refill"  # Prescription refill reminder
    CUSTOM = "custom"  # Custom task type


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Task(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Tasks and workflow automation."""

    __tablename__ = "tasks"

    # Task details
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType), nullable=False, index=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.NORMAL, nullable=False
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Task title")
    description: Mapped[str | None] = mapped_column(Text, comment="Task description")

    # Assignment
    assigned_to_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        comment="User assigned to this task",
    )
    assigned_to_role: Mapped[str | None] = mapped_column(
        String(50), comment="Role assigned to this task (if not specific user)"
    )
    assigned_by_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who assigned the task",
    )

    # Related entities
    patient_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        index=True,
        comment="Related patient",
    )
    appointment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        comment="Related appointment",
    )
    claim_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billing_claims.id", ondelete="SET NULL"),
        comment="Related billing claim",
    )
    document_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        comment="Related document",
    )

    # Scheduling
    due_date: Mapped[str | None] = mapped_column(
        String(10), index=True, comment="Due date (YYYY-MM-DD)"
    )
    due_time: Mapped[str | None] = mapped_column(
        String(8), comment="Due time (HH:MM:SS)"
    )
    scheduled_for: Mapped[str | None] = mapped_column(
        String(29), comment="Scheduled execution time (ISO 8601)"
    )

    # Completion
    completed_at: Mapped[str | None] = mapped_column(
        String(29), comment="Completion timestamp (ISO 8601)"
    )
    completed_by_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who completed the task",
    )
    completion_notes: Mapped[str | None] = mapped_column(
        Text, comment="Notes about task completion"
    )

    # Workflow
    workflow_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        comment="Workflow this task belongs to",
    )
    parent_task_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        comment="Parent task if this is a subtask",
    )
    depends_on_task_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        comment="Task that must be completed before this one",
    )

    # Automation
    is_automated: Mapped[bool] = mapped_column(
        default=False, comment="Is this an automated task"
    )
    automation_config: Mapped[dict | None] = mapped_column(
        JSONB, comment="Configuration for automated execution"
    )
    last_execution_at: Mapped[str | None] = mapped_column(
        String(29), comment="Last execution timestamp for recurring tasks"
    )
    next_execution_at: Mapped[str | None] = mapped_column(
        String(29), comment="Next execution timestamp for recurring tasks"
    )
    is_recurring: Mapped[bool] = mapped_column(
        default=False, comment="Is this a recurring task"
    )
    recurrence_rule: Mapped[str | None] = mapped_column(
        String(255), comment="Recurrence rule (e.g., RRULE format)"
    )

    # Reminders
    reminder_sent: Mapped[bool] = mapped_column(
        default=False, comment="Has reminder been sent"
    )
    reminder_sent_at: Mapped[str | None] = mapped_column(
        String(29), comment="Reminder sent timestamp (ISO 8601)"
    )

    # Metadata
    tags: Mapped[list | None] = mapped_column(JSONB, comment="Array of tags")
    metadata: Mapped[dict | None] = mapped_column(JSONB, comment="Additional metadata")

    # Relationships
    assigned_to_user = relationship(
        "User", foreign_keys=[assigned_to_user_id], back_populates="assigned_tasks"
    )
    assigned_by_user = relationship("User", foreign_keys=[assigned_by_user_id])
    completed_by_user = relationship("User", foreign_keys=[completed_by_user_id])
    patient = relationship("Patient")
    appointment = relationship("Appointment")
    claim = relationship("BillingClaim")
    document = relationship("Document")
    parent_task = relationship(
        "Task", remote_side="Task.id", foreign_keys=[parent_task_id], uselist=False
    )
    depends_on_task = relationship(
        "Task", remote_side="Task.id", foreign_keys=[depends_on_task_id], uselist=False
    )

    def __repr__(self) -> str:
        return f"<Task(title={self.title}, status={self.status}, priority={self.priority})>"

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        from datetime import date

        if not self.due_date or self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        ):
            return False

        try:
            due = date.fromisoformat(self.due_date)
            return due < date.today()
        except (ValueError, TypeError):
            return False

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

    @property
    def can_execute(self) -> bool:
        """Check if task can be executed (no blocking dependencies)."""
        # Would need to check depends_on_task status in actual implementation
        return self.status == TaskStatus.PENDING
