"""Pydantic schemas for analytics and metrics."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Time Range Schemas
# ============================================================================


class DateRange(BaseModel):
    """Date range for analytics queries."""

    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    comparison_start_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    comparison_end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")


# ============================================================================
# Financial Analytics
# ============================================================================


class RevenueMetrics(BaseModel):
    """Revenue metrics."""

    total_revenue: float
    total_charges: float
    total_payments: float
    total_adjustments: float
    outstanding_balance: float
    collection_rate: float  # Percentage
    average_revenue_per_patient: float
    period_start: str
    period_end: str
    comparison_change: Optional[float] = None  # Percentage change from comparison period


class PaymentMetrics(BaseModel):
    """Payment metrics."""

    total_payments: int
    total_amount: float
    insurance_payments: float
    patient_payments: float
    average_payment_amount: float
    payment_methods: dict[str, float]  # Method -> Amount
    period_start: str
    period_end: str


class ClaimMetrics(BaseModel):
    """Claims metrics."""

    total_claims: int
    submitted_claims: int
    accepted_claims: int
    rejected_claims: int
    denied_claims: int
    pending_claims: int
    acceptance_rate: float  # Percentage
    average_claim_amount: float
    total_claim_value: float
    period_start: str
    period_end: str


# ============================================================================
# Clinical Analytics
# ============================================================================


class AppointmentMetrics(BaseModel):
    """Appointment metrics."""

    total_appointments: int
    scheduled_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int
    completion_rate: float  # Percentage
    no_show_rate: float  # Percentage
    cancellation_rate: float  # Percentage
    average_appointments_per_day: float
    period_start: str
    period_end: str


class PatientMetrics(BaseModel):
    """Patient metrics."""

    total_patients: int
    new_patients: int
    active_patients: int
    inactive_patients: int
    average_age: float
    gender_distribution: dict[str, int]  # Gender -> Count
    insurance_distribution: dict[str, int]  # Insurance type -> Count
    period_start: str
    period_end: str


class ProviderMetrics(BaseModel):
    """Provider productivity metrics."""

    provider_id: UUID
    provider_name: str
    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_shows: int
    total_patients_seen: int
    unique_patients: int
    average_appointments_per_day: float
    completion_rate: float  # Percentage
    revenue_generated: float
    period_start: str
    period_end: str


# ============================================================================
# Operational Analytics
# ============================================================================


class TaskMetrics(BaseModel):
    """Task completion metrics."""

    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    completion_rate: float  # Percentage
    average_completion_time_hours: float
    by_type: dict[str, int]  # Task type -> Count
    by_priority: dict[str, int]  # Priority -> Count
    period_start: str
    period_end: str


class DocumentMetrics(BaseModel):
    """Document processing metrics."""

    total_documents: int
    pending_review: int
    reviewed_documents: int
    approved_documents: int
    rejected_documents: int
    average_review_time_hours: float
    by_type: dict[str, int]  # Document type -> Count
    period_start: str
    period_end: str


class StaffProductivityMetrics(BaseModel):
    """Staff productivity metrics."""

    user_id: UUID
    user_name: str
    tasks_assigned: int
    tasks_completed: int
    messages_sent: int
    patients_handled: int
    documents_processed: int
    period_start: str
    period_end: str


# ============================================================================
# Trend Analysis
# ============================================================================


class TimeSeriesDataPoint(BaseModel):
    """Time series data point."""

    date: str
    value: float
    label: Optional[str] = None


class TrendAnalysis(BaseModel):
    """Trend analysis data."""

    metric_name: str
    data_points: list[TimeSeriesDataPoint]
    trend_direction: str  # "up", "down", "stable"
    trend_percentage: float
    period_start: str
    period_end: str


# ============================================================================
# Dashboard Metrics
# ============================================================================


class OverviewDashboardMetrics(BaseModel):
    """Overview dashboard metrics."""

    revenue_today: float
    revenue_this_month: float
    appointments_today: int
    appointments_this_week: int
    pending_tasks: int
    overdue_tasks: int
    unread_messages: int
    pending_claims: int
    outstanding_balance: float
    new_patients_this_month: int


class FinancialDashboardMetrics(BaseModel):
    """Financial dashboard metrics."""

    revenue: RevenueMetrics
    payments: PaymentMetrics
    claims: ClaimMetrics
    revenue_trend: list[TimeSeriesDataPoint]
    top_payers: list[dict]  # Top insurance payers
    aging_report: dict[str, float]  # Age bucket -> Amount


class ClinicalDashboardMetrics(BaseModel):
    """Clinical dashboard metrics."""

    appointments: AppointmentMetrics
    patients: PatientMetrics
    providers: list[ProviderMetrics]
    appointment_trend: list[TimeSeriesDataPoint]
    top_diagnoses: list[dict]
    quality_measures: dict[str, float]


class OperationalDashboardMetrics(BaseModel):
    """Operational dashboard metrics."""

    tasks: TaskMetrics
    documents: DocumentMetrics
    staff_productivity: list[StaffProductivityMetrics]
    task_completion_trend: list[TimeSeriesDataPoint]
    workflow_efficiency: dict[str, float]


# ============================================================================
# Export Schemas
# ============================================================================


class ExportRequest(BaseModel):
    """Request to export analytics data."""

    metric_type: str = Field(..., max_length=100)
    format: str = Field("csv", pattern=r"^(csv|excel|json)$")
    date_range: DateRange
    filters: Optional[dict] = None
    include_charts: bool = False


class ExportResponse(BaseModel):
    """Response after export."""

    export_id: UUID
    file_path: str
    file_size: int
    format: str
    expires_at: str
    download_url: Optional[str] = None


# ============================================================================
# KPI Schemas
# ============================================================================


class KPIMetric(BaseModel):
    """Key Performance Indicator metric."""

    name: str
    value: float
    unit: str  # e.g., "$", "%", "count"
    target: Optional[float] = None
    comparison_value: Optional[float] = None
    comparison_period: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    trend_percentage: Optional[float] = None
    status: Optional[str] = None  # "good", "warning", "critical"


class KPIDashboard(BaseModel):
    """KPI dashboard with multiple metrics."""

    category: str  # "financial", "clinical", "operational"
    metrics: list[KPIMetric]
    period_start: str
    period_end: str
    last_updated: str
