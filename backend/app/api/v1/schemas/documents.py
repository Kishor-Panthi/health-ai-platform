"""Pydantic schemas for documents."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.document import DocumentStatus, DocumentType


# ============================================================================
# Document Schemas
# ============================================================================


class DocumentBase(BaseModel):
    """Base schema for documents."""

    document_type: DocumentType = Field(..., description="Type of document")
    title: str = Field(..., max_length=255, description="Document title")
    description: Optional[str] = Field(None, description="Document description")
    document_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date of document")
    is_confidential: bool = Field(default=False, description="Confidential/sensitive document")
    access_restricted: bool = Field(default=False, description="Restrict access")
    tags: Optional[list[str]] = Field(None, description="Tags for organization")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class DocumentCreate(DocumentBase):
    """Schema for creating a document (metadata only, file uploaded separately)."""

    patient_id: UUID = Field(..., description="Patient ID")
    appointment_id: Optional[UUID] = Field(None, description="Appointment ID")
    clinical_note_id: Optional[UUID] = Field(None, description="Clinical note ID")
    provider_id: Optional[UUID] = Field(None, description="Provider ID")
    status: DocumentStatus = Field(default=DocumentStatus.PENDING_REVIEW, description="Document status")


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    document_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    is_confidential: Optional[bool] = None
    access_restricted: Optional[bool] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class Document(DocumentBase):
    """Schema for document response."""

    id: UUID
    patient_id: UUID
    appointment_id: Optional[UUID] = None
    clinical_note_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    practice_id: UUID
    status: DocumentStatus
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    file_extension: Optional[str] = None
    storage_backend: str
    bucket_name: Optional[str] = None
    encryption_enabled: bool
    extracted_text: Optional[str] = None
    ocr_performed: bool
    version: int
    parent_document_id: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[str] = None
    uploaded_by: UUID
    upload_ip: Optional[str] = None
    expires_at: Optional[str] = None
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    is_deleted: bool
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


class DocumentWithComputedFields(Document):
    """Document with computed fields."""

    file_size_mb: float
    is_approved: bool
    is_reviewed: bool


# ============================================================================
# Document Upload Schemas
# ============================================================================


class DocumentUploadMetadata(BaseModel):
    """Metadata for document upload."""

    patient_id: UUID = Field(..., description="Patient ID")
    document_type: DocumentType = Field(..., description="Type of document")
    title: str = Field(..., max_length=255, description="Document title")
    description: Optional[str] = Field(None, description="Document description")
    document_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date of document")
    appointment_id: Optional[UUID] = Field(None, description="Appointment ID")
    clinical_note_id: Optional[UUID] = Field(None, description="Clinical note ID")
    provider_id: Optional[UUID] = Field(None, description="Provider ID")
    is_confidential: bool = Field(default=False, description="Confidential document")
    tags: Optional[list[str]] = Field(None, description="Tags")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""

    document_id: UUID
    file_name: str
    file_size: int
    upload_url: Optional[str] = Field(None, description="Pre-signed URL for upload (S3)")
    message: str


class DocumentDownloadResponse(BaseModel):
    """Response for document download."""

    document_id: UUID
    file_name: str
    download_url: str
    expires_in_seconds: int


# ============================================================================
# Document Review/Approval Schemas
# ============================================================================


class ReviewDocumentRequest(BaseModel):
    """Schema for reviewing a document."""

    notes: Optional[str] = Field(None, description="Review notes")


class ApproveDocumentRequest(BaseModel):
    """Schema for approving a document."""

    notes: Optional[str] = Field(None, description="Approval notes")


class ReviewApprovalResponse(BaseModel):
    """Response after review/approval."""

    document_id: UUID
    status: DocumentStatus
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[str] = None
    message: str


# ============================================================================
# Document Version Schemas
# ============================================================================


class CreateDocumentVersionRequest(BaseModel):
    """Schema for creating a new version of a document."""

    title: Optional[str] = Field(None, max_length=255, description="New version title")
    description: Optional[str] = Field(None, description="Version description")
    metadata: Optional[dict[str, Any]] = Field(None, description="Version metadata")


class DocumentVersion(BaseModel):
    """Schema for document version info."""

    id: UUID
    version: int
    parent_document_id: Optional[UUID] = None
    title: str
    file_name: str
    file_size: int
    uploaded_by: UUID
    created_at: str


class DocumentVersionHistory(BaseModel):
    """Document version history."""

    document_id: UUID
    current_version: int
    versions: list[DocumentVersion]


# ============================================================================
# Document Search Schemas
# ============================================================================


class DocumentSearchFilters(BaseModel):
    """Filters for document search."""

    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    provider_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    is_confidential: Optional[bool] = None
    tags: Optional[list[str]] = None
    search_text: Optional[str] = Field(None, description="Search in title, description, extracted text")


# ============================================================================
# Summary Schemas
# ============================================================================


class DocumentSummary(BaseModel):
    """Summary of documents for a patient."""

    patient_id: UUID
    total_documents: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    total_size_mb: float
    pending_review: int
    confidential_count: int
    recent_documents: list[Document]


class StorageStats(BaseModel):
    """Storage statistics."""

    total_documents: int
    total_size_bytes: int
    total_size_mb: float
    total_size_gb: float
    by_storage_backend: dict[str, int]
    by_mime_type: dict[str, int]
