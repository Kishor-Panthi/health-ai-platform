"""add all missing tables - providers, staff, medical records, billing, clinical docs, communications, analytics

Revision ID: 002
Revises: 001
Create Date: 2025-11-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================================
    # PHASE 1: Provider & Staff Management
    # ============================================================================

    # Providers table
    op.create_table('providers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('npi', sa.String(length=10), nullable=True),
        sa.Column('dea_number', sa.String(length=20), nullable=True),
        sa.Column('specialty', sa.String(length=100), nullable=True),
        sa.Column('credentials', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE')
    )
    op.create_index('idx_providers_practice', 'providers', ['practice_id'])
    op.create_index('idx_providers_npi', 'providers', ['npi'], unique=True, postgresql_where=sa.text('npi IS NOT NULL'))
    op.create_index('idx_providers_active', 'providers', ['is_active'])

    # Staff table
    op.create_table('staff',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE')
    )
    op.create_index('idx_staff_practice', 'staff', ['practice_id'])
    op.create_index('idx_staff_role', 'staff', ['role'])
    op.create_index('idx_staff_active', 'staff', ['is_active'])

    # Provider Schedules table
    op.create_table('provider_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),  # 0=Monday, 6=Sunday
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE')
    )
    op.create_index('idx_provider_schedules_provider', 'provider_schedules', ['provider_id'])
    op.create_index('idx_provider_schedules_day', 'provider_schedules', ['day_of_week'])

    # ============================================================================
    # PHASE 2: Medical Records & Insurance
    # ============================================================================

    # Allergies table
    op.create_table('allergies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('allergen', sa.String(length=200), nullable=False),
        sa.Column('reaction', sa.String(length=500), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=True),  # mild, moderate, severe
        sa.Column('onset_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),  # active, inactive, resolved
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE')
    )
    op.create_index('idx_allergies_patient', 'allergies', ['patient_id'])
    op.create_index('idx_allergies_status', 'allergies', ['status'])

    # Medications table
    op.create_table('medications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medication_name', sa.String(length=200), nullable=False),
        sa.Column('dosage', sa.String(length=100), nullable=True),
        sa.Column('frequency', sa.String(length=100), nullable=True),
        sa.Column('route', sa.String(length=50), nullable=True),
        sa.Column('prescribing_provider_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),  # active, discontinued, completed
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prescribing_provider_id'], ['providers.id'], ondelete='SET NULL')
    )
    op.create_index('idx_medications_patient', 'medications', ['patient_id'])
    op.create_index('idx_medications_status', 'medications', ['status'])

    # Conditions table
    op.create_table('conditions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('condition_name', sa.String(length=200), nullable=False),
        sa.Column('icd10_code', sa.String(length=10), nullable=True),
        sa.Column('onset_date', sa.Date(), nullable=True),
        sa.Column('resolved_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),  # active, resolved, chronic
        sa.Column('severity', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE')
    )
    op.create_index('idx_conditions_patient', 'conditions', ['patient_id'])
    op.create_index('idx_conditions_status', 'conditions', ['status'])
    op.create_index('idx_conditions_icd10', 'conditions', ['icd10_code'])

    # Vitals table
    op.create_table('vitals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recorded_by', postgresql.UUID(as_uuid=True), nullable=True),  # staff or provider id
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('temperature', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('blood_pressure_systolic', sa.Integer(), nullable=True),
        sa.Column('blood_pressure_diastolic', sa.Integer(), nullable=True),
        sa.Column('respiratory_rate', sa.Integer(), nullable=True),
        sa.Column('oxygen_saturation', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('height', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('bmi', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE')
    )
    op.create_index('idx_vitals_patient', 'vitals', ['patient_id'])
    op.create_index('idx_vitals_recorded', 'vitals', ['recorded_at'])

    # Immunizations table
    op.create_table('immunizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vaccine_name', sa.String(length=200), nullable=False),
        sa.Column('cvx_code', sa.String(length=10), nullable=True),  # CDC vaccine code
        sa.Column('administered_date', sa.Date(), nullable=False),
        sa.Column('administered_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('lot_number', sa.String(length=100), nullable=True),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('site', sa.String(length=100), nullable=True),  # injection site
        sa.Column('route', sa.String(length=50), nullable=True),
        sa.Column('dose', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['administered_by'], ['providers.id'], ondelete='SET NULL')
    )
    op.create_index('idx_immunizations_patient', 'immunizations', ['patient_id'])
    op.create_index('idx_immunizations_date', 'immunizations', ['administered_date'])

    # Insurance Policies table
    op.create_table('insurance_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insurance_company', sa.String(length=200), nullable=False),
        sa.Column('policy_number', sa.String(length=100), nullable=False),
        sa.Column('group_number', sa.String(length=100), nullable=True),
        sa.Column('subscriber_name', sa.String(length=200), nullable=True),
        sa.Column('subscriber_dob', sa.Date(), nullable=True),
        sa.Column('relationship_to_patient', sa.String(length=50), nullable=True),
        sa.Column('policy_type', sa.String(length=50), nullable=True),  # primary, secondary, tertiary
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('copay_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('deductible', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE')
    )
    op.create_index('idx_insurance_patient', 'insurance_policies', ['patient_id'])
    op.create_index('idx_insurance_active', 'insurance_policies', ['is_active'])

    # Insurance Verifications table
    op.create_table('insurance_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insurance_policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('verified_date', sa.DateTime(), nullable=False),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verification_method', sa.String(length=50), nullable=True),  # phone, online, fax
        sa.Column('coverage_status', sa.String(length=50), nullable=False),  # active, inactive, pending
        sa.Column('coverage_details', postgresql.JSONB(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['insurance_policy_id'], ['insurance_policies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_verification_policy', 'insurance_verifications', ['insurance_policy_id'])
    op.create_index('idx_verification_date', 'insurance_verifications', ['verified_date'])

    # ============================================================================
    # PHASE 3: Billing & Clinical Documentation
    # ============================================================================

    # Billing Claims table
    op.create_table('billing_claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('appointment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('insurance_policy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('claim_number', sa.String(length=50), nullable=True, unique=True),
        sa.Column('date_of_service', sa.Date(), nullable=False),
        sa.Column('total_charge', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('insurance_payment', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('patient_payment', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('adjustment', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('claim_status', sa.String(length=50), nullable=False, server_default='pending'),
        # pending, submitted, accepted, rejected, paid, denied, appealed
        sa.Column('submitted_date', sa.DateTime(), nullable=True),
        sa.Column('paid_date', sa.DateTime(), nullable=True),
        sa.Column('denial_reason', sa.Text(), nullable=True),
        sa.Column('diagnosis_codes', postgresql.JSONB(), nullable=True),  # ICD-10 codes
        sa.Column('procedure_codes', postgresql.JSONB(), nullable=True),  # CPT codes
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['insurance_policy_id'], ['insurance_policies.id'], ondelete='SET NULL')
    )
    op.create_index('idx_claims_practice', 'billing_claims', ['practice_id'])
    op.create_index('idx_claims_patient', 'billing_claims', ['patient_id'])
    op.create_index('idx_claims_status', 'billing_claims', ['claim_status'])
    op.create_index('idx_claims_dos', 'billing_claims', ['date_of_service'])

    # Billing Payments table
    op.create_table('billing_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('claim_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),  # cash, check, card, insurance
        sa.Column('payment_source', sa.String(length=50), nullable=False),  # patient, insurance
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claim_id'], ['billing_claims.id'], ondelete='SET NULL')
    )
    op.create_index('idx_payments_practice', 'billing_payments', ['practice_id'])
    op.create_index('idx_payments_patient', 'billing_payments', ['patient_id'])
    op.create_index('idx_payments_date', 'billing_payments', ['payment_date'])

    # Billing Transactions table
    op.create_table('billing_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('claim_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),  # charge, payment, adjustment
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claim_id'], ['billing_claims.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_transactions_practice', 'billing_transactions', ['practice_id'])
    op.create_index('idx_transactions_patient', 'billing_transactions', ['patient_id'])
    op.create_index('idx_transactions_date', 'billing_transactions', ['transaction_date'])

    # Clinical Notes table
    op.create_table('clinical_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('appointment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note_type', sa.String(length=50), nullable=False),  # SOAP, progress, H&P, consult
        sa.Column('note_date', sa.DateTime(), nullable=False),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('subjective', sa.Text(), nullable=True),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('assessment', sa.Text(), nullable=True),
        sa.Column('plan', sa.Text(), nullable=True),
        sa.Column('full_note', sa.Text(), nullable=True),
        sa.Column('is_signed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('signed_at', sa.DateTime(), nullable=True),
        sa.Column('signed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signed_by'], ['providers.id'], ondelete='SET NULL')
    )
    op.create_index('idx_notes_practice', 'clinical_notes', ['practice_id'])
    op.create_index('idx_notes_patient', 'clinical_notes', ['patient_id'])
    op.create_index('idx_notes_provider', 'clinical_notes', ['provider_id'])
    op.create_index('idx_notes_date', 'clinical_notes', ['note_date'])

    # Documents table
    op.create_table('documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=False),  # lab_result, imaging, consent, etc
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_documents_practice', 'documents', ['practice_id'])
    op.create_index('idx_documents_patient', 'documents', ['patient_id'])
    op.create_index('idx_documents_type', 'documents', ['document_type'])

    # ============================================================================
    # PHASE 4: Communications & Notifications
    # ============================================================================

    # Messages table
    op.create_table('messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),  # email, sms, internal
        sa.Column('from_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_patient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('parent_message_id', postgresql.UUID(as_uuid=True), nullable=True),  # for threading
        sa.Column('status', sa.String(length=50), nullable=False, server_default='sent'),  # sent, delivered, read, failed
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['to_patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_message_id'], ['messages.id'], ondelete='SET NULL')
    )
    op.create_index('idx_messages_practice', 'messages', ['practice_id'])
    op.create_index('idx_messages_from', 'messages', ['from_user_id'])
    op.create_index('idx_messages_to_patient', 'messages', ['to_patient_id'])
    op.create_index('idx_messages_to_user', 'messages', ['to_user_id'])
    op.create_index('idx_messages_sent', 'messages', ['sent_at'])

    # Notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        # appointment_reminder, lab_result, message_received, payment_due, etc
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),  # email, sms, push, in_app
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        # pending, sent, delivered, failed
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE')
    )
    op.create_index('idx_notifications_practice', 'notifications', ['practice_id'])
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])
    op.create_index('idx_notifications_patient', 'notifications', ['patient_id'])
    op.create_index('idx_notifications_read', 'notifications', ['is_read'])

    # Tasks table
    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(length=50), nullable=False),  # follow_up, referral, lab_review, etc
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='normal'),  # low, normal, high, urgent
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        # pending, in_progress, completed, cancelled
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE')
    )
    op.create_index('idx_tasks_practice', 'tasks', ['practice_id'])
    op.create_index('idx_tasks_assigned', 'tasks', ['assigned_to'])
    op.create_index('idx_tasks_patient', 'tasks', ['patient_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_due', 'tasks', ['due_date'])

    # ============================================================================
    # PHASE 5: Reporting & Analytics
    # ============================================================================

    # Reports table
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        # pending, processing, completed, failed
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_reports_practice', 'reports', ['practice_id'])
    op.create_index('idx_reports_type', 'reports', ['report_type'])
    op.create_index('idx_reports_date', 'reports', ['generated_at'])

    # Report Schedules table
    op.create_table('report_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('schedule', sa.String(length=50), nullable=False),  # daily, weekly, monthly
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('recipients', postgresql.JSONB(), nullable=True),  # email addresses
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_schedules_practice', 'report_schedules', ['practice_id'])
    op.create_index('idx_schedules_active', 'report_schedules', ['is_active'])
    op.create_index('idx_schedules_next_run', 'report_schedules', ['next_run_at'])

    # Dashboards table
    op.create_table('dashboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),  # null = shared dashboard
        sa.Column('dashboard_name', sa.String(length=255), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('layout', postgresql.JSONB(), nullable=True),  # grid layout configuration
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('idx_dashboards_practice', 'dashboards', ['practice_id'])
    op.create_index('idx_dashboards_user', 'dashboards', ['user_id'])

    # Dashboard Widgets table
    op.create_table('dashboard_widgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('widget_type', sa.String(length=50), nullable=False),
        # patient_count, appointment_count, revenue_chart, etc
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('configuration', postgresql.JSONB(), nullable=True),
        sa.Column('position', postgresql.JSONB(), nullable=True),  # x, y, w, h for grid
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE')
    )
    op.create_index('idx_widgets_dashboard', 'dashboard_widgets', ['dashboard_id'])


def downgrade():
    # Drop all tables in reverse order (respecting foreign keys)
    op.drop_table('dashboard_widgets')
    op.drop_table('dashboards')
    op.drop_table('report_schedules')
    op.drop_table('reports')
    op.drop_table('tasks')
    op.drop_table('notifications')
    op.drop_table('messages')
    op.drop_table('documents')
    op.drop_table('clinical_notes')
    op.drop_table('billing_transactions')
    op.drop_table('billing_payments')
    op.drop_table('billing_claims')
    op.drop_table('insurance_verifications')
    op.drop_table('insurance_policies')
    op.drop_table('immunizations')
    op.drop_table('vitals')
    op.drop_table('conditions')
    op.drop_table('medications')
    op.drop_table('allergies')
    op.drop_table('provider_schedules')
    op.drop_table('staff')
    op.drop_table('providers')
