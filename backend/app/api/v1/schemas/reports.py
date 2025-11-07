"""Pydantic schemas for reports."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.report import ReportFormat, ReportStatus, ReportType
from app.models.report_schedule import DeliveryMethod, ScheduleFrequency, ScheduleStatus


# ============================================================================
# Report Schemas
# ============================================================================


class ReportBase(BaseModel):
    """Base report schema."""

    report_type: ReportType
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    parameters: Optional[dict] = None
    columns: Optional[list] = None
    sort_by: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[str] = Field(None, pattern=r"^(asc|desc)$")
    format: ReportFormat = ReportFormat.PDF
    expires_at: Optional[str] = None
    is_shared: bool = False
    shared_with_users: Optional[list[UUID]] = None
    is_template: bool = False
    template_name: Optional[str] = Field(None, max_length=255)
    metadata: Optional[dict] = None


class ReportCreate(ReportBase):
    """Schema for creating a report."""

    pass


class ReportUpdate(BaseModel):
    """Schema for updating a report."""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parameters: Optional[dict] = None
    status: Optional[ReportStatus] = None
    metadata: Optional[dict] = None


class Report(ReportBase):
    """Complete report schema."""

    id: UUID
    practice_id: UUID
    status: ReportStatus
    created_by_user_id: Optional[UUID]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time_ms: Optional[int] = None
    result_count: Optional[int] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    storage_backend: Optional[str] = None
    bucket_name: Optional[str] = None
    error_message: Optional[str] = None
    download_count: int
    last_downloaded_at: Optional[str] = None
    created_at: str
    updated_at: str
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class ReportWithComputedFields(Report):
    """Report with computed properties."""

    is_completed: bool
    is_running: bool
    is_failed: bool
    file_size_mb: Optional[float]
    is_expired: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Report Execution Schemas
# ============================================================================


class ExecuteReportRequest(BaseModel):
    """Request to execute a report."""

    parameters: Optional[dict] = None
    format: Optional[ReportFormat] = None


class ExecuteReportResponse(BaseModel):
    """Response after executing report."""

    report_id: UUID
    status: ReportStatus
    message: str = "Report execution started"


class DownloadReportResponse(BaseModel):
    """Response with report download details."""

    report_id: UUID
    file_path: str
    file_size: int
    file_size_mb: float
    format: ReportFormat
    download_url: Optional[str] = None


# ============================================================================
# Report Schedule Schemas
# ============================================================================


class ReportScheduleBase(BaseModel):
    """Base report schedule schema."""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    report_type: str = Field(..., max_length=100)
    report_format: str = Field(..., max_length=50)
    report_parameters: Optional[dict] = None
    frequency: ScheduleFrequency
    cron_expression: Optional[str] = Field(None, max_length=100)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    time_of_day: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$")
    timezone: str = Field("UTC", max_length=50)
    delivery_method: DeliveryMethod = DeliveryMethod.EMAIL
    email_recipients: Optional[list[str]] = None
    email_subject: Optional[str] = Field(None, max_length=255)
    email_body: Optional[str] = None
    retention_days: Optional[int] = Field(None, ge=1)
    auto_delete_old_reports: bool = False
    metadata: Optional[dict] = None


class ReportScheduleCreate(ReportScheduleBase):
    """Schema for creating a report schedule."""

    pass


class ReportScheduleUpdate(BaseModel):
    """Schema for updating a report schedule."""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    report_parameters: Optional[dict] = None
    frequency: Optional[ScheduleFrequency] = None
    cron_expression: Optional[str] = Field(None, max_length=100)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    time_of_day: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$")
    timezone: Optional[str] = Field(None, max_length=50)
    status: Optional[ScheduleStatus] = None
    is_enabled: Optional[bool] = None
    delivery_method: Optional[DeliveryMethod] = None
    email_recipients: Optional[list[str]] = None
    email_subject: Optional[str] = Field(None, max_length=255)
    email_body: Optional[str] = None
    retention_days: Optional[int] = Field(None, ge=1)
    auto_delete_old_reports: Optional[bool] = None
    metadata: Optional[dict] = None


class ReportSchedule(ReportScheduleBase):
    """Complete report schedule schema."""

    id: UUID
    practice_id: UUID
    status: ScheduleStatus
    is_enabled: bool
    created_by_user_id: UUID
    last_run_at: Optional[str] = None
    last_run_status: Optional[str] = None
    last_run_error: Optional[str] = None
    next_run_at: Optional[str] = None
    total_runs: int
    successful_runs: int
    failed_runs: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ReportScheduleWithComputedFields(ReportSchedule):
    """Report schedule with computed properties."""

    is_active: bool
    is_due: bool
    success_rate: float

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Report Template Schemas
# ============================================================================


class ReportTemplate(BaseModel):
    """Report template schema."""

    id: UUID
    report_type: ReportType
    name: str
    description: Optional[str]
    parameters: Optional[dict]
    columns: Optional[list]
    format: ReportFormat
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class CreateFromTemplateRequest(BaseModel):
    """Request to create report from template."""

    template_id: UUID
    name: str = Field(..., max_length=255)
    parameters: Optional[dict] = None
    format: Optional[ReportFormat] = None


# ============================================================================
# Query Schemas
# ============================================================================


class ReportSummary(BaseModel):
    """Summary of report for listings."""

    id: UUID
    report_type: ReportType
    name: str
    status: ReportStatus
    format: ReportFormat
    result_count: Optional[int]
    execution_time_ms: Optional[int]
    created_at: str
    completed_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ReportStats(BaseModel):
    """Report statistics."""

    total_reports: int
    completed_reports: int
    running_reports: int
    failed_reports: int
    total_downloads: int
    by_type: dict[str, int]
    by_format: dict[str, int]
