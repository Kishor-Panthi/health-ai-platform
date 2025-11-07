"""Practice model."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Practice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Multi-tenant practice entity."""

    __tablename__ = 'practices'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    timezone: Mapped[str] = mapped_column(String(64), default='UTC', nullable=False)
    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(128))
    state: Mapped[str | None] = mapped_column(String(64))
    postal_code: Mapped[str | None] = mapped_column(String(32))

    # Relationships
    users = relationship('User', back_populates='practice', cascade='all,delete-orphan')
    patients = relationship('Patient', back_populates='practice', cascade='all,delete-orphan')
    appointments = relationship('Appointment', back_populates='practice', cascade='all,delete-orphan')
    providers = relationship('Provider', back_populates='practice', cascade='all,delete-orphan')
    staff = relationship('Staff', back_populates='practice', cascade='all,delete-orphan')

    def __repr__(self) -> str:
        return f"<Practice(id={self.id}, name={self.name}, domain={self.domain})>"
