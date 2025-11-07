"""Document model for file and document management."""

from __future__ import annotations

import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentType(str, enum.Enum):
    """Document type enumeration."""

    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    PATHOLOGY = "pathology"
    CONSULTATION = "consultation"
    REFERRAL = "referral"
    INSURANCE = "insurance"
    CONSENT_FORM = "consent_form"
    REGISTRATION_FORM = "registration_form"
    CORRESPONDENCE = "correspondence"
    PRESCRIPTION = "prescription"
    MEDICAL_RECORD = "medical_record"
    DISCHARGE_SUMMARY = "discharge_summary"
    OPERATIVE_REPORT = "operative_report"
    PROGRESS_NOTE = "progress_note"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document status enumeration."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Document(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Document and file management for patient records."""

    __tablename__ = "documents"

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Appointment reference (optional)
    appointment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        index=True,
    )

    # Clinical note reference (optional)
    clinical_note_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinical_notes.id", ondelete="SET NULL"),
        index=True,
    )

    # Provider reference (optional - who uploaded/created)
    provider_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="SET NULL"),
        index=True,
    )

    # Document metadata
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), nullable=False, index=True
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.PENDING_REVIEW, nullable=False, index=True
    )

    # Document identification
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Document title"
    )
    description: Mapped[str | None] = mapped_column(
        Text, comment="Document description"
    )

    # File information
    file_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Original file name"
    )
    file_path: Mapped[str] = mapped_column(
        String(1000), nullable=False, comment="Storage path or S3 key"
    )
    file_size: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="File size in bytes"
    )
    mime_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="MIME type (e.g., application/pdf)"
    )
    file_extension: Mapped[str | None] = mapped_column(
        String(10), comment="File extension"
    )

    # Storage information
    storage_backend: Mapped[str] = mapped_column(
        String(50), default="local", comment="Storage backend: local, s3, azure, etc."
    )
    bucket_name: Mapped[str | None] = mapped_column(
        String(255), comment="S3 bucket or container name"
    )

    # Document date
    document_date: Mapped[str | None] = mapped_column(
        String(10), index=True, comment="Date of document (YYYY-MM-DD)"
    )

    # Security and access
    is_confidential: Mapped[bool] = mapped_column(
        default=False, comment="Confidential/sensitive document"
    )
    encryption_enabled: Mapped[bool] = mapped_column(
        default=False, comment="Is file encrypted"
    )
    access_restricted: Mapped[bool] = mapped_column(
        default=False, comment="Restrict access to specific users"
    )

    # Content extraction (for searchability)
    extracted_text: Mapped[str | None] = mapped_column(
        Text, comment="Extracted text content for search"
    )
    ocr_performed: Mapped[bool] = mapped_column(
        default=False, comment="Has OCR been performed"
    )

    # Version control
    version: Mapped[int] = mapped_column(
        default=1, comment="Document version number"
    )
    parent_document_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        comment="Parent document if this is a version",
    )

    # Review and approval
    reviewed_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who reviewed document",
    )
    reviewed_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when reviewed (ISO 8601)"
    )
    approved_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who approved document",
    )
    approved_at: Mapped[str | None] = mapped_column(
        String(29), comment="Timestamp when approved (ISO 8601)"
    )

    # Upload information
    uploaded_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="User who uploaded document",
    )
    upload_ip: Mapped[str | None] = mapped_column(
        String(45), comment="IP address at time of upload"
    )

    # Metadata and tags
    tags: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of tags for organization"
    )
    metadata: Mapped[dict | None] = mapped_column(
        JSONB, comment="Additional structured metadata"
    )

    # Expiration (for temporary documents)
    expires_at: Mapped[str | None] = mapped_column(
        String(29), comment="Expiration timestamp (ISO 8601)"
    )

    # External references
    external_id: Mapped[str | None] = mapped_column(
        String(255), comment="External system ID"
    )
    external_source: Mapped[str | None] = mapped_column(
        String(100), comment="External source system"
    )

    # Relationships
    patient = relationship("Patient", back_populates="documents")
    appointment = relationship("Appointment", back_populates="documents")
    clinical_note = relationship("ClinicalNote")
    provider = relationship("Provider")
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by])
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    parent_document = relationship(
        "Document",
        remote_side="Document.id",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Document(title={self.title}, type={self.document_type}, patient_id={self.patient_id})>"

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)

    @property
    def is_approved(self) -> bool:
        """Check if document is approved."""
        return self.status == DocumentStatus.APPROVED

    @property
    def is_reviewed(self) -> bool:
        """Check if document has been reviewed."""
        return self.status in (DocumentStatus.REVIEWED, DocumentStatus.APPROVED)
