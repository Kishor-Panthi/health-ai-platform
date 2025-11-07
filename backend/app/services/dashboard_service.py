"""Service for dashboard operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.dashboards import DashboardCreate, DashboardUpdate
from app.models.dashboard import Dashboard, DashboardType


class DashboardService:
    """Service for managing dashboards."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    async def create_dashboard(
        self, dashboard_in: DashboardCreate, user_id: Optional[UUID] = None
    ) -> Dashboard:
        """Create a new dashboard."""
        dashboard = Dashboard(
            practice_id=self.practice_id,
            user_id=user_id,
            name=dashboard_in.name,
            description=dashboard_in.description,
            dashboard_type=dashboard_in.dashboard_type,
            widgets=dashboard_in.widgets,
            layout=dashboard_in.layout,
            theme=dashboard_in.theme,
            refresh_interval=dashboard_in.refresh_interval,
            auto_refresh=dashboard_in.auto_refresh,
            is_public=dashboard_in.is_public,
            shared_with_users=dashboard_in.shared_with_users,
            shared_with_roles=dashboard_in.shared_with_roles,
            is_default=dashboard_in.is_default,
            is_template=False,
            view_count=0,
            sort_order=dashboard_in.sort_order,
            metadata=dashboard_in.metadata,
        )

        self.db.add(dashboard)
        await self.db.flush()
        await self.db.refresh(dashboard)
        return dashboard

    async def get_dashboard(self, dashboard_id: UUID) -> Optional[Dashboard]:
        """Get dashboard by ID."""
        result = await self.db.execute(
            select(Dashboard).where(
                and_(
                    Dashboard.id == dashboard_id,
                    Dashboard.practice_id == self.practice_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_dashboard(
        self, dashboard_id: UUID, dashboard_in: DashboardUpdate
    ) -> Optional[Dashboard]:
        """Update dashboard."""
        dashboard = await self.get_dashboard(dashboard_id)
        if not dashboard:
            return None

        update_data = dashboard_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dashboard, field, value)

        dashboard.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        await self.db.refresh(dashboard)
        return dashboard

    async def delete_dashboard(self, dashboard_id: UUID) -> bool:
        """Delete dashboard."""
        dashboard = await self.get_dashboard(dashboard_id)
        if not dashboard:
            return False

        await self.db.delete(dashboard)
        await self.db.flush()
        return True

    async def list_user_dashboards(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Dashboard], int]:
        """List dashboards for a user."""
        conditions = [
            Dashboard.practice_id == self.practice_id,
            or_(
                Dashboard.user_id == user_id,
                Dashboard.is_public == True,
            ),
        ]

        count_query = select(func.count()).select_from(Dashboard).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = (
            select(Dashboard)
            .where(and_(*conditions))
            .order_by(Dashboard.sort_order.asc(), Dashboard.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        dashboards = result.scalars().all()
        return list(dashboards), total

    async def record_view(self, dashboard_id: UUID) -> Optional[Dashboard]:
        """Record dashboard view."""
        dashboard = await self.get_dashboard(dashboard_id)
        if not dashboard:
            return None

        dashboard.view_count += 1
        dashboard.last_viewed_at = datetime.utcnow().isoformat()
        dashboard.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(dashboard)
        return dashboard
