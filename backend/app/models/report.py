"""Report model for report definitions and executions."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ReportType(str, enum.Enum):
    """Report type enumeration."""

    # Financial Reports
    REVENUE = "revenue"  # Revenue report
    CLAIMS = "claims"  # Claims report
    PAYMENTS = "payments"  # Payments report
    OUTSTANDING_BALANCES = "outstanding_balances"  # Patient balances
    COLLECTIONS = "collections"  # Collections report

    # Clinical Reports
    PATIENT_DEMOGRAPHICS = "patient_demographics"  # Patient demographics
    APPOINTMENT_STATISTICS = "appointment_statistics"  # Appointment stats
    PROVIDER_PRODUCTIVITY = "provider_productivity"  # Provider productivity
    NO_SHOWS = "no_shows"  # No-show report
    DIAGNOSIS_TRENDS = "diagnosis_trends"  # Diagnosis trends

    # Operational Reports
    STAFF_PRODUCTIVITY = "staff_productivity"  # Staff productivity
    TASK_COMPLETION = "task_completion"  # Task completion rates
    INSURANCE_VERIFICATION = "insurance_verification"  # Insurance verification
    DOCUMENT_STATUS = "document_status"  # Document processing status

    # Quality Reports
    PATIENT_SATISFACTION = "patient_satisfaction"  # Patient satisfaction
    CLINICAL_OUTCOMES = "clinical_outcomes"  # Clinical outcomes
    QUALITY_MEASURES = "quality_measures"  # Quality measures

    # Custom Reports
    CUSTOM = "custom"  # Custom report


class ReportStatus(str, enum.Enum):
    """Report execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReportFormat(str, enum.Enum):
    """Report output format enumeration."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


class Report(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Reports and analytics."""

    __tablename__ = "reports"

    # Report definition
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Report name")
    description: Mapped[str | None] = mapped_column(Text, comment="Report description")

    # Report configuration
    parameters: Mapped[dict | None] = mapped_column(
        JSONB, comment="Report parameters (filters, date ranges, etc.)"
    )
    columns: Mapped[list | None] = mapped_column(
        JSONB, comment="Report columns configuration"
    )
    sort_by: Mapped[str | None] = mapped_column(
        String(100), comment="Default sort column"
    )
    sort_order: Mapped[str | None] = mapped_column(
        String(10), comment="Sort order (asc/desc)"
    )

    # Execution
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False, index=True
    )
    format: Mapped[ReportFormat] = mapped_column(
        Enum(ReportFormat), default=ReportFormat.PDF, nullable=False
    )

    # Ownership
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        comment="User who created the report",
    )

    # Execution details
    started_at: Mapped[str | None] = mapped_column(
        String(29), comment="Execution start timestamp (ISO 8601)"
    )
    completed_at: Mapped[str | None] = mapped_column(
        String(29), comment="Execution completion timestamp (ISO 8601)"
    )
    execution_time_ms: Mapped[int | None] = mapped_column(
        comment="Execution time in milliseconds"
    )

    # Results
    result_count: Mapped[int | None] = mapped_column(
        comment="Number of records in result"
    )
    file_path: Mapped[str | None] = mapped_column(
        String(1000), comment="Generated report file path"
    )
    file_size: Mapped[int | None] = mapped_column(
        comment="Generated file size in bytes"
    )
    storage_backend: Mapped[str | None] = mapped_column(
        String(50), comment="Storage backend (local, s3, azure)"
    )
    bucket_name: Mapped[str | None] = mapped_column(
        String(255), comment="S3 bucket or Azure container"
    )

    # Error handling
    error_message: Mapped[str | None] = mapped_column(
        Text, comment="Error message if failed"
    )

    # Access and expiration
    expires_at: Mapped[str | None] = mapped_column(
        String(29), comment="Report expiration timestamp (ISO 8601)"
    )
    download_count: Mapped[int] = mapped_column(
        default=0, comment="Number of times downloaded"
    )
    last_downloaded_at: Mapped[str | None] = mapped_column(
        String(29), comment="Last download timestamp (ISO 8601)"
    )

    # Sharing
    is_shared: Mapped[bool] = mapped_column(
        default=False, comment="Is report shared with others"
    )
    shared_with_users: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of user IDs with access"
    )

    # Template
    is_template: Mapped[bool] = mapped_column(
        default=False, comment="Is this a report template"
    )
    template_name: Mapped[str | None] = mapped_column(
        String(255), comment="Template name if template"
    )

    # Metadata
    metadata: Mapped[dict | None] = mapped_column(JSONB, comment="Additional metadata")

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])

    def __repr__(self) -> str:
        return f"<Report(name={self.name}, type={self.report_type}, status={self.status})>"

    @property
    def is_completed(self) -> bool:
        """Check if report execution is completed."""
        return self.status == ReportStatus.COMPLETED

    @property
    def is_running(self) -> bool:
        """Check if report is currently running."""
        return self.status == ReportStatus.RUNNING

    @property
    def is_failed(self) -> bool:
        """Check if report execution failed."""
        return self.status == ReportStatus.FAILED

    @property
    def file_size_mb(self) -> float | None:
        """Get file size in MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None

    @property
    def is_expired(self) -> bool:
        """Check if report has expired."""
        if not self.expires_at:
            return False

        from datetime import datetime
        try:
            expires = datetime.fromisoformat(self.expires_at)
            return expires < datetime.utcnow()
        except (ValueError, TypeError):
            return False
