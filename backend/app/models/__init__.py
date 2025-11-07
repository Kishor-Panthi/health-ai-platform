"""Database models."""

from app.models.base import Base
from app.models.practice import Practice
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.audit import AuditLog
from app.models.provider import Provider
from app.models.staff import Staff, StaffRole
from app.models.provider_schedule import ProviderSchedule, DayOfWeek

# Medical Records
from app.models.medical_allergy import MedicalAllergy, AllergySeverity, AllergyStatus
from app.models.medical_medication import MedicalMedication, MedicationStatus, MedicationRoute
from app.models.medical_condition import MedicalCondition, ConditionStatus, ConditionSeverity
from app.models.medical_immunization import MedicalImmunization
from app.models.medical_vitals import MedicalVitals

# Insurance
from app.models.insurance_policy import InsurancePolicy, PolicyType, PolicyStatus
from app.models.insurance_verification import InsuranceVerification, VerificationStatus, VerificationMethod

# Billing
from app.models.billing_claim import BillingClaim, ClaimStatus, ClaimType
from app.models.billing_payment import BillingPayment, PaymentMethod, PaymentStatus, PaymentSource
from app.models.billing_transaction import BillingTransaction, TransactionType, AdjustmentReason

# Clinical Documentation
from app.models.clinical_note import ClinicalNote, NoteType, NoteStatus
from app.models.document import Document, DocumentType, DocumentStatus

# Communications & Automation
from app.models.message import Message, MessageType, MessagePriority, MessageStatus
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationChannel, NotificationStatus
from app.models.task import Task, TaskType, TaskStatus, TaskPriority

# Analytics & Reporting
from app.models.report import Report, ReportType, ReportStatus, ReportFormat
from app.models.report_schedule import ReportSchedule, ScheduleFrequency, ScheduleStatus, DeliveryMethod
from app.models.dashboard import Dashboard, DashboardWidget, DashboardType, WidgetType, RefreshInterval

__all__ = [
    'Base',
    'Practice',
    'User',
    'UserRole',
    'Patient',
    'Appointment',
    'AuditLog',
    'Provider',
    'Staff',
    'StaffRole',
    'ProviderSchedule',
    'DayOfWeek',
    # Medical Records
    'MedicalAllergy',
    'AllergySeverity',
    'AllergyStatus',
    'MedicalMedication',
    'MedicationStatus',
    'MedicationRoute',
    'MedicalCondition',
    'ConditionStatus',
    'ConditionSeverity',
    'MedicalImmunization',
    'MedicalVitals',
    # Insurance
    'InsurancePolicy',
    'PolicyType',
    'PolicyStatus',
    'InsuranceVerification',
    'VerificationStatus',
    'VerificationMethod',
    # Billing
    'BillingClaim',
    'ClaimStatus',
    'ClaimType',
    'BillingPayment',
    'PaymentMethod',
    'PaymentStatus',
    'PaymentSource',
    'BillingTransaction',
    'TransactionType',
    'AdjustmentReason',
    # Clinical Documentation
    'ClinicalNote',
    'NoteType',
    'NoteStatus',
    'Document',
    'DocumentType',
    'DocumentStatus',
    # Communications & Automation
    'Message',
    'MessageType',
    'MessagePriority',
    'MessageStatus',
    'Notification',
    'NotificationType',
    'NotificationPriority',
    'NotificationChannel',
    'NotificationStatus',
    'Task',
    'TaskType',
    'TaskStatus',
    'TaskPriority',
    # Analytics & Reporting
    'Report',
    'ReportType',
    'ReportStatus',
    'ReportFormat',
    'ReportSchedule',
    'ScheduleFrequency',
    'ScheduleStatus',
    'DeliveryMethod',
    'Dashboard',
    'DashboardWidget',
    'DashboardType',
    'WidgetType',
    'RefreshInterval',
]
