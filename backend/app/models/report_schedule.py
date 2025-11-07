"""Report schedule model for automated report generation."""

from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ScheduleFrequency(str, enum.Enum):
    """Schedule frequency enumeration."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"  # Uses cron expression


class ScheduleStatus(str, enum.Enum):
    """Schedule status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class DeliveryMethod(str, enum.Enum):
    """Report delivery method enumeration."""

    EMAIL = "email"
    PORTAL = "portal"  # Save to portal for download
    BOTH = "both"


class ReportSchedule(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """Scheduled report generation."""

    __tablename__ = "report_schedules"

    # Schedule details
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Schedule name")
    description: Mapped[str | None] = mapped_column(Text, comment="Schedule description")

    # Report configuration
    report_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Type of report to generate"
    )
    report_format: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Output format (pdf, excel, csv, etc.)"
    )
    report_parameters: Mapped[dict | None] = mapped_column(
        JSONB, comment="Report parameters and filters"
    )

    # Schedule configuration
    frequency: Mapped[ScheduleFrequency] = mapped_column(
        Enum(ScheduleFrequency), nullable=False, index=True
    )
    cron_expression: Mapped[str | None] = mapped_column(
        String(100), comment="Cron expression for custom frequency"
    )
    day_of_week: Mapped[int | None] = mapped_column(
        comment="Day of week for weekly schedules (0=Monday)"
    )
    day_of_month: Mapped[int | None] = mapped_column(
        comment="Day of month for monthly schedules (1-31)"
    )
    time_of_day: Mapped[str | None] = mapped_column(
        String(8), comment="Time to run (HH:MM:SS)"
    )
    timezone: Mapped[str] = mapped_column(
        String(50), default="UTC", nullable=False, comment="Timezone for schedule"
    )

    # Status
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus), default=ScheduleStatus.ACTIVE, nullable=False, index=True
    )
    is_enabled: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Is schedule enabled"
    )

    # Ownership
    created_by_user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who created the schedule",
    )

    # Delivery
    delivery_method: Mapped[DeliveryMethod] = mapped_column(
        Enum(DeliveryMethod), default=DeliveryMethod.EMAIL, nullable=False
    )
    email_recipients: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of email addresses"
    )
    email_subject: Mapped[str | None] = mapped_column(
        String(255), comment="Email subject template"
    )
    email_body: Mapped[str | None] = mapped_column(Text, comment="Email body template")

    # Execution tracking
    last_run_at: Mapped[str | None] = mapped_column(
        String(29), comment="Last execution timestamp (ISO 8601)"
    )
    last_run_status: Mapped[str | None] = mapped_column(
        String(50), comment="Status of last run"
    )
    last_run_error: Mapped[str | None] = mapped_column(
        Text, comment="Error from last run if failed"
    )
    next_run_at: Mapped[str | None] = mapped_column(
        String(29), index=True, comment="Next scheduled run timestamp (ISO 8601)"
    )

    # Statistics
    total_runs: Mapped[int] = mapped_column(default=0, comment="Total number of runs")
    successful_runs: Mapped[int] = mapped_column(
        default=0, comment="Number of successful runs"
    )
    failed_runs: Mapped[int] = mapped_column(default=0, comment="Number of failed runs")

    # Report retention
    retention_days: Mapped[int | None] = mapped_column(
        comment="Days to retain generated reports"
    )
    auto_delete_old_reports: Mapped[bool] = mapped_column(
        default=False, comment="Automatically delete old reports"
    )

    # Metadata
    metadata: Mapped[dict | None] = mapped_column(JSONB, comment="Additional metadata")

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])

    def __repr__(self) -> str:
        return f"<ReportSchedule(name={self.name}, frequency={self.frequency}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if schedule is active."""
        return self.status == ScheduleStatus.ACTIVE and self.is_enabled

    @property
    def is_due(self) -> bool:
        """Check if schedule is due to run."""
        if not self.is_active or not self.next_run_at:
            return False

        from datetime import datetime
        try:
            next_run = datetime.fromisoformat(self.next_run_at)
            return next_run <= datetime.utcnow()
        except (ValueError, TypeError):
            return False

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_runs == 0:
            return 0.0
        return round((self.successful_runs / self.total_runs) * 100, 2)
