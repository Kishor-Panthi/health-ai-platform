"""Service for managing patient medical records."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.medical_records import (
    MedicalAllergyCreate,
    MedicalAllergyUpdate,
    MedicalConditionCreate,
    MedicalConditionUpdate,
    MedicalImmunizationCreate,
    MedicalImmunizationUpdate,
    MedicalMedicationCreate,
    MedicalMedicationUpdate,
    MedicalVitalsCreate,
    MedicalVitalsUpdate,
)
from app.models.medical_allergy import AllergyStatus, MedicalAllergy
from app.models.medical_condition import ConditionStatus, MedicalCondition
from app.models.medical_immunization import MedicalImmunization
from app.models.medical_medication import MedicationStatus, MedicalMedication
from app.models.medical_vitals import MedicalVitals


class MedicalRecordService:
    """Service for managing patient medical records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # Medical Allergies
    # ========================================================================

    async def get_patient_allergies(
        self,
        patient_id: UUID,
        active_only: bool = False,
    ) -> list[MedicalAllergy]:
        """Get all allergies for a patient."""
        query = select(MedicalAllergy).where(MedicalAllergy.patient_id == patient_id)

        if active_only:
            query = query.where(MedicalAllergy.status == AllergyStatus.ACTIVE)

        query = query.order_by(MedicalAllergy.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_allergy_by_id(
        self,
        allergy_id: UUID,
        patient_id: UUID,
    ) -> MedicalAllergy | None:
        """Get a specific allergy by ID."""
        query = select(MedicalAllergy).where(
            and_(
                MedicalAllergy.id == allergy_id,
                MedicalAllergy.patient_id == patient_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_allergy(
        self,
        allergy_data: MedicalAllergyCreate,
    ) -> MedicalAllergy:
        """Create a new allergy record."""
        allergy = MedicalAllergy(**allergy_data.model_dump())
        self.db.add(allergy)
        await self.db.flush()
        await self.db.refresh(allergy)
        return allergy

    async def update_allergy(
        self,
        allergy_id: UUID,
        patient_id: UUID,
        allergy_data: MedicalAllergyUpdate,
    ) -> MedicalAllergy | None:
        """Update an allergy record."""
        allergy = await self.get_allergy_by_id(allergy_id, patient_id)
        if not allergy:
            return None

        for field, value in allergy_data.model_dump(exclude_unset=True).items():
            setattr(allergy, field, value)

        await self.db.flush()
        await self.db.refresh(allergy)
        return allergy

    async def delete_allergy(
        self,
        allergy_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete an allergy record."""
        allergy = await self.get_allergy_by_id(allergy_id, patient_id)
        if not allergy:
            return False

        await self.db.delete(allergy)
        await self.db.flush()
        return True

    # ========================================================================
    # Medical Medications
    # ========================================================================

    async def get_patient_medications(
        self,
        patient_id: UUID,
        active_only: bool = False,
    ) -> list[MedicalMedication]:
        """Get all medications for a patient."""
        query = select(MedicalMedication).where(MedicalMedication.patient_id == patient_id)

        if active_only:
            query = query.where(MedicalMedication.status == MedicationStatus.ACTIVE)

        query = query.order_by(MedicalMedication.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_medication_by_id(
        self,
        medication_id: UUID,
        patient_id: UUID,
    ) -> MedicalMedication | None:
        """Get a specific medication by ID."""
        query = select(MedicalMedication).where(
            and_(
                MedicalMedication.id == medication_id,
                MedicalMedication.patient_id == patient_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_medication(
        self,
        medication_data: MedicalMedicationCreate,
    ) -> MedicalMedication:
        """Create a new medication record."""
        medication = MedicalMedication(**medication_data.model_dump())
        self.db.add(medication)
        await self.db.flush()
        await self.db.refresh(medication)
        return medication

    async def update_medication(
        self,
        medication_id: UUID,
        patient_id: UUID,
        medication_data: MedicalMedicationUpdate,
    ) -> MedicalMedication | None:
        """Update a medication record."""
        medication = await self.get_medication_by_id(medication_id, patient_id)
        if not medication:
            return None

        for field, value in medication_data.model_dump(exclude_unset=True).items():
            setattr(medication, field, value)

        await self.db.flush()
        await self.db.refresh(medication)
        return medication

    async def delete_medication(
        self,
        medication_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete a medication record."""
        medication = await self.get_medication_by_id(medication_id, patient_id)
        if not medication:
            return False

        await self.db.delete(medication)
        await self.db.flush()
        return True

    # ========================================================================
    # Medical Conditions
    # ========================================================================

    async def get_patient_conditions(
        self,
        patient_id: UUID,
        active_only: bool = False,
        chronic_only: bool = False,
    ) -> list[MedicalCondition]:
        """Get all conditions for a patient."""
        query = select(MedicalCondition).where(MedicalCondition.patient_id == patient_id)

        if active_only:
            query = query.where(MedicalCondition.status == ConditionStatus.ACTIVE)

        if chronic_only:
            query = query.where(MedicalCondition.is_chronic == True)

        query = query.order_by(MedicalCondition.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_condition_by_id(
        self,
        condition_id: UUID,
        patient_id: UUID,
    ) -> MedicalCondition | None:
        """Get a specific condition by ID."""
        query = select(MedicalCondition).where(
            and_(
                MedicalCondition.id == condition_id,
                MedicalCondition.patient_id == patient_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_condition(
        self,
        condition_data: MedicalConditionCreate,
    ) -> MedicalCondition:
        """Create a new condition record."""
        condition = MedicalCondition(**condition_data.model_dump())
        self.db.add(condition)
        await self.db.flush()
        await self.db.refresh(condition)
        return condition

    async def update_condition(
        self,
        condition_id: UUID,
        patient_id: UUID,
        condition_data: MedicalConditionUpdate,
    ) -> MedicalCondition | None:
        """Update a condition record."""
        condition = await self.get_condition_by_id(condition_id, patient_id)
        if not condition:
            return None

        for field, value in condition_data.model_dump(exclude_unset=True).items():
            setattr(condition, field, value)

        await self.db.flush()
        await self.db.refresh(condition)
        return condition

    async def delete_condition(
        self,
        condition_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete a condition record."""
        condition = await self.get_condition_by_id(condition_id, patient_id)
        if not condition:
            return False

        await self.db.delete(condition)
        await self.db.flush()
        return True

    # ========================================================================
    # Medical Immunizations
    # ========================================================================

    async def get_patient_immunizations(
        self,
        patient_id: UUID,
    ) -> list[MedicalImmunization]:
        """Get all immunizations for a patient."""
        query = (
            select(MedicalImmunization)
            .where(MedicalImmunization.patient_id == patient_id)
            .order_by(MedicalImmunization.administration_date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_immunization_by_id(
        self,
        immunization_id: UUID,
        patient_id: UUID,
    ) -> MedicalImmunization | None:
        """Get a specific immunization by ID."""
        query = select(MedicalImmunization).where(
            and_(
                MedicalImmunization.id == immunization_id,
                MedicalImmunization.patient_id == patient_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_immunization(
        self,
        immunization_data: MedicalImmunizationCreate,
    ) -> MedicalImmunization:
        """Create a new immunization record."""
        immunization = MedicalImmunization(**immunization_data.model_dump())
        self.db.add(immunization)
        await self.db.flush()
        await self.db.refresh(immunization)
        return immunization

    async def update_immunization(
        self,
        immunization_id: UUID,
        patient_id: UUID,
        immunization_data: MedicalImmunizationUpdate,
    ) -> MedicalImmunization | None:
        """Update an immunization record."""
        immunization = await self.get_immunization_by_id(immunization_id, patient_id)
        if not immunization:
            return None

        for field, value in immunization_data.model_dump(exclude_unset=True).items():
            setattr(immunization, field, value)

        await self.db.flush()
        await self.db.refresh(immunization)
        return immunization

    async def delete_immunization(
        self,
        immunization_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete an immunization record."""
        immunization = await self.get_immunization_by_id(immunization_id, patient_id)
        if not immunization:
            return False

        await self.db.delete(immunization)
        await self.db.flush()
        return True

    # ========================================================================
    # Medical Vitals
    # ========================================================================

    async def get_patient_vitals(
        self,
        patient_id: UUID,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[MedicalVitals]:
        """Get vitals for a patient with optional date filtering."""
        query = select(MedicalVitals).where(MedicalVitals.patient_id == patient_id)

        if start_date:
            query = query.where(MedicalVitals.measurement_date >= start_date)
        if end_date:
            query = query.where(MedicalVitals.measurement_date <= end_date)

        query = query.order_by(
            MedicalVitals.measurement_date.desc(),
            MedicalVitals.measurement_time.desc(),
        ).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_vitals_by_id(
        self,
        vitals_id: UUID,
        patient_id: UUID,
    ) -> MedicalVitals | None:
        """Get specific vitals by ID."""
        query = select(MedicalVitals).where(
            and_(
                MedicalVitals.id == vitals_id,
                MedicalVitals.patient_id == patient_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_vitals(
        self,
        vitals_data: MedicalVitalsCreate,
    ) -> MedicalVitals:
        """Create a new vitals record."""
        vitals = MedicalVitals(**vitals_data.model_dump())

        # Auto-calculate BMI if height and weight are provided
        if vitals.height and vitals.weight and not vitals.bmi:
            vitals.bmi = vitals.calculate_bmi()

        self.db.add(vitals)
        await self.db.flush()
        await self.db.refresh(vitals)
        return vitals

    async def update_vitals(
        self,
        vitals_id: UUID,
        patient_id: UUID,
        vitals_data: MedicalVitalsUpdate,
    ) -> MedicalVitals | None:
        """Update a vitals record."""
        vitals = await self.get_vitals_by_id(vitals_id, patient_id)
        if not vitals:
            return None

        for field, value in vitals_data.model_dump(exclude_unset=True).items():
            setattr(vitals, field, value)

        # Recalculate BMI if height or weight changed
        if 'height' in vitals_data.model_dump(exclude_unset=True) or 'weight' in vitals_data.model_dump(exclude_unset=True):
            if vitals.height and vitals.weight:
                vitals.bmi = vitals.calculate_bmi()

        await self.db.flush()
        await self.db.refresh(vitals)
        return vitals

    async def delete_vitals(
        self,
        vitals_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete a vitals record."""
        vitals = await self.get_vitals_by_id(vitals_id, patient_id)
        if not vitals:
            return False

        await self.db.delete(vitals)
        await self.db.flush()
        return True

    # ========================================================================
    # Comprehensive Patient Medical Summary
    # ========================================================================

    async def get_patient_medical_summary(
        self,
        patient_id: UUID,
    ) -> dict:
        """Get comprehensive medical summary for a patient."""
        allergies = await self.get_patient_allergies(patient_id, active_only=True)
        medications = await self.get_patient_medications(patient_id, active_only=True)
        conditions = await self.get_patient_conditions(patient_id, active_only=True)
        immunizations = await self.get_patient_immunizations(patient_id)
        vitals = await self.get_patient_vitals(patient_id, limit=10)

        return {
            'patient_id': patient_id,
            'allergies': allergies,
            'medications': medications,
            'conditions': conditions,
            'immunizations': immunizations,
            'recent_vitals': vitals,
        }
