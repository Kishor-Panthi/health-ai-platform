"""API endpoints for reports and analytics."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.analytics import (
    AppointmentMetrics,
    ClaimMetrics,
    DateRange,
    OverviewDashboardMetrics,
    PatientMetrics,
    RevenueMetrics,
    TaskMetrics,
)
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.reports import (
    ExecuteReportRequest,
    ExecuteReportResponse,
    Report,
    ReportCreate,
    ReportSchedule,
    ReportScheduleCreate,
    ReportScheduleUpdate,
    ReportStats,
    ReportSummary,
    ReportUpdate,
    ReportWithComputedFields,
)
from app.models.report import ReportFormat, ReportStatus, ReportType
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService

router = APIRouter()


# ============================================================================
# Report CRUD Endpoints
# ============================================================================


@router.post("/", response_model=Report, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_in: ReportCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new report."""
    service = ReportService(db, current_user.practice_id)
    report = await service.create_report(report_in, current_user.id)
    await db.commit()
    return report


@router.get("/", response_model=PaginatedResponse[ReportSummary])
async def list_reports(
    report_type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None,
    format: Optional[ReportFormat] = None,
    templates_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """List reports."""
    service = ReportService(db, current_user.practice_id)
    reports, total = await service.list_reports(
        report_type=report_type,
        status=status,
        format=format,
        created_by_user_id=current_user.id if not templates_only else None,
        templates_only=templates_only,
        skip=skip,
        limit=limit,
    )

    summaries = [
        ReportSummary(
            id=r.id,
            report_type=r.report_type,
            name=r.name,
            status=r.status,
            format=r.format,
            result_count=r.result_count,
            execution_time_ms=r.execution_time_ms,
            created_at=r.created_at,
            completed_at=r.completed_at,
        )
        for r in reports
    ]

    return PaginatedResponse(
        items=summaries,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/{report_id}", response_model=ReportWithComputedFields)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific report."""
    service = ReportService(db, current_user.practice_id)
    report = await service.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportWithComputedFields(
        **report.__dict__,
        is_completed=report.is_completed,
        is_running=report.is_running,
        is_failed=report.is_failed,
        file_size_mb=report.file_size_mb,
        is_expired=report.is_expired,
    )


@router.patch("/{report_id}", response_model=Report)
async def update_report(
    report_id: UUID,
    report_in: ReportUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update report."""
    service = ReportService(db, current_user.practice_id)
    report = await service.update_report(report_id, report_in)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    await db.commit()
    return report


@router.delete("/{report_id}", response_model=SuccessResponse)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a report."""
    service = ReportService(db, current_user.practice_id)
    deleted = await service.delete_report(report_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")

    await db.commit()
    return SuccessResponse(message="Report deleted successfully")


# ============================================================================
# Report Execution Endpoints
# ============================================================================


@router.post("/{report_id}/execute", response_model=ExecuteReportResponse)
async def execute_report(
    report_id: UUID,
    execute_request: ExecuteReportRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Execute a report."""
    service = ReportService(db, current_user.practice_id)
    report = await service.execute_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    await db.commit()

    return ExecuteReportResponse(
        report_id=report.id,
        status=report.status,
    )


# ============================================================================
# Report Schedule Endpoints
# ============================================================================


@router.post("/schedules", response_model=ReportSchedule, status_code=status.HTTP_201_CREATED)
async def create_report_schedule(
    schedule_in: ReportScheduleCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a report schedule."""
    service = ReportService(db, current_user.practice_id)
    schedule = await service.create_schedule(schedule_in, current_user.id)
    await db.commit()
    return schedule


@router.get("/schedules/{schedule_id}", response_model=ReportSchedule)
async def get_report_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a report schedule."""
    service = ReportService(db, current_user.practice_id)
    schedule = await service.get_schedule(schedule_id)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedule


@router.patch("/schedules/{schedule_id}", response_model=ReportSchedule)
async def update_report_schedule(
    schedule_id: UUID,
    schedule_in: ReportScheduleUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a report schedule."""
    service = ReportService(db, current_user.practice_id)
    schedule = await service.update_schedule(schedule_id, schedule_in)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await db.commit()
    return schedule


# ============================================================================
# Statistics Endpoints
# ============================================================================


@router.get("/stats/summary", response_model=ReportStats)
async def get_report_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get report statistics."""
    service = ReportService(db, current_user.practice_id)
    stats = await service.get_report_stats()

    return ReportStats(
        total_reports=stats["total_reports"],
        completed_reports=stats["completed_reports"],
        running_reports=stats["running_reports"],
        failed_reports=stats["failed_reports"],
        total_downloads=stats["total_downloads"],
        by_type=stats["by_type"],
        by_format=stats["by_format"],
    )


# ============================================================================
# Analytics Endpoints
# ============================================================================


@router.post("/analytics/revenue", response_model=RevenueMetrics)
async def get_revenue_metrics(
    date_range: DateRange,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get revenue metrics."""
    service = AnalyticsService(db, current_user.practice_id)
    metrics = await service.get_revenue_metrics(
        date_range.start_date,
        date_range.end_date,
    )

    return RevenueMetrics(
        total_revenue=metrics["total_revenue"],
        total_charges=0,  # Placeholder
        total_payments=metrics["total_revenue"],
        total_adjustments=0,  # Placeholder
        outstanding_balance=0,  # Placeholder
        collection_rate=100.0,  # Placeholder
        average_revenue_per_patient=0,  # Placeholder
        period_start=metrics["period_start"],
        period_end=metrics["period_end"],
    )


@router.post("/analytics/appointments", response_model=AppointmentMetrics)
async def get_appointment_metrics(
    date_range: DateRange,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get appointment metrics."""
    service = AnalyticsService(db, current_user.practice_id)
    metrics = await service.get_appointment_metrics(
        date_range.start_date,
        date_range.end_date,
    )

    return AppointmentMetrics(
        total_appointments=metrics["total_appointments"],
        scheduled_appointments=0,  # Placeholder
        completed_appointments=metrics["completed_appointments"],
        cancelled_appointments=0,  # Placeholder
        no_show_appointments=0,  # Placeholder
        completion_rate=metrics["completion_rate"],
        no_show_rate=0.0,  # Placeholder
        cancellation_rate=0.0,  # Placeholder
        average_appointments_per_day=0.0,  # Placeholder
        period_start=metrics["period_start"],
        period_end=metrics["period_end"],
    )


@router.post("/analytics/patients", response_model=PatientMetrics)
async def get_patient_metrics(
    date_range: DateRange,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get patient metrics."""
    service = AnalyticsService(db, current_user.practice_id)
    metrics = await service.get_patient_metrics(
        date_range.start_date,
        date_range.end_date,
    )

    return PatientMetrics(
        total_patients=metrics["total_patients"],
        new_patients=metrics["new_patients"],
        active_patients=0,  # Placeholder
        inactive_patients=0,  # Placeholder
        average_age=0.0,  # Placeholder
        gender_distribution={},  # Placeholder
        insurance_distribution={},  # Placeholder
        period_start=metrics["period_start"],
        period_end=metrics["period_end"],
    )


@router.post("/analytics/tasks", response_model=TaskMetrics)
async def get_task_metrics(
    date_range: DateRange,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get task metrics."""
    service = AnalyticsService(db, current_user.practice_id)
    metrics = await service.get_task_metrics(
        date_range.start_date,
        date_range.end_date,
    )

    return TaskMetrics(
        total_tasks=metrics["total_tasks"],
        completed_tasks=metrics["completed_tasks"],
        pending_tasks=0,  # Placeholder
        overdue_tasks=0,  # Placeholder
        completion_rate=metrics["completion_rate"],
        average_completion_time_hours=0.0,  # Placeholder
        by_type={},  # Placeholder
        by_priority={},  # Placeholder
        period_start=metrics["period_start"],
        period_end=metrics["period_end"],
    )


@router.post("/analytics/claims", response_model=ClaimMetrics)
async def get_claim_metrics(
    date_range: DateRange,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get claim metrics."""
    service = AnalyticsService(db, current_user.practice_id)
    metrics = await service.get_claim_metrics(
        date_range.start_date,
        date_range.end_date,
    )

    return ClaimMetrics(
        total_claims=metrics["total_claims"],
        submitted_claims=0,  # Placeholder
        accepted_claims=metrics["accepted_claims"],
        rejected_claims=0,  # Placeholder
        denied_claims=0,  # Placeholder
        pending_claims=0,  # Placeholder
        acceptance_rate=metrics["acceptance_rate"],
        average_claim_amount=0.0,  # Placeholder
        total_claim_value=0.0,  # Placeholder
        period_start=metrics["period_start"],
        period_end=metrics["period_end"],
    )


@router.get("/analytics/overview", response_model=OverviewDashboardMetrics)
async def get_overview_metrics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get overview dashboard metrics."""
    # Return placeholder data - would be computed from various services
    return OverviewDashboardMetrics(
        revenue_today=0.0,
        revenue_this_month=0.0,
        appointments_today=0,
        appointments_this_week=0,
        pending_tasks=0,
        overdue_tasks=0,
        unread_messages=0,
        pending_claims=0,
        outstanding_balance=0.0,
        new_patients_this_month=0,
    )
