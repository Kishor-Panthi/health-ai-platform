"""add e-prescribing tables - drugs, pharmacies, prescriptions, drug interactions

Revision ID: 003
Revises: 002
Create Date: 2025-11-13 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================================
    # E-PRESCRIBING TABLES
    # ============================================================================

    # Drugs table - comprehensive drug database
    op.create_table('drugs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ndc', sa.String(length=11), nullable=False, unique=True),  # National Drug Code
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=True),
        sa.Column('brand_name', sa.String(length=255), nullable=True),
        sa.Column('strength', sa.String(length=100), nullable=True),
        sa.Column('dosage_form', sa.String(length=100), nullable=True),  # tablet, capsule, liquid, injection
        sa.Column('route', sa.String(length=50), nullable=True),  # oral, topical, IV, IM
        sa.Column('dea_schedule', sa.String(length=10), nullable=True),  # I, II, III, IV, V for controlled substances
        sa.Column('manufacturer', sa.String(length=255), nullable=True),
        sa.Column('active_ingredients', postgresql.JSONB(), nullable=True),
        sa.Column('inactive_ingredients', postgresql.JSONB(), nullable=True),
        sa.Column('warnings', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_drugs_ndc', 'drugs', ['ndc'], unique=True)
    op.create_index('idx_drugs_name', 'drugs', ['name'])
    op.create_index('idx_drugs_generic', 'drugs', ['generic_name'])
    op.create_index('idx_drugs_brand', 'drugs', ['brand_name'])
    op.create_index('idx_drugs_active', 'drugs', ['is_active'])
    # Full-text search indexes for drug names
    op.execute("""
        CREATE INDEX idx_drugs_name_fts ON drugs
        USING gin(to_tsvector('english', name));
    """)
    op.execute("""
        CREATE INDEX idx_drugs_generic_fts ON drugs
        USING gin(to_tsvector('english', generic_name));
    """)

    # Drug Interactions table
    op.create_table('drug_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drug_ndc_1', sa.String(length=11), nullable=False),
        sa.Column('drug_ndc_2', sa.String(length=11), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),  # severe, moderate, minor
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('mechanism', sa.Text(), nullable=True),  # How interaction occurs
        sa.Column('management', sa.Text(), nullable=True),  # Clinical recommendations
        sa.Column('documentation', sa.String(length=50), nullable=True),  # well-documented, theoretical
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['drug_ndc_1'], ['drugs.ndc'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['drug_ndc_2'], ['drugs.ndc'], ondelete='CASCADE')
    )
    op.create_index('idx_interactions_drug1', 'drug_interactions', ['drug_ndc_1'])
    op.create_index('idx_interactions_drug2', 'drug_interactions', ['drug_ndc_2'])
    op.create_index('idx_interactions_severity', 'drug_interactions', ['severity'])
    # Unique constraint to prevent duplicate interactions
    op.create_index(
        'idx_interactions_unique',
        'drug_interactions',
        ['drug_ndc_1', 'drug_ndc_2'],
        unique=True
    )

    # Pharmacies table
    op.create_table('pharmacies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ncpdp_id', sa.String(length=7), nullable=False, unique=True),
        # National Council for Prescription Drug Programs ID
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('fax', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_24_hour', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('accepts_eprescribe', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_verified', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_pharmacies_ncpdp', 'pharmacies', ['ncpdp_id'], unique=True)
    op.create_index('idx_pharmacies_zip', 'pharmacies', ['zip_code'])
    op.create_index('idx_pharmacies_city_state', 'pharmacies', ['city', 'state'])
    op.create_index('idx_pharmacies_name', 'pharmacies', ['name'])

    # Prescriptions table
    op.create_table('prescriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pharmacy_ncpdp', sa.String(length=7), nullable=True),

        # Drug Information
        sa.Column('drug_ndc', sa.String(length=11), nullable=False),
        sa.Column('drug_name', sa.String(length=255), nullable=False),
        sa.Column('strength', sa.String(length=100), nullable=True),
        sa.Column('dosage_form', sa.String(length=100), nullable=True),

        # Prescription Details
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('days_supply', sa.Integer(), nullable=False),
        sa.Column('refills', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sig', sa.Text(), nullable=False),  # Directions for patient
        sa.Column('notes', sa.Text(), nullable=True),  # Internal notes

        # Status Tracking
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        # pending, sent, accepted, rejected, cancelled, completed
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),

        # Rejection/Error Handling
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),

        # Surescripts Message IDs
        sa.Column('message_id', sa.String(length=100), nullable=True),
        sa.Column('relates_to_message_id', sa.String(length=100), nullable=True),

        # Controlled Substance Tracking
        sa.Column('is_controlled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dea_schedule', sa.String(length=10), nullable=True),
        sa.Column('epcs_signature', sa.String(length=500), nullable=True),  # Digital signature for EPCS

        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pharmacy_ncpdp'], ['pharmacies.ncpdp_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['drug_ndc'], ['drugs.ndc'], ondelete='RESTRICT')
    )
    op.create_index('idx_prescriptions_practice', 'prescriptions', ['practice_id'])
    op.create_index('idx_prescriptions_patient', 'prescriptions', ['patient_id'])
    op.create_index('idx_prescriptions_provider', 'prescriptions', ['provider_id'])
    op.create_index('idx_prescriptions_pharmacy', 'prescriptions', ['pharmacy_ncpdp'])
    op.create_index('idx_prescriptions_status', 'prescriptions', ['status'])
    op.create_index('idx_prescriptions_drug', 'prescriptions', ['drug_ndc'])
    op.create_index('idx_prescriptions_created', 'prescriptions', ['created_at'])

    # Prescription History (for medication history from PBMs)
    op.create_table('prescription_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drug_ndc', sa.String(length=11), nullable=True),
        sa.Column('drug_name', sa.String(length=255), nullable=False),
        sa.Column('prescriber_name', sa.String(length=200), nullable=True),
        sa.Column('prescriber_npi', sa.String(length=10), nullable=True),
        sa.Column('pharmacy_name', sa.String(length=255), nullable=True),
        sa.Column('fill_date', sa.Date(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('days_supply', sa.Integer(), nullable=True),
        sa.Column('refills_remaining', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),  # surescripts, manual
        sa.Column('retrieved_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE')
    )
    op.create_index('idx_rx_history_patient', 'prescription_history', ['patient_id'])
    op.create_index('idx_rx_history_fill_date', 'prescription_history', ['fill_date'])


def downgrade():
    op.drop_table('prescription_history')
    op.drop_table('prescriptions')
    op.drop_table('pharmacies')
    op.drop_table('drug_interactions')

    # Drop full-text search indexes
    op.execute("DROP INDEX IF EXISTS idx_drugs_name_fts")
    op.execute("DROP INDEX IF EXISTS idx_drugs_generic_fts")

    op.drop_table('drugs')
