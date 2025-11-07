"""Provider schedule model for availability management."""

from __future__ import annotations

import enum
from datetime import time

from sqlalchemy import String, Boolean, ForeignKey, Enum, Time, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DayOfWeek(int, enum.Enum):
    """Days of the week (0=Monday, 6=Sunday)."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class ProviderSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Provider availability schedule by day of week."""

    __tablename__ = 'provider_schedules'

    # Provider reference
    provider_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('providers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Day and time
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='0=Monday, 6=Sunday'
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Location and availability
    location: Mapped[str | None] = mapped_column(
        String(255),
        comment='Office location, room number, or clinic name'
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment='Whether provider is accepting appointments during this time'
    )

    # Appointment settings
    slot_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        comment='Default appointment duration in minutes'
    )
    max_patients_per_slot: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment='Maximum number of patients that can be scheduled in one slot'
    )

    # Break times
    lunch_break_start: Mapped[time | None] = mapped_column(Time)
    lunch_break_end: Mapped[time | None] = mapped_column(Time)

    # Notes
    notes: Mapped[str | None] = mapped_column(
        String(500),
        comment='Special notes about this schedule block'
    )

    # Effective dates (for temporary schedule changes)
    effective_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Start date for this schedule (YYYY-MM-DD), null means permanent'
    )
    expiration_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='End date for this schedule (YYYY-MM-DD), null means no expiration'
    )

    # Relationships
    provider = relationship('Provider', back_populates='schedules')

    def __repr__(self) -> str:
        day_name = DayOfWeek(self.day_of_week).name
        return f"<ProviderSchedule(provider_id={self.provider_id}, day={day_name}, {self.start_time}-{self.end_time})>"

    @property
    def day_name(self) -> str:
        """Get the day of week name."""
        return DayOfWeek(self.day_of_week).name

    @property
    def duration_minutes(self) -> int:
        """Calculate schedule duration in minutes."""
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            return end_minutes - start_minutes
        return 0

    def is_time_in_schedule(self, check_time: time) -> bool:
        """Check if a given time falls within this schedule."""
        return self.start_time <= check_time <= self.end_time

    def is_lunch_break(self, check_time: time) -> bool:
        """Check if a given time falls within lunch break."""
        if self.lunch_break_start and self.lunch_break_end:
            return self.lunch_break_start <= check_time <= self.lunch_break_end
        return False
