"""Service for analytics operations."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.models.billing_claim import BillingClaim, ClaimStatus
from app.models.billing_payment import BillingPayment
from app.models.patient import Patient
from app.models.task import Task, TaskStatus


class AnalyticsService:
    """Service for analytics and metrics."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    async def get_revenue_metrics(self, start_date: str, end_date: str) -> dict:
        """Get revenue metrics for date range."""
        # Simplified revenue calculation from payments
        query = select(
            func.count(BillingPayment.id).label("count"),
            func.sum(BillingPayment.amount).label("total"),
        ).where(
            and_(
                BillingPayment.practice_id == self.practice_id,
                BillingPayment.payment_date >= start_date,
                BillingPayment.payment_date <= end_date,
            )
        )

        result = await self.db.execute(query)
        row = result.one()

        return {
            "total_payments": row.count or 0,
            "total_revenue": float(row.total or 0),
            "period_start": start_date,
            "period_end": end_date,
        }

    async def get_appointment_metrics(self, start_date: str, end_date: str) -> dict:
        """Get appointment metrics for date range."""
        query = (
            select(
                func.count(Appointment.id).label("total"),
                Appointment.status,
            )
            .where(
                and_(
                    Appointment.practice_id == self.practice_id,
                    Appointment.appointment_date >= start_date,
                    Appointment.appointment_date <= end_date,
                )
            )
            .group_by(Appointment.status)
        )

        result = await self.db.execute(query)
        status_counts = {row.status.value: row.total for row in result}

        total = sum(status_counts.values())
        completed = status_counts.get("completed", 0)

        return {
            "total_appointments": total,
            "completed_appointments": completed,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "by_status": status_counts,
            "period_start": start_date,
            "period_end": end_date,
        }

    async def get_patient_metrics(self, start_date: str, end_date: str) -> dict:
        """Get patient metrics."""
        total_query = select(func.count(Patient.id)).where(
            Patient.practice_id == self.practice_id
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar_one()

        new_query = select(func.count(Patient.id)).where(
            and_(
                Patient.practice_id == self.practice_id,
                Patient.created_at >= start_date,
                Patient.created_at <= end_date,
            )
        )
        new_result = await self.db.execute(new_query)
        new_patients = new_result.scalar_one()

        return {
            "total_patients": total,
            "new_patients": new_patients,
            "period_start": start_date,
            "period_end": end_date,
        }

    async def get_task_metrics(self, start_date: str, end_date: str) -> dict:
        """Get task metrics for date range."""
        query = (
            select(
                func.count(Task.id).label("total"),
                Task.status,
            )
            .where(
                and_(
                    Task.practice_id == self.practice_id,
                    Task.is_deleted == False,
                    Task.created_at >= start_date,
                    Task.created_at <= end_date,
                )
            )
            .group_by(Task.status)
        )

        result = await self.db.execute(query)
        status_counts = {row.status.value: row.total for row in result}

        total = sum(status_counts.values())
        completed = status_counts.get("completed", 0)

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "by_status": status_counts,
            "period_start": start_date,
            "period_end": end_date,
        }

    async def get_claim_metrics(self, start_date: str, end_date: str) -> dict:
        """Get claims metrics for date range."""
        query = (
            select(
                func.count(BillingClaim.id).label("total"),
                BillingClaim.status,
            )
            .where(
                and_(
                    BillingClaim.practice_id == self.practice_id,
                    BillingClaim.service_date_from >= start_date,
                    BillingClaim.service_date_from <= end_date,
                )
            )
            .group_by(BillingClaim.status)
        )

        result = await self.db.execute(query)
        status_counts = {row.status.value: row.total for row in result}

        total = sum(status_counts.values())
        accepted = status_counts.get("accepted", 0)

        return {
            "total_claims": total,
            "accepted_claims": accepted,
            "acceptance_rate": (accepted / total * 100) if total > 0 else 0,
            "by_status": status_counts,
            "period_start": start_date,
            "period_end": end_date,
        }
