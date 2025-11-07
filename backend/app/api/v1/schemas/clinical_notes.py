"""Pydantic schemas for clinical notes."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.clinical_note import NoteStatus, NoteType


# ============================================================================
# Clinical Note Schemas
# ============================================================================


class ClinicalNoteBase(BaseModel):
    """Base schema for clinical notes."""

    note_type: NoteType = Field(default=NoteType.PROGRESS, description="Type of clinical note")
    note_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date of service/note")
    title: Optional[str] = Field(None, max_length=255, description="Note title or chief complaint")

    # SOAP sections
    subjective: Optional[str] = Field(None, description="Subjective: Patient's description")
    objective: Optional[str] = Field(None, description="Objective: Physician's observations")
    assessment: Optional[str] = Field(None, description="Assessment: Diagnosis and impression")
    plan: Optional[str] = Field(None, description="Plan: Treatment plan")

    # Additional sections
    history_of_present_illness: Optional[str] = Field(None, description="HPI")
    review_of_systems: Optional[str] = Field(None, description="ROS")
    physical_examination: Optional[str] = Field(None, description="Physical exam findings")
    labs_and_imaging: Optional[str] = Field(None, description="Labs and imaging results")

    # Full content for non-SOAP notes
    content: Optional[str] = Field(None, description="Full note content")

    # Structured data
    diagnosis_codes: Optional[list[str]] = Field(None, description="ICD-10 diagnosis codes")
    procedure_codes: Optional[list[str]] = Field(None, description="CPT/procedure codes")
    medications_prescribed: Optional[list[dict[str, Any]]] = Field(None, description="Medications prescribed")
    orders: Optional[list[dict[str, Any]]] = Field(None, description="Orders (labs, imaging, referrals)")

    # Template
    template_id: Optional[UUID] = Field(None, description="Template used")
    template_name: Optional[str] = Field(None, max_length=255, description="Template name")

    # Metadata
    tags: Optional[list[str]] = Field(None, description="Tags for organization")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class ClinicalNoteCreate(ClinicalNoteBase):
    """Schema for creating a clinical note."""

    patient_id: UUID = Field(..., description="Patient ID")
    provider_id: UUID = Field(..., description="Provider ID (author)")
    appointment_id: Optional[UUID] = Field(None, description="Appointment ID")
    status: NoteStatus = Field(default=NoteStatus.DRAFT, description="Initial note status")


class ClinicalNoteUpdate(BaseModel):
    """Schema for updating a clinical note."""

    note_type: Optional[NoteType] = None
    status: Optional[NoteStatus] = None
    note_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    title: Optional[str] = Field(None, max_length=255)
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    review_of_systems: Optional[str] = None
    physical_examination: Optional[str] = None
    labs_and_imaging: Optional[str] = None
    content: Optional[str] = None
    diagnosis_codes: Optional[list[str]] = None
    procedure_codes: Optional[list[str]] = None
    medications_prescribed: Optional[list[dict[str, Any]]] = None
    orders: Optional[list[dict[str, Any]]] = None
    template_id: Optional[UUID] = None
    template_name: Optional[str] = Field(None, max_length=255)
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class ClinicalNote(ClinicalNoteBase):
    """Schema for clinical note response."""

    id: UUID
    patient_id: UUID
    provider_id: UUID
    appointment_id: Optional[UUID] = None
    practice_id: UUID
    status: NoteStatus
    signed_at: Optional[str] = None
    signed_by: Optional[UUID] = None
    signature_ip: Optional[str] = None
    attestation_statement: Optional[str] = None
    is_amendment: bool
    amended_note_id: Optional[UUID] = None
    amendment_reason: Optional[str] = None
    is_addendum: bool
    addendum_to_note_id: Optional[UUID] = None
    is_deleted: bool
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


class ClinicalNoteWithStatus(ClinicalNote):
    """Clinical note with computed status flags."""

    is_signed: bool
    is_locked: bool


# ============================================================================
# Note Signing Schemas
# ============================================================================


class SignNoteRequest(BaseModel):
    """Schema for signing a clinical note."""

    signature_ip: str = Field(..., max_length=45, description="IP address of signer")
    attestation_statement: Optional[str] = Field(
        None,
        description="Attestation statement (optional, defaults to standard statement)"
    )


class SignNoteResponse(BaseModel):
    """Response after signing a note."""

    note_id: UUID
    signed_at: str
    signed_by: UUID
    message: str


# ============================================================================
# Amendment/Addendum Schemas
# ============================================================================


class CreateAmendmentRequest(BaseModel):
    """Schema for creating an amendment to a note."""

    original_note_id: UUID = Field(..., description="Original note being amended")
    amendment_reason: str = Field(..., min_length=1, description="Reason for amendment")

    # Updated content
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    content: Optional[str] = None

    # Additional changes
    diagnosis_codes: Optional[list[str]] = None
    procedure_codes: Optional[list[str]] = None


class CreateAddendumRequest(BaseModel):
    """Schema for creating an addendum to a note."""

    original_note_id: UUID = Field(..., description="Note to add addendum to")
    addendum_content: str = Field(..., min_length=1, description="Addendum content")
    note_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date of addendum")


# ============================================================================
# Note Templates
# ============================================================================


class NoteTemplate(BaseModel):
    """Schema for note templates (future use)."""

    id: UUID
    name: str
    note_type: NoteType
    template_content: dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str


# ============================================================================
# Summary Schemas
# ============================================================================


class NoteSummary(BaseModel):
    """Summary of notes for a patient."""

    patient_id: UUID
    total_notes: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    unsigned_notes: int
    recent_notes: list[ClinicalNote]
