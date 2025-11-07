"""Service for managing documents."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.documents import DocumentCreate, DocumentUpdate
from app.models.document import Document, DocumentStatus, DocumentType


class DocumentService:
    """Service for document operations."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ========================================================================
    # CRUD Operations
    # ========================================================================

    async def list_documents(
        self,
        patient_id: Optional[UUID] = None,
        document_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        provider_id: Optional[UUID] = None,
        appointment_id: Optional[UUID] = None,
        is_confidential: Optional[bool] = None,
        tags: Optional[list[str]] = None,
        search_text: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Document], int]:
        """List documents with filtering."""
        query = select(Document).where(
            and_(
                Document.practice_id == self.practice_id,
                Document.is_deleted == False,
            )
        )

        if patient_id:
            query = query.where(Document.patient_id == patient_id)
        if document_type:
            query = query.where(Document.document_type == document_type)
        if status:
            query = query.where(Document.status == status)
        if start_date:
            query = query.where(Document.document_date >= start_date)
        if end_date:
            query = query.where(Document.document_date <= end_date)
        if provider_id:
            query = query.where(Document.provider_id == provider_id)
        if appointment_id:
            query = query.where(Document.appointment_id == appointment_id)
        if is_confidential is not None:
            query = query.where(Document.is_confidential == is_confidential)

        # Tag filtering (JSONB contains)
        if tags:
            for tag in tags:
                query = query.where(Document.tags.contains([tag]))

        # Text search
        if search_text:
            query = query.where(
                or_(
                    Document.title.ilike(f"%{search_text}%"),
                    Document.description.ilike(f"%{search_text}%"),
                    Document.extracted_text.ilike(f"%{search_text}%"),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        documents = list(result.scalars().all())

        return documents, total

    async def get_document_by_id(
        self,
        document_id: UUID,
        patient_id: UUID,
    ) -> Document | None:
        """Get a specific document by ID."""
        query = select(Document).where(
            and_(
                Document.id == document_id,
                Document.patient_id == patient_id,
                Document.practice_id == self.practice_id,
                Document.is_deleted == False,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_document_metadata(
        self,
        document_data: DocumentCreate,
        file_name: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        uploaded_by: UUID,
        upload_ip: Optional[str] = None,
        storage_backend: str = "local",
        bucket_name: Optional[str] = None,
    ) -> Document:
        """Create document metadata (after file upload)."""
        # Extract file extension
        file_extension = None
        if "." in file_name:
            file_extension = file_name.rsplit(".", 1)[1].lower()

        document = Document(
            **document_data.model_dump(),
            practice_id=self.practice_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            file_extension=file_extension,
            storage_backend=storage_backend,
            bucket_name=bucket_name,
            uploaded_by=uploaded_by,
            upload_ip=upload_ip,
        )
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def update_document(
        self,
        document_id: UUID,
        patient_id: UUID,
        document_data: DocumentUpdate,
    ) -> Document | None:
        """Update document metadata."""
        document = await self.get_document_by_id(document_id, patient_id)
        if not document:
            return None

        for field, value in document_data.model_dump(exclude_unset=True).items():
            setattr(document, field, value)

        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def delete_document(
        self,
        document_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Soft delete a document."""
        document = await self.get_document_by_id(document_id, patient_id)
        if not document:
            return False

        document.is_deleted = True
        document.status = DocumentStatus.DELETED
        await self.db.flush()
        return True

    # ========================================================================
    # Review and Approval
    # ========================================================================

    async def review_document(
        self,
        document_id: UUID,
        patient_id: UUID,
        reviewer_id: UUID,
    ) -> Document | None:
        """Mark document as reviewed."""
        document = await self.get_document_by_id(document_id, patient_id)
        if not document:
            return None

        from datetime import datetime

        document.status = DocumentStatus.REVIEWED
        document.reviewed_by = reviewer_id
        document.reviewed_at = datetime.now().isoformat()

        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def approve_document(
        self,
        document_id: UUID,
        patient_id: UUID,
        approver_id: UUID,
    ) -> Document | None:
        """Mark document as approved."""
        document = await self.get_document_by_id(document_id, patient_id)
        if not document:
            return None

        if not document.is_reviewed and document.status != DocumentStatus.REVIEWED:
            raise ValueError("Document must be reviewed before approval")

        from datetime import datetime

        document.status = DocumentStatus.APPROVED
        document.approved_by = approver_id
        document.approved_at = datetime.now().isoformat()

        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def archive_document(
        self,
        document_id: UUID,
        patient_id: UUID,
    ) -> Document | None:
        """Archive a document."""
        document = await self.get_document_by_id(document_id, patient_id)
        if not document:
            return None

        document.status = DocumentStatus.ARCHIVED
        await self.db.flush()
        await self.db.refresh(document)
        return document

    # ========================================================================
    # Version Control
    # ========================================================================

    async def create_document_version(
        self,
        parent_document_id: UUID,
        patient_id: UUID,
        file_name: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        uploaded_by: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        storage_backend: str = "local",
        bucket_name: Optional[str] = None,
    ) -> Document | None:
        """Create a new version of a document."""
        # Get parent document
        parent = await self.get_document_by_id(parent_document_id, patient_id)
        if not parent:
            return None

        # Extract file extension
        file_extension = None
        if "." in file_name:
            file_extension = file_name.rsplit(".", 1)[1].lower()

        # Create new version
        new_version = Document(
            patient_id=parent.patient_id,
            appointment_id=parent.appointment_id,
            clinical_note_id=parent.clinical_note_id,
            provider_id=parent.provider_id,
            practice_id=self.practice_id,
            document_type=parent.document_type,
            status=DocumentStatus.PENDING_REVIEW,
            title=title or parent.title,
            description=description or parent.description,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            file_extension=file_extension,
            storage_backend=storage_backend,
            bucket_name=bucket_name,
            document_date=parent.document_date,
            is_confidential=parent.is_confidential,
            access_restricted=parent.access_restricted,
            version=parent.version + 1,
            parent_document_id=parent_document_id,
            tags=parent.tags,
            metadata=parent.metadata,
            uploaded_by=uploaded_by,
        )

        self.db.add(new_version)
        await self.db.flush()
        await self.db.refresh(new_version)
        return new_version

    async def get_document_versions(
        self,
        document_id: UUID,
        patient_id: UUID,
    ) -> list[Document]:
        """Get all versions of a document."""
        # First get the document to find the parent
        document = await self.get_document_by_id(document_id, patient_id)
        if not document:
            return []

        # If this is a version, get the parent first
        root_id = document.parent_document_id or document_id

        # Get all versions
        query = (
            select(Document)
            .where(
                and_(
                    Document.practice_id == self.practice_id,
                    Document.patient_id == patient_id,
                    or_(
                        Document.id == root_id,
                        Document.parent_document_id == root_id,
                    ),
                    Document.is_deleted == False,
                )
            )
            .order_by(Document.version.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ========================================================================
    # OCR and Text Extraction
    # ========================================================================

    async def update_extracted_text(
        self,
        document_id: UUID,
        patient_id: UUID,
        extracted_text: str,
    ) -> Document | None:
        """Update document with extracted text (OCR result)."""
        document = await self.get_document_by_id(document_id, patient_id)
        if not document:
            return None

        document.extracted_text = extracted_text
        document.ocr_performed = True

        await self.db.flush()
        await self.db.refresh(document)
        return document

    # ========================================================================
    # Queries and Statistics
    # ========================================================================

    async def get_documents_by_appointment(
        self,
        appointment_id: UUID,
        patient_id: UUID,
    ) -> list[Document]:
        """Get all documents for a specific appointment."""
        query = (
            select(Document)
            .where(
                and_(
                    Document.practice_id == self.practice_id,
                    Document.appointment_id == appointment_id,
                    Document.patient_id == patient_id,
                    Document.is_deleted == False,
                )
            )
            .order_by(Document.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_documents_by_clinical_note(
        self,
        clinical_note_id: UUID,
        patient_id: UUID,
    ) -> list[Document]:
        """Get all documents linked to a clinical note."""
        query = (
            select(Document)
            .where(
                and_(
                    Document.practice_id == self.practice_id,
                    Document.clinical_note_id == clinical_note_id,
                    Document.patient_id == patient_id,
                    Document.is_deleted == False,
                )
            )
            .order_by(Document.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_pending_review_documents(
        self,
        limit: int = 50,
    ) -> list[Document]:
        """Get documents pending review."""
        query = (
            select(Document)
            .where(
                and_(
                    Document.practice_id == self.practice_id,
                    Document.status == DocumentStatus.PENDING_REVIEW,
                    Document.is_deleted == False,
                )
            )
            .order_by(Document.created_at.asc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_storage_stats(self) -> dict:
        """Get storage statistics for the practice."""
        # Total documents count
        count_query = select(func.count()).where(
            and_(
                Document.practice_id == self.practice_id,
                Document.is_deleted == False,
            )
        )
        count_result = await self.db.execute(count_query)
        total_documents = count_result.scalar_one()

        # Total size
        size_query = select(func.sum(Document.file_size)).where(
            and_(
                Document.practice_id == self.practice_id,
                Document.is_deleted == False,
            )
        )
        size_result = await self.db.execute(size_query)
        total_size = size_result.scalar_one() or 0

        return {
            "total_documents": total_documents,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024),
        }
