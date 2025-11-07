"""Pydantic schemas for insurance."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.insurance_policy import PolicyStatus, PolicyType
from app.models.insurance_verification import VerificationMethod, VerificationStatus


# ============================================================================
# Insurance Policy Schemas
# ============================================================================


class InsurancePolicyBase(BaseModel):
    """Base schema for insurance policies."""

    policy_number: str = Field(..., max_length=100, description="Insurance policy number")
    insurance_company: str = Field(..., max_length=255, description="Insurance company name")
    insurance_phone: Optional[str] = Field(None, max_length=32, description="Insurance company phone")
    policy_type: PolicyType = Field(..., description="Type of policy")
    policy_holder_name: Optional[str] = Field(None, max_length=255, description="Policy holder name")
    policy_holder_relationship: Optional[str] = Field(None, max_length=50, description="Relationship to patient")
    policy_holder_dob: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Policy holder DOB")
    group_number: Optional[str] = Field(None, max_length=100, description="Group number")
    plan_name: Optional[str] = Field(None, max_length=255, description="Plan name")
    effective_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Policy effective date")
    termination_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Policy termination date")
    status: PolicyStatus = Field(default=PolicyStatus.ACTIVE, description="Policy status")
    copay: Optional[Decimal] = Field(None, ge=0, le=9999.99, description="Copay amount")
    deductible: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Deductible amount")
    deductible_met: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Amount of deductible met")
    out_of_pocket_max: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Out-of-pocket maximum")
    out_of_pocket_met: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Amount of OOP met")
    is_primary: bool = Field(default=True, description="Is this the primary insurance")
    priority_order: int = Field(default=1, ge=1, le=10, description="Priority order (1=primary, 2=secondary, etc)")
    notes: Optional[str] = Field(None, description="Additional notes")


class InsurancePolicyCreate(InsurancePolicyBase):
    """Schema for creating an insurance policy."""

    patient_id: UUID = Field(..., description="Patient ID")


class InsurancePolicyUpdate(BaseModel):
    """Schema for updating an insurance policy."""

    policy_number: Optional[str] = Field(None, max_length=100)
    insurance_company: Optional[str] = Field(None, max_length=255)
    insurance_phone: Optional[str] = Field(None, max_length=32)
    policy_type: Optional[PolicyType] = None
    policy_holder_name: Optional[str] = Field(None, max_length=255)
    policy_holder_relationship: Optional[str] = Field(None, max_length=50)
    policy_holder_dob: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    group_number: Optional[str] = Field(None, max_length=100)
    plan_name: Optional[str] = Field(None, max_length=255)
    effective_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    termination_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    status: Optional[PolicyStatus] = None
    copay: Optional[Decimal] = Field(None, ge=0, le=9999.99)
    deductible: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    deductible_met: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    out_of_pocket_max: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    out_of_pocket_met: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    is_primary: Optional[bool] = None
    priority_order: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class InsurancePolicy(InsurancePolicyBase):
    """Schema for insurance policy response."""

    id: UUID
    patient_id: UUID
    practice_id: UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


# ============================================================================
# Insurance Verification Schemas
# ============================================================================


class InsuranceVerificationBase(BaseModel):
    """Base schema for insurance verifications."""

    verification_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date of verification")
    verification_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}:\d{2}$', description="Time of verification")
    method: VerificationMethod = Field(..., description="Verification method")
    status: VerificationStatus = Field(..., description="Verification status")
    verified_by: Optional[UUID] = Field(None, description="User who performed verification")
    reference_number: Optional[str] = Field(None, max_length=100, description="Reference/confirmation number")
    representative_name: Optional[str] = Field(None, max_length=255, description="Insurance rep name")
    representative_id: Optional[str] = Field(None, max_length=100, description="Insurance rep ID")
    effective_date_verified: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Verified effective date")
    termination_date_verified: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Verified termination date")
    benefits_verified: Optional[dict[str, Any]] = Field(None, description="Verified benefits details (JSON)")
    copay_verified: Optional[Decimal] = Field(None, ge=0, le=9999.99, description="Verified copay")
    deductible_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Verified deductible")
    deductible_met_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Verified deductible met")
    out_of_pocket_max_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Verified OOP max")
    out_of_pocket_met_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99, description="Verified OOP met")
    requires_authorization: Optional[bool] = Field(None, description="Does service require authorization")
    authorization_number: Optional[str] = Field(None, max_length=100, description="Authorization number if obtained")
    notes: Optional[str] = Field(None, description="Additional verification notes")
    next_verification_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Next verification date")


class InsuranceVerificationCreate(InsuranceVerificationBase):
    """Schema for creating an insurance verification."""

    policy_id: UUID = Field(..., description="Insurance policy ID")


class InsuranceVerificationUpdate(BaseModel):
    """Schema for updating an insurance verification."""

    verification_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    verification_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}:\d{2}$')
    method: Optional[VerificationMethod] = None
    status: Optional[VerificationStatus] = None
    verified_by: Optional[UUID] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    representative_name: Optional[str] = Field(None, max_length=255)
    representative_id: Optional[str] = Field(None, max_length=100)
    effective_date_verified: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    termination_date_verified: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    benefits_verified: Optional[dict[str, Any]] = None
    copay_verified: Optional[Decimal] = Field(None, ge=0, le=9999.99)
    deductible_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    deductible_met_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    out_of_pocket_max_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    out_of_pocket_met_verified: Optional[Decimal] = Field(None, ge=0, le=99999.99)
    requires_authorization: Optional[bool] = None
    authorization_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    next_verification_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')


class InsuranceVerification(InsuranceVerificationBase):
    """Schema for insurance verification response."""

    id: UUID
    policy_id: UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


# ============================================================================
# Combined Schemas
# ============================================================================


class InsurancePolicyWithVerifications(InsurancePolicy):
    """Insurance policy with verification history."""

    verifications: list[InsuranceVerification] = Field(default_factory=list)

    model_config = {'from_attributes': True}
