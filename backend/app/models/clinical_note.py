"""Clinical note model for medical documentation."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class NoteType(str, enum.Enum):
    """Clinical note type enumeration."""

    SOAP = "soap"  # Subjective, Objective, Assessment, Plan
    PROGRESS = "progress"
    CONSULTATION = "consultation"
    PROCEDURE = "procedure"
    OPERATIVE = "operative"
    DISCHARGE = "discharge"
    H_AND_P = "h_and_p"  # History and Physical
    FOLLOW_UP = "follow_up"
    PHONE_CALL = "phone_call"
    REFERRAL = "referral"
    GENERAL = "general"


class NoteStatus(str, enum.Enum):
    """Note status enumeration."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SIGNED = "signed"
    AMENDED = "amended"
    ADDENDED = "addended"
    LOCKED = "locked"


class ClinicalNote(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Clinical documentation and progress notes."""

    __tablename__ = "clinical_notes"

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Appointment reference (optional - note may not be tied to appointment)
    appointment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        index=True,
    )

    # Provider/Author
    provider_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Note metadata
    note_type: Mapped[NoteType] = mapped_column(
        Enum(NoteType), default=NoteType.PROGRESS, nullable=False, index=True
    )
    status: Mapped[NoteStatus] = mapped_column(
        Enum(NoteStatus), default=NoteStatus.DRAFT, nullable=False, index=True
    )

    # Note date
    note_date: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True, comment="Date of service/note (YYYY-MM-DD)"
    )

    # Title/Chief Complaint
    title: Mapped[str | None] = mapped_column(
        String(255), comment="Note title or chief complaint"
    )

    # SOAP Components
    subjective: Mapped[str | None] = mapped_column(
        Text, comment="Subjective: Patient's description of symptoms"
    )
    objective: Mapped[str | None] = mapped_column(
        Text, comment="Objective: Physician's observations and exam findings"
    )
    assessment: Mapped[str | None] = mapped_column(
        Text, comment="Assessment: Diagnosis and clinical impression"
    )
    plan: Mapped[str | None] = mapped_column(
        Text, comment="Plan: Treatment plan and next steps"
    )

    # Additional sections (for non-SOAP notes)
    history_of_present_illness: Mapped[str | None] = mapped_column(
        Text, comment="HPI: History of present illness"
    )
    review_of_systems: Mapped[str | None] = mapped_column(
        Text, comment="ROS: Review of systems"
    )
    physical_examination: Mapped[str | None] = mapped_column(
        Text, comment="Physical exam findings"
    )
    labs_and_imaging: Mapped[str | None] = mapped_column(
        Text, comment="Labs, imaging, and diagnostic results"
    )

    # Full note content (for free-text notes)
    content: Mapped[str | None] = mapped_column(
        Text, comment="Full note content for general notes"
    )

    # Structured data
    diagnosis_codes: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of ICD-10 diagnosis codes"
    )
    procedure_codes: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of CPT/procedure codes"
    )
    medications_prescribed: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of medications prescribed during visit"
    )
    orders: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of orders (labs, imaging, referrals)"
    )

    # Signature and attestation
    signed_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when note was signed (ISO 8601)"
    )
    signed_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="SET NULL"),
        comment="Provider who signed the note",
    )
    signature_ip: Mapped[str | None] = mapped_column(
        String(45), comment="IP address at time of signature"
    )
    attestation_statement: Mapped[str | None] = mapped_column(
        Text, comment="Attestation statement"
    )

    # Amendment tracking
    is_amendment: Mapped[bool] = mapped_column(
        default=False, comment="Is this an amendment to another note"
    )
    amended_note_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinical_notes.id", ondelete="SET NULL"),
        comment="Original note being amended",
    )
    amendment_reason: Mapped[str | None] = mapped_column(
        Text, comment="Reason for amendment"
    )

    # Addendum tracking
    is_addendum: Mapped[bool] = mapped_column(
        default=False, comment="Is this an addendum to another note"
    )
    addendum_to_note_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinical_notes.id", ondelete="SET NULL"),
        comment="Note this is an addendum to",
    )

    # Templates
    template_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), comment="Template used (if any)"
    )
    template_name: Mapped[str | None] = mapped_column(
        String(255), comment="Name of template used"
    )

    # Additional metadata
    tags: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of tags for organization"
    )
    metadata: Mapped[dict | None] = mapped_column(
        JSONB, comment="Additional structured metadata"
    )

    # Relationships
    patient = relationship("Patient", back_populates="clinical_notes")
    appointment = relationship("Appointment", back_populates="clinical_notes")
    provider = relationship("Provider", foreign_keys=[provider_id], back_populates="clinical_notes")
    signed_by_provider = relationship("Provider", foreign_keys=[signed_by])
    amended_note = relationship(
        "ClinicalNote",
        foreign_keys=[amended_note_id],
        remote_side="ClinicalNote.id",
        uselist=False,
    )
    addendum_to_note = relationship(
        "ClinicalNote",
        foreign_keys=[addendum_to_note_id],
        remote_side="ClinicalNote.id",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<ClinicalNote(type={self.note_type}, status={self.status}, patient_id={self.patient_id})>"

    @property
    def is_signed(self) -> bool:
        """Check if note is signed."""
        return self.status == NoteStatus.SIGNED and self.signed_at is not None

    @property
    def is_locked(self) -> bool:
        """Check if note is locked (signed or locked status)."""
        return self.status in (NoteStatus.SIGNED, NoteStatus.LOCKED)
