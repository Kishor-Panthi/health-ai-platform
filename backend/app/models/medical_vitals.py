"""Medical vitals model for patient vital signs tracking."""

from __future__ import annotations

from sqlalchemy import String, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class MedicalVitals(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Patient vital signs record."""

    __tablename__ = 'medical_vitals'

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Measurement date/time
    measurement_date: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment='Date vitals were taken (YYYY-MM-DD)'
    )
    measurement_time: Mapped[str | None] = mapped_column(
        String(8),
        comment='Time vitals were taken (HH:MM:SS)'
    )

    # Core vital signs
    temperature: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1),
        comment='Body temperature in Fahrenheit'
    )
    temperature_method: Mapped[str | None] = mapped_column(
        String(50),
        comment='Method: oral, axillary, tympanic, rectal, temporal'
    )

    pulse: Mapped[int | None] = mapped_column(
        comment='Heart rate in beats per minute'
    )
    pulse_rhythm: Mapped[str | None] = mapped_column(
        String(50),
        comment='Rhythm: regular, irregular'
    )

    respiration_rate: Mapped[int | None] = mapped_column(
        comment='Respiratory rate in breaths per minute'
    )

    # Blood pressure
    blood_pressure_systolic: Mapped[int | None] = mapped_column(
        comment='Systolic blood pressure (mmHg)'
    )
    blood_pressure_diastolic: Mapped[int | None] = mapped_column(
        comment='Diastolic blood pressure (mmHg)'
    )
    blood_pressure_position: Mapped[str | None] = mapped_column(
        String(50),
        comment='Position: sitting, standing, lying'
    )
    blood_pressure_arm: Mapped[str | None] = mapped_column(
        String(10),
        comment='Arm: left, right'
    )

    # Oxygen saturation
    oxygen_saturation: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment='Oxygen saturation percentage (SpO2)'
    )
    oxygen_flow_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment='Supplemental oxygen flow rate in L/min if applicable'
    )

    # Physical measurements
    height: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment='Height in inches'
    )
    weight: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        comment='Weight in pounds'
    )
    bmi: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1),
        comment='Body Mass Index (calculated or measured)'
    )

    # Additional measurements
    head_circumference: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment='Head circumference in inches (pediatric)'
    )
    waist_circumference: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment='Waist circumference in inches'
    )

    # Pain assessment
    pain_score: Mapped[int | None] = mapped_column(
        comment='Pain level on 0-10 scale'
    )
    pain_location: Mapped[str | None] = mapped_column(
        String(255),
        comment='Location of pain'
    )

    # Clinical context
    recorded_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        comment='User who recorded these vitals'
    )
    recorded_during_visit: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('appointments.id', ondelete='SET NULL'),
        comment='Appointment during which vitals were taken'
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment='Additional notes or observations'
    )

    # Relationships
    patient = relationship('Patient', back_populates='vitals')
    appointment = relationship('Appointment', foreign_keys=[recorded_during_visit])

    def __repr__(self) -> str:
        return f"<MedicalVitals(patient_id={self.patient_id}, date={self.measurement_date}, bp={self.blood_pressure_display})>"

    @property
    def blood_pressure_display(self) -> str | None:
        """Get formatted blood pressure (e.g., '120/80')."""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None

    @property
    def temperature_celsius(self) -> Decimal | None:
        """Convert temperature to Celsius."""
        if self.temperature:
            return (self.temperature - 32) * Decimal('5') / Decimal('9')
        return None

    @property
    def height_cm(self) -> Decimal | None:
        """Convert height to centimeters."""
        if self.height:
            return self.height * Decimal('2.54')
        return None

    @property
    def weight_kg(self) -> Decimal | None:
        """Convert weight to kilograms."""
        if self.weight:
            return self.weight * Decimal('0.453592')
        return None

    def calculate_bmi(self) -> Decimal | None:
        """Calculate BMI if height and weight are available."""
        if self.height and self.weight and self.height > 0:
            # BMI = (weight in pounds / (height in inches)^2) * 703
            bmi = (self.weight / (self.height ** 2)) * Decimal('703')
            return round(bmi, 1)
        return None
