"""API endpoints for dashboard management."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.dashboards import (
    Dashboard,
    DashboardCreate,
    DashboardSummary,
    DashboardUpdate,
    DashboardWithComputedFields,
)
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter()


# ============================================================================
# Dashboard CRUD Endpoints
# ============================================================================


@router.post("/", response_model=Dashboard, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    dashboard_in: DashboardCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new dashboard."""
    service = DashboardService(db, current_user.practice_id)
    dashboard = await service.create_dashboard(dashboard_in, current_user.id)
    await db.commit()
    return dashboard


@router.get("/", response_model=PaginatedResponse[DashboardSummary])
async def list_dashboards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """List dashboards for current user."""
    service = DashboardService(db, current_user.practice_id)
    dashboards, total = await service.list_user_dashboards(
        current_user.id,
        skip,
        limit,
    )

    summaries = [
        DashboardSummary(
            id=d.id,
            name=d.name,
            dashboard_type=d.dashboard_type,
            widget_count=d.widget_count,
            is_default=d.is_default,
            is_shared=d.is_shared,
            view_count=d.view_count,
            last_viewed_at=d.last_viewed_at,
            created_at=d.created_at,
        )
        for d in dashboards
    ]

    return PaginatedResponse(
        items=summaries,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/{dashboard_id}", response_model=DashboardWithComputedFields)
async def get_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific dashboard."""
    service = DashboardService(db, current_user.practice_id)
    dashboard = await service.get_dashboard(dashboard_id)

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Record view
    await service.record_view(dashboard_id)
    await db.commit()

    return DashboardWithComputedFields(
        **dashboard.__dict__,
        widget_count=dashboard.widget_count,
        is_shared=dashboard.is_shared,
    )


@router.patch("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(
    dashboard_id: UUID,
    dashboard_in: DashboardUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update dashboard."""
    service = DashboardService(db, current_user.practice_id)
    dashboard = await service.get_dashboard(dashboard_id)

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Verify ownership
    if dashboard.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    dashboard = await service.update_dashboard(dashboard_id, dashboard_in)
    await db.commit()
    return dashboard


@router.delete("/{dashboard_id}", response_model=SuccessResponse)
async def delete_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a dashboard."""
    service = DashboardService(db, current_user.practice_id)
    dashboard = await service.get_dashboard(dashboard_id)

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Verify ownership
    if dashboard.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    deleted = await service.delete_dashboard(dashboard_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    await db.commit()
    return SuccessResponse(message="Dashboard deleted successfully")
