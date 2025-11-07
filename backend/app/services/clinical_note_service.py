"""Service for managing clinical notes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.clinical_notes import (
    ClinicalNoteCreate,
    ClinicalNoteUpdate,
    CreateAddendumRequest,
    CreateAmendmentRequest,
)
from app.models.clinical_note import ClinicalNote, NoteStatus, NoteType


class ClinicalNoteService:
    """Service for clinical note operations."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ========================================================================
    # CRUD Operations
    # ========================================================================

    async def list_notes(
        self,
        patient_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        note_type: Optional[NoteType] = None,
        status: Optional[NoteStatus] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ClinicalNote], int]:
        """List clinical notes with filtering."""
        query = select(ClinicalNote).where(
            and_(
                ClinicalNote.practice_id == self.practice_id,
                ClinicalNote.is_deleted == False,
            )
        )

        if patient_id:
            query = query.where(ClinicalNote.patient_id == patient_id)
        if provider_id:
            query = query.where(ClinicalNote.provider_id == provider_id)
        if note_type:
            query = query.where(ClinicalNote.note_type == note_type)
        if status:
            query = query.where(ClinicalNote.status == status)
        if start_date:
            query = query.where(ClinicalNote.note_date >= start_date)
        if end_date:
            query = query.where(ClinicalNote.note_date <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(ClinicalNote.note_date.desc(), ClinicalNote.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        notes = list(result.scalars().all())

        return notes, total

    async def get_note_by_id(
        self,
        note_id: UUID,
        patient_id: UUID,
    ) -> ClinicalNote | None:
        """Get a specific note by ID."""
        query = select(ClinicalNote).where(
            and_(
                ClinicalNote.id == note_id,
                ClinicalNote.patient_id == patient_id,
                ClinicalNote.practice_id == self.practice_id,
                ClinicalNote.is_deleted == False,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_note(
        self,
        note_data: ClinicalNoteCreate,
    ) -> ClinicalNote:
        """Create a new clinical note."""
        note = ClinicalNote(
            **note_data.model_dump(),
            practice_id=self.practice_id,
        )
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def update_note(
        self,
        note_id: UUID,
        patient_id: UUID,
        note_data: ClinicalNoteUpdate,
        user_id: UUID,
    ) -> ClinicalNote | None:
        """Update a clinical note."""
        note = await self.get_note_by_id(note_id, patient_id)
        if not note:
            return None

        # Check if note is locked
        if note.is_locked:
            raise ValueError("Cannot edit a locked or signed note. Create an amendment instead.")

        for field, value in note_data.model_dump(exclude_unset=True).items():
            setattr(note, field, value)

        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def delete_note(
        self,
        note_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Soft delete a clinical note (only drafts)."""
        note = await self.get_note_by_id(note_id, patient_id)
        if not note:
            return False

        if note.status != NoteStatus.DRAFT:
            raise ValueError("Only draft notes can be deleted")

        note.is_deleted = True
        await self.db.flush()
        return True

    # ========================================================================
    # Note Signing
    # ========================================================================

    async def sign_note(
        self,
        note_id: UUID,
        patient_id: UUID,
        provider_id: UUID,
        signature_ip: str,
        attestation_statement: Optional[str] = None,
    ) -> ClinicalNote | None:
        """Sign a clinical note."""
        note = await self.get_note_by_id(note_id, patient_id)
        if not note:
            return None

        # Verify the provider is authorized to sign
        if note.provider_id != provider_id:
            raise ValueError("Only the note author can sign this note")

        if note.is_signed:
            raise ValueError("Note is already signed")

        # Set default attestation if not provided
        if not attestation_statement:
            attestation_statement = (
                "I attest that this clinical note accurately reflects the encounter "
                "and that the services documented were medically necessary and provided as described."
            )

        # Sign the note
        note.status = NoteStatus.SIGNED
        note.signed_at = datetime.now().isoformat()
        note.signed_by = provider_id
        note.signature_ip = signature_ip
        note.attestation_statement = attestation_statement

        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def lock_note(
        self,
        note_id: UUID,
        patient_id: UUID,
    ) -> ClinicalNote | None:
        """Lock a note (administrative)."""
        note = await self.get_note_by_id(note_id, patient_id)
        if not note:
            return None

        if not note.is_signed:
            raise ValueError("Note must be signed before it can be locked")

        note.status = NoteStatus.LOCKED
        await self.db.flush()
        await self.db.refresh(note)
        return note

    # ========================================================================
    # Amendments and Addenda
    # ========================================================================

    async def create_amendment(
        self,
        amendment_request: CreateAmendmentRequest,
        patient_id: UUID,
        provider_id: UUID,
    ) -> ClinicalNote | None:
        """Create an amendment to an existing note."""
        # Get original note
        original_note = await self.get_note_by_id(amendment_request.original_note_id, patient_id)
        if not original_note:
            return None

        # Verify note is signed
        if not original_note.is_signed:
            raise ValueError("Can only amend signed notes. Edit the draft instead.")

        # Verify provider authorization
        if original_note.provider_id != provider_id:
            raise ValueError("Only the original author can create an amendment")

        # Create amendment as a new note
        amendment = ClinicalNote(
            patient_id=patient_id,
            practice_id=self.practice_id,
            provider_id=provider_id,
            appointment_id=original_note.appointment_id,
            note_type=original_note.note_type,
            status=NoteStatus.DRAFT,
            note_date=original_note.note_date,
            title=f"AMENDMENT: {original_note.title or 'Clinical Note'}",
            is_amendment=True,
            amended_note_id=amendment_request.original_note_id,
            amendment_reason=amendment_request.amendment_reason,
            # Copy updated content
            subjective=amendment_request.subjective or original_note.subjective,
            objective=amendment_request.objective or original_note.objective,
            assessment=amendment_request.assessment or original_note.assessment,
            plan=amendment_request.plan or original_note.plan,
            content=amendment_request.content or original_note.content,
            diagnosis_codes=amendment_request.diagnosis_codes or original_note.diagnosis_codes,
            procedure_codes=amendment_request.procedure_codes or original_note.procedure_codes,
        )

        self.db.add(amendment)
        await self.db.flush()

        # Update original note status
        original_note.status = NoteStatus.AMENDED

        await self.db.flush()
        await self.db.refresh(amendment)
        return amendment

    async def create_addendum(
        self,
        addendum_request: CreateAddendumRequest,
        patient_id: UUID,
        provider_id: UUID,
    ) -> ClinicalNote | None:
        """Create an addendum to an existing note."""
        # Get original note
        original_note = await self.get_note_by_id(addendum_request.original_note_id, patient_id)
        if not original_note:
            return None

        # Verify note is signed
        if not original_note.is_signed:
            raise ValueError("Can only add addendum to signed notes")

        # Create addendum as a new note
        addendum = ClinicalNote(
            patient_id=patient_id,
            practice_id=self.practice_id,
            provider_id=provider_id,
            appointment_id=original_note.appointment_id,
            note_type=original_note.note_type,
            status=NoteStatus.DRAFT,
            note_date=addendum_request.note_date,
            title=f"ADDENDUM: {original_note.title or 'Clinical Note'}",
            is_addendum=True,
            addendum_to_note_id=addendum_request.original_note_id,
            content=addendum_request.addendum_content,
        )

        self.db.add(addendum)
        await self.db.flush()

        # Update original note status
        original_note.status = NoteStatus.ADDENDED

        await self.db.flush()
        await self.db.refresh(addendum)
        return addendum

    # ========================================================================
    # Queries and Filters
    # ========================================================================

    async def get_unsigned_notes(
        self,
        provider_id: UUID,
        days_back: int = 30,
    ) -> list[ClinicalNote]:
        """Get unsigned notes for a provider."""
        from datetime import date, timedelta

        cutoff_date = (date.today() - timedelta(days=days_back)).isoformat()

        query = (
            select(ClinicalNote)
            .where(
                and_(
                    ClinicalNote.practice_id == self.practice_id,
                    ClinicalNote.provider_id == provider_id,
                    ClinicalNote.status.in_([NoteStatus.DRAFT, NoteStatus.IN_PROGRESS, NoteStatus.COMPLETED]),
                    ClinicalNote.note_date >= cutoff_date,
                    ClinicalNote.is_deleted == False,
                )
            )
            .order_by(ClinicalNote.note_date.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search_notes(
        self,
        patient_id: UUID,
        search_text: str,
        limit: int = 50,
    ) -> list[ClinicalNote]:
        """Search notes by text content."""
        query = (
            select(ClinicalNote)
            .where(
                and_(
                    ClinicalNote.practice_id == self.practice_id,
                    ClinicalNote.patient_id == patient_id,
                    ClinicalNote.is_deleted == False,
                    or_(
                        ClinicalNote.title.ilike(f"%{search_text}%"),
                        ClinicalNote.subjective.ilike(f"%{search_text}%"),
                        ClinicalNote.objective.ilike(f"%{search_text}%"),
                        ClinicalNote.assessment.ilike(f"%{search_text}%"),
                        ClinicalNote.plan.ilike(f"%{search_text}%"),
                        ClinicalNote.content.ilike(f"%{search_text}%"),
                    ),
                )
            )
            .order_by(ClinicalNote.note_date.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_notes_by_appointment(
        self,
        appointment_id: UUID,
        patient_id: UUID,
    ) -> list[ClinicalNote]:
        """Get all notes for a specific appointment."""
        query = (
            select(ClinicalNote)
            .where(
                and_(
                    ClinicalNote.practice_id == self.practice_id,
                    ClinicalNote.appointment_id == appointment_id,
                    ClinicalNote.patient_id == patient_id,
                    ClinicalNote.is_deleted == False,
                )
            )
            .order_by(ClinicalNote.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_amendments_for_note(
        self,
        note_id: UUID,
        patient_id: UUID,
    ) -> list[ClinicalNote]:
        """Get all amendments for a note."""
        query = (
            select(ClinicalNote)
            .where(
                and_(
                    ClinicalNote.practice_id == self.practice_id,
                    ClinicalNote.patient_id == patient_id,
                    ClinicalNote.amended_note_id == note_id,
                    ClinicalNote.is_amendment == True,
                    ClinicalNote.is_deleted == False,
                )
            )
            .order_by(ClinicalNote.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_addenda_for_note(
        self,
        note_id: UUID,
        patient_id: UUID,
    ) -> list[ClinicalNote]:
        """Get all addenda for a note."""
        query = (
            select(ClinicalNote)
            .where(
                and_(
                    ClinicalNote.practice_id == self.practice_id,
                    ClinicalNote.patient_id == patient_id,
                    ClinicalNote.addendum_to_note_id == note_id,
                    ClinicalNote.is_addendum == True,
                    ClinicalNote.is_deleted == False,
                )
            )
            .order_by(ClinicalNote.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
