"""User model representing staff/providers."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    """User roles for authentication and basic permissions."""

    ADMIN = 'admin'
    PROVIDER = 'provider'
    STAFF = 'staff'


class User(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """User account for authentication and authorization."""

    __tablename__ = 'users'

    __table_args__ = (
        UniqueConstraint('practice_id', 'email', name='uq_users_practice_email'),
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.STAFF,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    practice = relationship('Practice', back_populates='users')
    appointments = relationship('Appointment', back_populates='provider')

    # Extended profiles (one-to-one relationships)
    provider = relationship(
        'Provider',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )
    staff = relationship(
        'Staff',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    # Communications relationships
    sent_messages = relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    received_messages = relationship('Message', foreign_keys='Message.recipient_user_id', back_populates='recipient_user')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    assigned_tasks = relationship('Task', foreign_keys='Task.assigned_to_user_id', back_populates='assigned_to_user')

    # Analytics relationships
    dashboards = relationship('Dashboard', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def is_provider(self) -> bool:
        """Check if user is a provider."""
        return self.role == UserRole.PROVIDER and self.provider is not None

    @property
    def is_staff_member(self) -> bool:
        """Check if user is a staff member."""
        return self.role == UserRole.STAFF and self.staff is not None

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
