"""API endpoints for document management."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.documents import (
    ApproveDocumentRequest,
    Document,
    DocumentCreate,
    DocumentUpdate,
    DocumentVersion,
    DocumentVersionHistory,
    DocumentWithComputedFields,
    ReviewApprovalResponse,
    ReviewDocumentRequest,
)
from app.models.document import DocumentStatus, DocumentType
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.patient_service import PatientService

router = APIRouter()


async def verify_patient_access(
    patient_id: UUID,
    current_user: User,
    db: AsyncSession,
) -> None:
    """Verify current user has access to patient."""
    patient_service = PatientService(db, current_user.practice_id)
    patient = await patient_service.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")


# ============================================================================
# CRUD Endpoints
# ============================================================================


@router.get("/patients/{patient_id}/documents", response_model=PaginatedResponse[Document])
async def list_patient_documents(
    patient_id: UUID,
    document_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    is_confidential: Optional[bool] = None,
    search_text: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all documents for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    documents, total = await service.list_documents(
        patient_id=patient_id,
        document_type=document_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        is_confidential=is_confidential,
        search_text=search_text,
        skip=skip,
        limit=limit,
    )

    return PaginatedResponse(
        items=documents,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post("/patients/{patient_id}/documents", response_model=Document, status_code=status.HTTP_201_CREATED)
async def create_document(
    patient_id: UUID,
    document_in: DocumentCreate,
    file_name: str = Query(..., max_length=255),
    file_path: str = Query(..., max_length=1000),
    file_size: int = Query(..., ge=0),
    mime_type: str = Query(..., max_length=100),
    storage_backend: str = Query("local", max_length=50),
    bucket_name: Optional[str] = Query(None, max_length=255),
    upload_ip: Optional[str] = Query(None, max_length=45),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create document metadata (after file upload)."""
    await verify_patient_access(patient_id, current_user, db)

    if document_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")

    service = DocumentService(db, current_user.practice_id)
    document = await service.create_document_metadata(
        document_in,
        file_name=file_name,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        uploaded_by=current_user.id,
        upload_ip=upload_ip,
        storage_backend=storage_backend,
        bucket_name=bucket_name,
    )
    await db.commit()
    return document


@router.get("/documents/{document_id}", response_model=DocumentWithComputedFields)
async def get_document(
    document_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific document by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    document = await service.get_document_by_id(document_id, patient_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentWithComputedFields(
        **document.__dict__,
        file_size_mb=document.file_size_mb,
        is_approved=document.is_approved,
        is_reviewed=document.is_reviewed,
    )


@router.patch("/documents/{document_id}", response_model=Document)
async def update_document(
    document_id: UUID,
    document_in: DocumentUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update document metadata."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    document = await service.update_document(document_id, patient_id, document_in)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.commit()
    return document


@router.delete("/documents/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a document (soft delete)."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    deleted = await service.delete_document(document_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.commit()
    return SuccessResponse(message="Document deleted successfully")


# ============================================================================
# Review/Approval Endpoints
# ============================================================================


@router.post("/documents/{document_id}/review", response_model=ReviewApprovalResponse)
async def review_document(
    document_id: UUID,
    review_request: ReviewDocumentRequest,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark document as reviewed."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    document = await service.review_document(document_id, patient_id, current_user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.commit()
    return ReviewApprovalResponse(
        document_id=document.id,
        status=document.status,
        reviewed_by=document.reviewed_by,
        reviewed_at=document.reviewed_at,
        message="Document reviewed successfully",
    )


@router.post("/documents/{document_id}/approve", response_model=ReviewApprovalResponse)
async def approve_document(
    document_id: UUID,
    approve_request: ApproveDocumentRequest,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark document as approved."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    try:
        document = await service.approve_document(document_id, patient_id, current_user.id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        await db.commit()
        return ReviewApprovalResponse(
            document_id=document.id,
            status=document.status,
            reviewed_by=document.reviewed_by,
            reviewed_at=document.reviewed_at,
            approved_by=document.approved_by,
            approved_at=document.approved_at,
            message="Document approved successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/documents/{document_id}/archive", response_model=Document)
async def archive_document(
    document_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Archive a document."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    document = await service.archive_document(document_id, patient_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.commit()
    return document


# ============================================================================
# Version Control Endpoints
# ============================================================================


@router.get("/documents/{document_id}/versions", response_model=DocumentVersionHistory)
async def get_document_versions(
    document_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all versions of a document."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    versions = await service.get_document_versions(document_id, patient_id)

    if not versions:
        raise HTTPException(status_code=404, detail="Document not found")

    # Find current version
    current_version = max(v.version for v in versions)

    version_list = [
        DocumentVersion(
            id=v.id,
            version=v.version,
            parent_document_id=v.parent_document_id,
            title=v.title,
            file_name=v.file_name,
            file_size=v.file_size,
            uploaded_by=v.uploaded_by,
            created_at=v.created_at,
        )
        for v in versions
    ]

    return DocumentVersionHistory(
        document_id=document_id,
        current_version=current_version,
        versions=version_list,
    )


# ============================================================================
# Query Endpoints
# ============================================================================


@router.get("/appointments/{appointment_id}/documents", response_model=list[Document])
async def get_appointment_documents(
    appointment_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all documents for a specific appointment."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    documents = await service.get_documents_by_appointment(appointment_id, patient_id)
    return documents


@router.get("/clinical-notes/{clinical_note_id}/documents", response_model=list[Document])
async def get_clinical_note_documents(
    clinical_note_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all documents linked to a clinical note."""
    await verify_patient_access(patient_id, current_user, db)

    service = DocumentService(db, current_user.practice_id)
    documents = await service.get_documents_by_clinical_note(clinical_note_id, patient_id)
    return documents


@router.get("/documents/pending-review", response_model=list[Document])
async def get_pending_review_documents(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get documents pending review."""
    service = DocumentService(db, current_user.practice_id)
    documents = await service.get_pending_review_documents(limit)
    return documents
