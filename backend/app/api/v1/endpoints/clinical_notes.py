"""API endpoints for clinical notes."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.clinical_notes import (
    ClinicalNote,
    ClinicalNoteCreate,
    ClinicalNoteUpdate,
    ClinicalNoteWithStatus,
    CreateAddendumRequest,
    CreateAmendmentRequest,
    SignNoteRequest,
    SignNoteResponse,
)
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.models.clinical_note import NoteStatus, NoteType
from app.models.user import User
from app.services.clinical_note_service import ClinicalNoteService
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


@router.get("/patients/{patient_id}/notes", response_model=PaginatedResponse[ClinicalNote])
async def list_patient_notes(
    patient_id: UUID,
    note_type: Optional[NoteType] = None,
    status: Optional[NoteStatus] = None,
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all clinical notes for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    notes, total = await service.list_notes(
        patient_id=patient_id,
        note_type=note_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    return PaginatedResponse(
        items=notes,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post("/patients/{patient_id}/notes", response_model=ClinicalNote, status_code=status.HTTP_201_CREATED)
async def create_note(
    patient_id: UUID,
    note_in: ClinicalNoteCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new clinical note."""
    await verify_patient_access(patient_id, current_user, db)

    if note_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")

    service = ClinicalNoteService(db, current_user.practice_id)
    note = await service.create_note(note_in)
    await db.commit()
    return note


@router.get("/notes/{note_id}", response_model=ClinicalNoteWithStatus)
async def get_note(
    note_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific clinical note by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    note = await service.get_note_by_id(note_id, patient_id)
    if not note:
        raise HTTPException(status_code=404, detail="Clinical note not found")

    return ClinicalNoteWithStatus(
        **note.__dict__,
        is_signed=note.is_signed,
        is_locked=note.is_locked,
    )


@router.patch("/notes/{note_id}", response_model=ClinicalNote)
async def update_note(
    note_id: UUID,
    note_in: ClinicalNoteUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a clinical note."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    try:
        note = await service.update_note(note_id, patient_id, note_in, current_user.id)
        if not note:
            raise HTTPException(status_code=404, detail="Clinical note not found")

        await db.commit()
        return note
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/notes/{note_id}", response_model=SuccessResponse)
async def delete_note(
    note_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a clinical note (drafts only)."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    try:
        deleted = await service.delete_note(note_id, patient_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Clinical note not found")

        await db.commit()
        return SuccessResponse(message="Clinical note deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Signing Endpoints
# ============================================================================


@router.post("/notes/{note_id}/sign", response_model=SignNoteResponse)
async def sign_note(
    note_id: UUID,
    sign_request: SignNoteRequest,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Sign a clinical note."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    try:
        note = await service.sign_note(
            note_id,
            patient_id,
            current_user.id,
            sign_request.signature_ip,
            sign_request.attestation_statement,
        )
        if not note:
            raise HTTPException(status_code=404, detail="Clinical note not found")

        await db.commit()
        return SignNoteResponse(
            note_id=note.id,
            signed_at=note.signed_at,
            signed_by=note.signed_by,
            message="Note signed successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notes/{note_id}/lock", response_model=ClinicalNote)
async def lock_note(
    note_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Lock a note (administrative)."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    try:
        note = await service.lock_note(note_id, patient_id)
        if not note:
            raise HTTPException(status_code=404, detail="Clinical note not found")

        await db.commit()
        return note
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Amendment/Addendum Endpoints
# ============================================================================


@router.post("/notes/amendments", response_model=ClinicalNote, status_code=status.HTTP_201_CREATED)
async def create_amendment(
    amendment_request: CreateAmendmentRequest,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create an amendment to an existing note."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    try:
        amendment = await service.create_amendment(
            amendment_request,
            patient_id,
            current_user.id,
        )
        if not amendment:
            raise HTTPException(status_code=404, detail="Original note not found")

        await db.commit()
        return amendment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notes/addenda", response_model=ClinicalNote, status_code=status.HTTP_201_CREATED)
async def create_addendum(
    addendum_request: CreateAddendumRequest,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create an addendum to an existing note."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    try:
        addendum = await service.create_addendum(
            addendum_request,
            patient_id,
            current_user.id,
        )
        if not addendum:
            raise HTTPException(status_code=404, detail="Original note not found")

        await db.commit()
        return addendum
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/notes/{note_id}/amendments", response_model=list[ClinicalNote])
async def get_note_amendments(
    note_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all amendments for a note."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    amendments = await service.get_amendments_for_note(note_id, patient_id)
    return amendments


@router.get("/notes/{note_id}/addenda", response_model=list[ClinicalNote])
async def get_note_addenda(
    note_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all addenda for a note."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    addenda = await service.get_addenda_for_note(note_id, patient_id)
    return addenda


# ============================================================================
# Query Endpoints
# ============================================================================


@router.get("/providers/{provider_id}/unsigned-notes", response_model=list[ClinicalNote])
async def get_unsigned_notes(
    provider_id: UUID,
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get unsigned notes for a provider."""
    service = ClinicalNoteService(db, current_user.practice_id)
    notes = await service.get_unsigned_notes(provider_id, days_back)
    return notes


@router.get("/patients/{patient_id}/notes/search", response_model=list[ClinicalNote])
async def search_notes(
    patient_id: UUID,
    search_text: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Search notes by text content."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    notes = await service.search_notes(patient_id, search_text, limit)
    return notes


@router.get("/appointments/{appointment_id}/notes", response_model=list[ClinicalNote])
async def get_appointment_notes(
    appointment_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all notes for a specific appointment."""
    await verify_patient_access(patient_id, current_user, db)

    service = ClinicalNoteService(db, current_user.practice_id)
    notes = await service.get_notes_by_appointment(appointment_id, patient_id)
    return notes
