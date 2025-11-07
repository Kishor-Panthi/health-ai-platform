"""Service for report operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.reports import ReportCreate, ReportScheduleCreate, ReportScheduleUpdate, ReportUpdate
from app.models.report import Report, ReportFormat, ReportStatus, ReportType
from app.models.report_schedule import ReportSchedule, ScheduleStatus


class ReportService:
    """Service for managing reports."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ============================================================================
    # Report CRUD Operations
    # ============================================================================

    async def create_report(
        self,
        report_in: ReportCreate,
        created_by_user_id: UUID,
    ) -> Report:
        """Create a new report."""
        report = Report(
            practice_id=self.practice_id,
            report_type=report_in.report_type,
            name=report_in.name,
            description=report_in.description,
            parameters=report_in.parameters,
            columns=report_in.columns,
            sort_by=report_in.sort_by,
            sort_order=report_in.sort_order,
            status=ReportStatus.PENDING,
            format=report_in.format,
            created_by_user_id=created_by_user_id,
            expires_at=report_in.expires_at,
            is_shared=report_in.is_shared,
            shared_with_users=report_in.shared_with_users,
            is_template=report_in.is_template,
            template_name=report_in.template_name,
            metadata=report_in.metadata,
            download_count=0,
        )

        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def get_report(self, report_id: UUID) -> Optional[Report]:
        """Get report by ID."""
        result = await self.db.execute(
            select(Report).where(
                and_(
                    Report.id == report_id,
                    Report.practice_id == self.practice_id,
                    Report.is_deleted == False,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_report(
        self, report_id: UUID, report_in: ReportUpdate
    ) -> Optional[Report]:
        """Update report."""
        report = await self.get_report(report_id)
        if not report:
            return None

        update_data = report_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(report, field, value)

        report.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def delete_report(self, report_id: UUID) -> bool:
        """Soft delete report."""
        report = await self.get_report(report_id)
        if not report:
            return False

        report.is_deleted = True
        report.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        return True

    # ============================================================================
    # Report Execution
    # ============================================================================

    async def execute_report(self, report_id: UUID) -> Optional[Report]:
        """Execute a report (start execution)."""
        report = await self.get_report(report_id)
        if not report:
            return None

        report.status = ReportStatus.RUNNING
        report.started_at = datetime.utcnow().isoformat()
        report.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def complete_report(
        self,
        report_id: UUID,
        result_count: int,
        file_path: str,
        file_size: int,
        storage_backend: str = "local",
        bucket_name: Optional[str] = None,
    ) -> Optional[Report]:
        """Mark report as completed with results."""
        report = await self.get_report(report_id)
        if not report:
            return None

        now = datetime.utcnow().isoformat()
        report.status = ReportStatus.COMPLETED
        report.completed_at = now
        report.result_count = result_count
        report.file_path = file_path
        report.file_size = file_size
        report.storage_backend = storage_backend
        report.bucket_name = bucket_name

        # Calculate execution time
        if report.started_at:
            try:
                started = datetime.fromisoformat(report.started_at)
                completed = datetime.fromisoformat(now)
                execution_time = (completed - started).total_seconds() * 1000
                report.execution_time_ms = int(execution_time)
            except (ValueError, TypeError):
                pass

        report.updated_at = now
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def fail_report(
        self, report_id: UUID, error_message: str
    ) -> Optional[Report]:
        """Mark report as failed."""
        report = await self.get_report(report_id)
        if not report:
            return None

        report.status = ReportStatus.FAILED
        report.error_message = error_message
        report.completed_at = datetime.utcnow().isoformat()
        report.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def record_download(self, report_id: UUID) -> Optional[Report]:
        """Record report download."""
        report = await self.get_report(report_id)
        if not report:
            return None

        report.download_count += 1
        report.last_downloaded_at = datetime.utcnow().isoformat()
        report.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(report)
        return report

    # ============================================================================
    # Query Operations
    # ============================================================================

    async def list_reports(
        self,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        format: Optional[ReportFormat] = None,
        created_by_user_id: Optional[UUID] = None,
        templates_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Report], int]:
        """List reports with filters."""
        conditions = [
            Report.practice_id == self.practice_id,
            Report.is_deleted == False,
        ]

        if report_type:
            conditions.append(Report.report_type == report_type)
        if status:
            conditions.append(Report.status == status)
        if format:
            conditions.append(Report.format == format)
        if created_by_user_id:
            conditions.append(Report.created_by_user_id == created_by_user_id)
        if templates_only:
            conditions.append(Report.is_template == True)

        # Count query
        count_query = select(func.count()).select_from(Report).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Report)
            .where(and_(*conditions))
            .order_by(Report.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        reports = result.scalars().all()
        return list(reports), total

    # ============================================================================
    # Report Schedule Operations
    # ============================================================================

    async def create_schedule(
        self,
        schedule_in: ReportScheduleCreate,
        created_by_user_id: UUID,
    ) -> ReportSchedule:
        """Create a report schedule."""
        schedule = ReportSchedule(
            practice_id=self.practice_id,
            name=schedule_in.name,
            description=schedule_in.description,
            report_type=schedule_in.report_type,
            report_format=schedule_in.report_format,
            report_parameters=schedule_in.report_parameters,
            frequency=schedule_in.frequency,
            cron_expression=schedule_in.cron_expression,
            day_of_week=schedule_in.day_of_week,
            day_of_month=schedule_in.day_of_month,
            time_of_day=schedule_in.time_of_day,
            timezone=schedule_in.timezone,
            status=ScheduleStatus.ACTIVE,
            is_enabled=True,
            created_by_user_id=created_by_user_id,
            delivery_method=schedule_in.delivery_method,
            email_recipients=schedule_in.email_recipients,
            email_subject=schedule_in.email_subject,
            email_body=schedule_in.email_body,
            retention_days=schedule_in.retention_days,
            auto_delete_old_reports=schedule_in.auto_delete_old_reports,
            metadata=schedule_in.metadata,
            total_runs=0,
            successful_runs=0,
            failed_runs=0,
        )

        self.db.add(schedule)
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule

    async def get_schedule(self, schedule_id: UUID) -> Optional[ReportSchedule]:
        """Get schedule by ID."""
        result = await self.db.execute(
            select(ReportSchedule).where(
                and_(
                    ReportSchedule.id == schedule_id,
                    ReportSchedule.practice_id == self.practice_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_schedule(
        self, schedule_id: UUID, schedule_in: ReportScheduleUpdate
    ) -> Optional[ReportSchedule]:
        """Update report schedule."""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        update_data = schedule_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        schedule.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule

    async def get_due_schedules(self, limit: int = 100) -> list[ReportSchedule]:
        """Get schedules that are due to run."""
        now = datetime.utcnow().isoformat()

        query = (
            select(ReportSchedule)
            .where(
                and_(
                    ReportSchedule.practice_id == self.practice_id,
                    ReportSchedule.status == ScheduleStatus.ACTIVE,
                    ReportSchedule.is_enabled == True,
                    ReportSchedule.next_run_at.isnot(None),
                    ReportSchedule.next_run_at <= now,
                )
            )
            .order_by(ReportSchedule.next_run_at.asc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ============================================================================
    # Statistics
    # ============================================================================

    async def get_report_stats(self) -> dict:
        """Get report statistics."""
        conditions = [
            Report.practice_id == self.practice_id,
            Report.is_deleted == False,
        ]

        # Total count
        total_query = select(func.count()).select_from(Report).where(and_(*conditions))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar_one()

        # By status
        status_query = (
            select(Report.status, func.count().label("count"))
            .where(and_(*conditions))
            .group_by(Report.status)
        )
        status_result = await self.db.execute(status_query)
        status_counts = {row.status.value: row.count for row in status_result}

        # By type
        type_query = (
            select(Report.report_type, func.count().label("count"))
            .where(and_(*conditions))
            .group_by(Report.report_type)
        )
        type_result = await self.db.execute(type_query)
        type_counts = {row.report_type.value: row.count for row in type_result}

        # By format
        format_query = (
            select(Report.format, func.count().label("count"))
            .where(and_(*conditions))
            .group_by(Report.format)
        )
        format_result = await self.db.execute(format_query)
        format_counts = {row.format.value: row.count for row in format_result}

        # Total downloads
        downloads_query = select(func.sum(Report.download_count)).where(and_(*conditions))
        downloads_result = await self.db.execute(downloads_query)
        total_downloads = downloads_result.scalar_one() or 0

        return {
            "total_reports": total,
            "completed_reports": status_counts.get("completed", 0),
            "running_reports": status_counts.get("running", 0),
            "failed_reports": status_counts.get("failed", 0),
            "total_downloads": total_downloads,
            "by_type": type_counts,
            "by_format": format_counts,
        }
