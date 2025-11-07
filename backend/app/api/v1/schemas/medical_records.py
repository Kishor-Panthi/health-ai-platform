"""Pydantic schemas for medical records."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.medical_allergy import AllergySeverity, AllergyStatus
from app.models.medical_condition import ConditionSeverity, ConditionStatus
from app.models.medical_medication import MedicationRoute, MedicationStatus


# ============================================================================
# Medical Allergy Schemas
# ============================================================================


class MedicalAllergyBase(BaseModel):
    """Base schema for medical allergies."""

    allergen: str = Field(..., max_length=255, description="Allergen name or substance")
    reaction: Optional[str] = Field(None, max_length=500, description="Description of reaction")
    severity: AllergySeverity = Field(..., description="Severity level")
    status: AllergyStatus = Field(default=AllergyStatus.ACTIVE, description="Current status")
    onset_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date allergy first noted")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicalAllergyCreate(MedicalAllergyBase):
    """Schema for creating a medical allergy."""

    patient_id: UUID = Field(..., description="Patient ID")


class MedicalAllergyUpdate(BaseModel):
    """Schema for updating a medical allergy."""

    allergen: Optional[str] = Field(None, max_length=255)
    reaction: Optional[str] = Field(None, max_length=500)
    severity: Optional[AllergySeverity] = None
    status: Optional[AllergyStatus] = None
    onset_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    notes: Optional[str] = None


class MedicalAllergy(MedicalAllergyBase):
    """Schema for medical allergy response."""

    id: UUID
    patient_id: UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


# ============================================================================
# Medical Medication Schemas
# ============================================================================


class MedicalMedicationBase(BaseModel):
    """Base schema for medical medications."""

    medication_name: str = Field(..., max_length=255, description="Medication name")
    dosage: Optional[str] = Field(None, max_length=100, description="Dosage (e.g., '10mg')")
    frequency: Optional[str] = Field(None, max_length=100, description="Frequency (e.g., 'twice daily')")
    route: Optional[MedicationRoute] = Field(None, description="Route of administration")
    status: MedicationStatus = Field(default=MedicationStatus.ACTIVE, description="Medication status")
    prescribed_by: Optional[UUID] = Field(None, description="Provider who prescribed")
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Start date")
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="End date")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for medication")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicalMedicationCreate(MedicalMedicationBase):
    """Schema for creating a medical medication."""

    patient_id: UUID = Field(..., description="Patient ID")


class MedicalMedicationUpdate(BaseModel):
    """Schema for updating a medical medication."""

    medication_name: Optional[str] = Field(None, max_length=255)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    route: Optional[MedicationRoute] = None
    status: Optional[MedicationStatus] = None
    prescribed_by: Optional[UUID] = None
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class MedicalMedication(MedicalMedicationBase):
    """Schema for medical medication response."""

    id: UUID
    patient_id: UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


# ============================================================================
# Medical Condition Schemas
# ============================================================================


class MedicalConditionBase(BaseModel):
    """Base schema for medical conditions."""

    condition_name: str = Field(..., max_length=255, description="Condition or diagnosis name")
    icd10_code: Optional[str] = Field(None, max_length=10, description="ICD-10 diagnosis code")
    status: ConditionStatus = Field(default=ConditionStatus.ACTIVE, description="Condition status")
    severity: Optional[ConditionSeverity] = Field(None, description="Severity level")
    is_chronic: bool = Field(default=False, description="Is this a chronic condition")
    onset_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date of onset")
    resolved_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date resolved")
    diagnosed_by: Optional[UUID] = Field(None, description="Provider who diagnosed")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicalConditionCreate(MedicalConditionBase):
    """Schema for creating a medical condition."""

    patient_id: UUID = Field(..., description="Patient ID")


class MedicalConditionUpdate(BaseModel):
    """Schema for updating a medical condition."""

    condition_name: Optional[str] = Field(None, max_length=255)
    icd10_code: Optional[str] = Field(None, max_length=10)
    status: Optional[ConditionStatus] = None
    severity: Optional[ConditionSeverity] = None
    is_chronic: Optional[bool] = None
    onset_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    resolved_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    diagnosed_by: Optional[UUID] = None
    notes: Optional[str] = None


class MedicalCondition(MedicalConditionBase):
    """Schema for medical condition response."""

    id: UUID
    patient_id: UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


# ============================================================================
# Medical Immunization Schemas
# ============================================================================


class MedicalImmunizationBase(BaseModel):
    """Base schema for medical immunizations."""

    vaccine_name: str = Field(..., max_length=255, description="Vaccine name")
    administration_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date administered")
    administered_by: Optional[UUID] = Field(None, description="User who administered")
    lot_number: Optional[str] = Field(None, max_length=100, description="Vaccine lot number")
    expiration_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Vaccine expiration")
    dose_number: Optional[int] = Field(None, ge=1, description="Dose number in series")
    series_complete: bool = Field(default=False, description="Is the series complete")
    manufacturer: Optional[str] = Field(None, max_length=255, description="Vaccine manufacturer")
    site: Optional[str] = Field(None, max_length=100, description="Injection site")
    route: Optional[str] = Field(None, max_length=50, description="Route (IM, SC, etc)")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicalImmunizationCreate(MedicalImmunizationBase):
    """Schema for creating a medical immunization."""

    patient_id: UUID = Field(..., description="Patient ID")


class MedicalImmunizationUpdate(BaseModel):
    """Schema for updating a medical immunization."""

    vaccine_name: Optional[str] = Field(None, max_length=255)
    administration_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    administered_by: Optional[UUID] = None
    lot_number: Optional[str] = Field(None, max_length=100)
    expiration_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    dose_number: Optional[int] = Field(None, ge=1)
    series_complete: Optional[bool] = None
    manufacturer: Optional[str] = Field(None, max_length=255)
    site: Optional[str] = Field(None, max_length=100)
    route: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class MedicalImmunization(MedicalImmunizationBase):
    """Schema for medical immunization response."""

    id: UUID
    patient_id: UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


# ============================================================================
# Medical Vitals Schemas
# ============================================================================


class MedicalVitalsBase(BaseModel):
    """Base schema for medical vitals."""

    measurement_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date measured")
    measurement_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}:\d{2}$', description="Time measured")

    # Core vitals
    temperature: Optional[Decimal] = Field(None, ge=90.0, le=110.0, description="Temperature in Fahrenheit")
    temperature_method: Optional[str] = Field(None, max_length=50, description="oral, axillary, tympanic, etc")
    pulse: Optional[int] = Field(None, ge=20, le=250, description="Heart rate (bpm)")
    pulse_rhythm: Optional[str] = Field(None, max_length=50, description="regular, irregular")
    respiration_rate: Optional[int] = Field(None, ge=5, le=60, description="Breaths per minute")

    # Blood pressure
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=300, description="Systolic BP (mmHg)")
    blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=200, description="Diastolic BP (mmHg)")
    blood_pressure_position: Optional[str] = Field(None, max_length=50, description="sitting, standing, lying")
    blood_pressure_arm: Optional[str] = Field(None, max_length=10, description="left, right")

    # Oxygen
    oxygen_saturation: Optional[Decimal] = Field(None, ge=0, le=100, description="SpO2 percentage")
    oxygen_flow_rate: Optional[Decimal] = Field(None, ge=0, le=20, description="Supplemental O2 (L/min)")

    # Physical measurements
    height: Optional[Decimal] = Field(None, ge=0, le=120, description="Height in inches")
    weight: Optional[Decimal] = Field(None, ge=0, le=2000, description="Weight in pounds")
    bmi: Optional[Decimal] = Field(None, ge=0, le=200, description="BMI")
    head_circumference: Optional[Decimal] = Field(None, ge=0, le=50, description="Head circumference (inches)")
    waist_circumference: Optional[Decimal] = Field(None, ge=0, le=100, description="Waist circumference (inches)")

    # Pain
    pain_score: Optional[int] = Field(None, ge=0, le=10, description="Pain level 0-10")
    pain_location: Optional[str] = Field(None, max_length=255, description="Location of pain")

    # Context
    recorded_by: Optional[UUID] = Field(None, description="User who recorded")
    recorded_during_visit: Optional[UUID] = Field(None, description="Appointment ID")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicalVitalsCreate(MedicalVitalsBase):
    """Schema for creating medical vitals."""

    patient_id: UUID = Field(..., description="Patient ID")


class MedicalVitalsUpdate(BaseModel):
    """Schema for updating medical vitals."""

    measurement_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    measurement_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}:\d{2}$')
    temperature: Optional[Decimal] = Field(None, ge=90.0, le=110.0)
    temperature_method: Optional[str] = Field(None, max_length=50)
    pulse: Optional[int] = Field(None, ge=20, le=250)
    pulse_rhythm: Optional[str] = Field(None, max_length=50)
    respiration_rate: Optional[int] = Field(None, ge=5, le=60)
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=300)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=200)
    blood_pressure_position: Optional[str] = Field(None, max_length=50)
    blood_pressure_arm: Optional[str] = Field(None, max_length=10)
    oxygen_saturation: Optional[Decimal] = Field(None, ge=0, le=100)
    oxygen_flow_rate: Optional[Decimal] = Field(None, ge=0, le=20)
    height: Optional[Decimal] = Field(None, ge=0, le=120)
    weight: Optional[Decimal] = Field(None, ge=0, le=2000)
    bmi: Optional[Decimal] = Field(None, ge=0, le=200)
    head_circumference: Optional[Decimal] = Field(None, ge=0, le=50)
    waist_circumference: Optional[Decimal] = Field(None, ge=0, le=100)
    pain_score: Optional[int] = Field(None, ge=0, le=10)
    pain_location: Optional[str] = Field(None, max_length=255)
    recorded_by: Optional[UUID] = None
    recorded_during_visit: Optional[UUID] = None
    notes: Optional[str] = None


class MedicalVitals(MedicalVitalsBase):
    """Schema for medical vitals response."""

    id: UUID
    patient_id: UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}
