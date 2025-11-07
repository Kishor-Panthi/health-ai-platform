"""Pydantic schemas for dashboards."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.dashboard import DashboardType, RefreshInterval, WidgetType


# ============================================================================
# Dashboard Widget Schemas
# ============================================================================


class WidgetConfigBase(BaseModel):
    """Base widget configuration."""

    widget_type: WidgetType
    title: str = Field(..., max_length=255)
    data_source: str = Field(..., max_length=255)
    config: dict
    width: int = Field(4, ge=1, le=12)
    height: int = Field(4, ge=1, le=12)
    position_x: int = Field(0, ge=0)
    position_y: int = Field(0, ge=0)
    refresh_interval: Optional[int] = Field(None, description="Refresh interval in seconds")


class WidgetConfig(WidgetConfigBase):
    """Widget configuration for dashboard."""

    id: str  # Widget instance ID within dashboard


class DashboardWidgetBase(BaseModel):
    """Base dashboard widget template schema."""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    widget_type: WidgetType
    data_source: str = Field(..., max_length=255)
    config: dict
    default_width: int = Field(4, ge=1, le=12)
    default_height: int = Field(4, ge=1, le=12)
    min_width: int = Field(2, ge=1, le=12)
    min_height: int = Field(2, ge=1, le=12)
    required_permissions: Optional[list[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    metadata: Optional[dict] = None


class DashboardWidgetCreate(DashboardWidgetBase):
    """Schema for creating a dashboard widget template."""

    pass


class DashboardWidget(DashboardWidgetBase):
    """Complete dashboard widget template schema."""

    id: UUID
    is_template: bool
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Dashboard Schemas
# ============================================================================


class DashboardBase(BaseModel):
    """Base dashboard schema."""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    dashboard_type: DashboardType
    widgets: list[WidgetConfig] = Field(default_factory=list)
    layout: Optional[dict] = None
    theme: Optional[str] = Field(None, max_length=50)
    refresh_interval: RefreshInterval = RefreshInterval.EVERY_5_MINUTES
    auto_refresh: bool = True
    is_public: bool = False
    shared_with_users: Optional[list[UUID]] = None
    shared_with_roles: Optional[list[str]] = None
    is_default: bool = False
    sort_order: int = 0
    metadata: Optional[dict] = None


class DashboardCreate(DashboardBase):
    """Schema for creating a dashboard."""

    pass


class DashboardUpdate(BaseModel):
    """Schema for updating a dashboard."""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    widgets: Optional[list[WidgetConfig]] = None
    layout: Optional[dict] = None
    theme: Optional[str] = Field(None, max_length=50)
    refresh_interval: Optional[RefreshInterval] = None
    auto_refresh: Optional[bool] = None
    is_public: Optional[bool] = None
    shared_with_users: Optional[list[UUID]] = None
    shared_with_roles: Optional[list[str]] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None
    metadata: Optional[dict] = None


class Dashboard(DashboardBase):
    """Complete dashboard schema."""

    id: UUID
    practice_id: UUID
    user_id: Optional[UUID]
    is_template: bool
    view_count: int
    last_viewed_at: Optional[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class DashboardWithComputedFields(Dashboard):
    """Dashboard with computed properties."""

    widget_count: int
    is_shared: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Dashboard Action Schemas
# ============================================================================


class AddWidgetRequest(BaseModel):
    """Request to add widget to dashboard."""

    widget: WidgetConfig


class RemoveWidgetRequest(BaseModel):
    """Request to remove widget from dashboard."""

    widget_id: str


class UpdateWidgetRequest(BaseModel):
    """Request to update widget in dashboard."""

    widget_id: str
    widget: WidgetConfig


class UpdateLayoutRequest(BaseModel):
    """Request to update dashboard layout."""

    layout: dict


class CloneDashboardRequest(BaseModel):
    """Request to clone a dashboard."""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None


# ============================================================================
# Widget Data Schemas
# ============================================================================


class WidgetDataRequest(BaseModel):
    """Request for widget data."""

    widget_id: str
    widget_type: WidgetType
    data_source: str
    config: dict
    date_range: Optional[dict] = None


class WidgetDataResponse(BaseModel):
    """Response with widget data."""

    widget_id: str
    data: dict
    last_updated: str
    next_refresh: Optional[str] = None


# ============================================================================
# Dashboard Templates
# ============================================================================


class DashboardTemplate(BaseModel):
    """Dashboard template schema."""

    id: UUID
    name: str
    description: Optional[str]
    dashboard_type: DashboardType
    widget_count: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class CreateFromTemplateRequest(BaseModel):
    """Request to create dashboard from template."""

    template_id: UUID
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


# ============================================================================
# Query Schemas
# ============================================================================


class DashboardSummary(BaseModel):
    """Summary of dashboard for listings."""

    id: UUID
    name: str
    dashboard_type: DashboardType
    widget_count: int
    is_default: bool
    is_shared: bool
    view_count: int
    last_viewed_at: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    """Dashboard statistics."""

    total_dashboards: int
    by_type: dict[str, int]
    total_widgets: int
    most_viewed_dashboard_id: Optional[UUID]
    total_views: int
