"\"\"\"Patient model.\""

from __future__ import annotations

import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.encryption import EncryptedString
from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class PatientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Patient(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    __table_args__ = (
        UniqueConstraint("practice_id", "mrn", name="uq_patients_practice_mrn"),
    )

    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    mrn: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    dob: Mapped[date | None] = mapped_column(Date())
    gender: Mapped[str | None] = mapped_column(String(32))
    ssn: Mapped[str | None] = mapped_column(EncryptedString(255))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(32))
    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(128))
    state: Mapped[str | None] = mapped_column(String(64))
    postal_code: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[PatientStatus] = mapped_column(Enum(PatientStatus), default=PatientStatus.ACTIVE, nullable=False)
    primary_provider_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    practice = relationship('Practice', back_populates='patients')
    appointments = relationship('Appointment', back_populates='patient')

    # Medical records relationships
    allergies = relationship('MedicalAllergy', back_populates='patient', cascade='all, delete-orphan')
    medications = relationship('MedicalMedication', back_populates='patient', cascade='all, delete-orphan')
    conditions = relationship('MedicalCondition', back_populates='patient', cascade='all, delete-orphan')
    immunizations = relationship('MedicalImmunization', back_populates='patient', cascade='all, delete-orphan')
    vitals = relationship('MedicalVitals', back_populates='patient', cascade='all, delete-orphan')

    # Insurance relationships
    insurance_policies = relationship('InsurancePolicy', back_populates='patient', cascade='all, delete-orphan')

    # Billing relationships
    billing_claims = relationship('BillingClaim', back_populates='patient', cascade='all, delete-orphan')
    billing_payments = relationship('BillingPayment', back_populates='patient', cascade='all, delete-orphan')
    billing_transactions = relationship('BillingTransaction', back_populates='patient', cascade='all, delete-orphan')

    # Clinical documentation relationships
    clinical_notes = relationship('ClinicalNote', back_populates='patient', cascade='all, delete-orphan')
    documents = relationship('Document', back_populates='patient', cascade='all, delete-orphan')
