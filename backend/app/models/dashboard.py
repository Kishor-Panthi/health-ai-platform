"""Dashboard model for user dashboard configurations."""

from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DashboardType(str, enum.Enum):
    """Dashboard type enumeration."""

    OVERVIEW = "overview"  # General overview dashboard
    CLINICAL = "clinical"  # Clinical metrics
    FINANCIAL = "financial"  # Financial metrics
    OPERATIONAL = "operational"  # Operational metrics
    PROVIDER = "provider"  # Provider-specific dashboard
    PATIENT = "patient"  # Patient-specific dashboard
    CUSTOM = "custom"  # Custom dashboard


class WidgetType(str, enum.Enum):
    """Dashboard widget type enumeration."""

    # Chart widgets
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    DONUT_CHART = "donut_chart"

    # Display widgets
    METRIC_CARD = "metric_card"  # Single metric display
    TABLE = "table"  # Data table
    LIST = "list"  # List view
    CALENDAR = "calendar"  # Calendar view
    TIMELINE = "timeline"  # Timeline view

    # Specialized widgets
    PATIENT_LIST = "patient_list"
    APPOINTMENT_SCHEDULE = "appointment_schedule"
    TASK_LIST = "task_list"
    NOTIFICATION_FEED = "notification_feed"
    REVENUE_SUMMARY = "revenue_summary"
    CLAIMS_STATUS = "claims_status"

    # Custom
    CUSTOM = "custom"


class RefreshInterval(str, enum.Enum):
    """Dashboard refresh interval enumeration."""

    REALTIME = "realtime"  # WebSocket real-time updates
    EVERY_MINUTE = "every_minute"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_HOUR = "every_hour"
    MANUAL = "manual"  # Manual refresh only


class Dashboard(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """User dashboard configurations."""

    __tablename__ = "dashboards"

    # Dashboard details
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Dashboard name")
    description: Mapped[str | None] = mapped_column(Text, comment="Dashboard description")
    dashboard_type: Mapped[DashboardType] = mapped_column(
        Enum(DashboardType), nullable=False, index=True
    )

    # Ownership
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        comment="Owner user (null for shared dashboards)",
    )

    # Layout and widgets
    widgets: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        comment="Array of widget configurations",
    )
    layout: Mapped[dict | None] = mapped_column(
        JSONB, comment="Dashboard layout configuration (grid positions, sizes)"
    )

    # Display settings
    theme: Mapped[str | None] = mapped_column(
        String(50), comment="Dashboard theme (light, dark, custom)"
    )
    refresh_interval: Mapped[RefreshInterval] = mapped_column(
        Enum(RefreshInterval), default=RefreshInterval.EVERY_5_MINUTES, nullable=False
    )
    auto_refresh: Mapped[bool] = mapped_column(
        default=True, comment="Enable automatic refresh"
    )

    # Access control
    is_public: Mapped[bool] = mapped_column(
        default=False, comment="Is dashboard public to all practice users"
    )
    shared_with_users: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of user IDs with access"
    )
    shared_with_roles: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of user roles with access"
    )

    # Defaults
    is_default: Mapped[bool] = mapped_column(
        default=False, comment="Is this the default dashboard for user"
    )
    is_template: Mapped[bool] = mapped_column(
        default=False, comment="Is this a dashboard template"
    )

    # Usage tracking
    view_count: Mapped[int] = mapped_column(default=0, comment="Number of views")
    last_viewed_at: Mapped[str | None] = mapped_column(
        String(29), comment="Last view timestamp (ISO 8601)"
    )

    # Sorting
    sort_order: Mapped[int] = mapped_column(
        default=0, comment="Display order for user's dashboards"
    )

    # Metadata
    metadata: Mapped[dict | None] = mapped_column(JSONB, comment="Additional metadata")

    # Relationships
    user = relationship("User", back_populates="dashboards")

    def __repr__(self) -> str:
        return f"<Dashboard(name={self.name}, type={self.dashboard_type})>"

    @property
    def widget_count(self) -> int:
        """Get number of widgets in dashboard."""
        if self.widgets:
            return len(self.widgets)
        return 0

    @property
    def is_shared(self) -> bool:
        """Check if dashboard is shared."""
        return self.is_public or bool(self.shared_with_users) or bool(self.shared_with_roles)


class DashboardWidget(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Dashboard widget definitions (for reusable widgets)."""

    __tablename__ = "dashboard_widgets"

    # Widget details
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Widget name")
    description: Mapped[str | None] = mapped_column(Text, comment="Widget description")
    widget_type: Mapped[WidgetType] = mapped_column(
        Enum(WidgetType), nullable=False, index=True
    )

    # Configuration
    data_source: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Data source endpoint or query"
    )
    config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, comment="Widget configuration (chart options, filters, etc.)"
    )

    # Display settings
    default_width: Mapped[int] = mapped_column(
        default=4, comment="Default grid width (1-12)"
    )
    default_height: Mapped[int] = mapped_column(
        default=4, comment="Default grid height"
    )
    min_width: Mapped[int] = mapped_column(default=2, comment="Minimum width")
    min_height: Mapped[int] = mapped_column(default=2, comment="Minimum height")

    # Permissions
    required_permissions: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of required permissions to view widget"
    )

    # Template
    is_template: Mapped[bool] = mapped_column(
        default=True, comment="Is this a widget template"
    )
    category: Mapped[str | None] = mapped_column(
        String(100), comment="Widget category for organization"
    )

    # Metadata
    metadata: Mapped[dict | None] = mapped_column(JSONB, comment="Additional metadata")

    def __repr__(self) -> str:
        return f"<DashboardWidget(name={self.name}, type={self.widget_type})>"
