# Implementation Plan: E-Prescribing, Patient Portal & Infrastructure

## Overview

Based on comprehensive codebase analysis:
- **Backend**: 85% complete, missing migrations + integrations
- **Frontend**: 100% UI built, 0% connected to APIs
- **Gap**: E-prescribing, patient portal, production infrastructure

## Priority Order

### Phase 0: Critical Fixes (2-3 days) 🔴
**Must do before anything else**
1. Generate all database migrations (23 missing tables)
2. Set up basic third-party integrations (Email, S3)
3. Connect frontend to existing backend APIs

### Phase 1: E-Prescribing (2-3 weeks) 🟠
**Critical for Practice Fusion parity**
1. Surescripts API integration
2. Drug database & interaction checking
3. Pharmacy search & prescription transmission
4. EPCS for controlled substances

### Phase 2: Patient Portal (2-3 weeks) 🟡
**Table stakes feature**
1. Patient authentication & registration
2. Online appointment booking
3. Medical records view
4. Secure messaging
5. Intake forms

### Phase 3: Infrastructure (1 week) 🟢
**Production readiness**
1. Monitoring & alerts (Datadog/Sentry)
2. Cloud storage (S3)
3. Email/SMS (SendGrid/Twilio)
4. Caching (Redis)

---

## Phase 0: Critical Fixes (Days 1-3)

### Day 1: Database Migrations

**Problem**: Only 5 of 28 tables migrated to database

**Solution**: Generate comprehensive migrations

```bash
# backend/alembic/versions/

# Generate migration for all missing tables
alembic revision --autogenerate -m "add_all_missing_tables"

# Tables to migrate:
# - providers, staff, provider_schedules (3)
# - allergies, medications, conditions, vitals, immunizations (5)
# - insurance_policies, insurance_verifications (2)
# - billing_claims, billing_payments, billing_transactions (3)
# - clinical_notes, documents (2)
# - messages, notifications, tasks (3)
# - reports, report_schedules, dashboards, dashboard_widgets (4)
# - prescriptions (1) - NEW for e-prescribing
```

**Code to Create**:
```python
# backend/alembic/versions/002_add_all_missing_tables.py
"""add all missing tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-13
"""

def upgrade():
    # Providers & Staff
    op.create_table('providers',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('practice_id', postgresql.UUID(), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('npi', sa.String(10), nullable=True),
        sa.Column('dea_number', sa.String(20), nullable=True),
        sa.Column('specialty', sa.String(100), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id'])
    )
    op.create_index('idx_providers_npi', 'providers', ['npi'])
    op.create_index('idx_providers_practice', 'providers', ['practice_id'])

    # Continue for all 23 missing tables...
    # (Full implementation below)

def downgrade():
    op.drop_table('providers')
    # Drop all tables in reverse order
```

**Validation**:
```bash
# Run migration
alembic upgrade head

# Verify all tables exist
psql -d healthai -c "\dt"
```

### Day 2: Basic API Integration (Frontend)

**Problem**: Frontend uses 100% mock data

**Solution**: Create API client and connect to real endpoints

```typescript
// frontend/src/lib/api/client.ts
import { QueryClient } from '@tanstack/react-query';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getToken();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Patient endpoints
  async getPatients(params?: { search?: string; status?: string }) {
    const queryString = new URLSearchParams(params).toString();
    return this.request<{ data: Patient[] }>(`/api/v1/patients?${queryString}`);
  }

  async getPatient(id: string) {
    return this.request<{ data: Patient }>(`/api/v1/patients/${id}`);
  }

  async createPatient(data: CreatePatientRequest) {
    return this.request<{ data: Patient }>('/api/v1/patients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePatient(id: string, data: UpdatePatientRequest) {
    return this.request<{ data: Patient }>(`/api/v1/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Appointment endpoints
  async getAppointments(params?: {
    start_date?: string;
    end_date?: string;
    provider_id?: string;
  }) {
    const queryString = new URLSearchParams(params).toString();
    return this.request<{ data: Appointment[] }>(`/api/v1/appointments?${queryString}`);
  }

  async createAppointment(data: CreateAppointmentRequest) {
    return this.request<{ data: Appointment }>('/api/v1/appointments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Add all other endpoints...
}

export const apiClient = new ApiClient(API_BASE_URL);
```

**Replace Mock Data with Real API**:
```typescript
// frontend/src/app/patients/page.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';

export default function PatientsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Replace mock data with real API call
  const { data, isLoading, error } = useQuery({
    queryKey: ['patients', searchTerm, statusFilter],
    queryFn: () => apiClient.getPatients({
      search: searchTerm,
      status: statusFilter === 'all' ? undefined : statusFilter
    })
  });

  const patients = data?.data || [];

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    // Existing UI code...
    <PatientList patients={patients} />
  );
}
```

### Day 3: Basic Third-Party Integrations

**Email Service** (SendGrid):
```python
# backend/services/email/sendgrid_service.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@youreHR.com')

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None
    ):
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        if text_content:
            message.plain_text_content = text_content

        try:
            response = self.client.send(message)
            return {
                'success': True,
                'message_id': response.headers.get('X-Message-Id')
            }
        except Exception as e:
            logger.error(f"Email send failed: {str(e)}")
            return {'success': False, 'error': str(e)}
```

**File Storage** (AWS S3):
```python
# backend/services/storage/s3_service.py
import boto3
from botocore.exceptions import ClientError
import os

class S3StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.environ.get('S3_BUCKET_NAME')

    async def upload_file(
        self,
        file_content: bytes,
        file_key: str,
        content_type: str = 'application/octet-stream'
    ):
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                ServerSideEncryption='AES256'  # HIPAA requirement
            )
            return {
                'success': True,
                'key': file_key,
                'url': f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
            }
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def get_presigned_url(self, file_key: str, expiration: int = 3600):
        """Generate temporary download URL"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return {'success': True, 'url': url}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
```

---

## Phase 1: E-Prescribing Integration (Weeks 1-3)

### Week 1: Surescripts Setup & Drug Database

**Goal**: Set up Surescripts account and implement drug database

#### Step 1: Surescripts Account
```bash
# Apply at: https://surescripts.com/network-connections/
# Wait for approval (1-2 weeks)
# Get credentials:
# - Client ID
# - Client Secret
# - Endpoint URLs (test & production)
```

#### Step 2: Drug Database Schema
```sql
-- backend/alembic/versions/003_add_drug_database.sql

CREATE TABLE drugs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ndc VARCHAR(11) NOT NULL UNIQUE,  -- National Drug Code
    name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    brand_name VARCHAR(255),
    strength VARCHAR(100),
    dosage_form VARCHAR(100),  -- tablet, capsule, liquid, etc
    route VARCHAR(50),  -- oral, topical, injection
    dea_schedule VARCHAR(10),  -- I, II, III, IV, V (controlled substances)
    manufacturer VARCHAR(255),
    active_ingredients JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_drugs_ndc ON drugs(ndc);
CREATE INDEX idx_drugs_name ON drugs USING gin(to_tsvector('english', name));
CREATE INDEX idx_drugs_generic ON drugs USING gin(to_tsvector('english', generic_name));

CREATE TABLE drug_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drug_ndc_1 VARCHAR(11) NOT NULL,
    drug_ndc_2 VARCHAR(11) NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- severe, moderate, minor
    description TEXT,
    mechanism TEXT,
    management TEXT,
    FOREIGN KEY (drug_ndc_1) REFERENCES drugs(ndc),
    FOREIGN KEY (drug_ndc_2) REFERENCES drugs(ndc)
);

CREATE TABLE pharmacies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ncpdp_id VARCHAR(7) NOT NULL UNIQUE,  -- National Council for Prescription Drug Programs ID
    name VARCHAR(255) NOT NULL,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    phone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(255),
    is_24_hour BOOLEAN DEFAULT FALSE,
    accepts_eprescribe BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pharmacies_ncpdp ON pharmacies(ncpdp_id);
CREATE INDEX idx_pharmacies_zip ON pharmacies(zip_code);

CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    practice_id UUID NOT NULL,
    patient_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    pharmacy_ncpdp VARCHAR(7),
    drug_ndc VARCHAR(11) NOT NULL,
    drug_name VARCHAR(255) NOT NULL,
    strength VARCHAR(100),
    dosage_form VARCHAR(100),
    quantity DECIMAL(10,2) NOT NULL,
    days_supply INTEGER NOT NULL,
    refills INTEGER DEFAULT 0,
    sig TEXT NOT NULL,  -- Directions for use
    notes TEXT,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, sent, accepted, rejected, cancelled
    sent_at TIMESTAMP,
    accepted_at TIMESTAMP,
    rejected_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (practice_id) REFERENCES practices(id),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (provider_id) REFERENCES providers(id),
    FOREIGN KEY (pharmacy_ncpdp) REFERENCES pharmacies(ncpdp_id),
    FOREIGN KEY (drug_ndc) REFERENCES drugs(ndc)
);

CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_provider ON prescriptions(provider_id);
CREATE INDEX idx_prescriptions_status ON prescriptions(status);
```

#### Step 3: Drug Search Service
```python
# backend/services/eprescribing/drug_service.py
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

class DrugService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_drugs(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search drugs by name (brand or generic)
        Uses full-text search for performance
        """
        stmt = select(Drug).where(
            or_(
                Drug.name.ilike(f"%{query}%"),
                Drug.generic_name.ilike(f"%{query}%"),
                Drug.brand_name.ilike(f"%{query}%")
            )
        ).where(
            Drug.is_active == True
        ).limit(limit)

        result = await self.db.execute(stmt)
        drugs = result.scalars().all()

        return [
            {
                'ndc': drug.ndc,
                'name': drug.name,
                'generic_name': drug.generic_name,
                'brand_name': drug.brand_name,
                'strength': drug.strength,
                'dosage_form': drug.dosage_form,
                'route': drug.route,
                'dea_schedule': drug.dea_schedule
            }
            for drug in drugs
        ]

    async def get_drug_by_ndc(self, ndc: str) -> Optional[Drug]:
        """Get drug details by NDC"""
        stmt = select(Drug).where(Drug.ndc == ndc)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def check_interactions(
        self,
        drug_ndc: str,
        patient_medications: List[str]  # List of NDCs
    ) -> List[Dict]:
        """
        Check drug-drug interactions
        Returns list of interactions with severity
        """
        interactions = []

        for med_ndc in patient_medications:
            # Check both directions
            stmt = select(DrugInteraction).where(
                or_(
                    (DrugInteraction.drug_ndc_1 == drug_ndc) &
                    (DrugInteraction.drug_ndc_2 == med_ndc),
                    (DrugInteraction.drug_ndc_1 == med_ndc) &
                    (DrugInteraction.drug_ndc_2 == drug_ndc)
                )
            )

            result = await self.db.execute(stmt)
            interaction = result.scalar_one_or_none()

            if interaction:
                interactions.append({
                    'severity': interaction.severity,
                    'description': interaction.description,
                    'mechanism': interaction.mechanism,
                    'management': interaction.management,
                    'interacting_drug_ndc': med_ndc
                })

        return sorted(interactions, key=lambda x:
            {'severe': 0, 'moderate': 1, 'minor': 2}[x['severity']]
        )

    async def check_allergy_contraindications(
        self,
        drug_ndc: str,
        patient_allergies: List[str]  # List of allergen names
    ) -> List[Dict]:
        """Check if drug contains allergens"""
        drug = await self.get_drug_by_ndc(drug_ndc)
        if not drug:
            return []

        contraindications = []
        active_ingredients = drug.active_ingredients or {}

        for allergy in patient_allergies:
            # Check if allergy matches any ingredient
            for ingredient in active_ingredients.get('ingredients', []):
                if allergy.lower() in ingredient.lower():
                    contraindications.append({
                        'severity': 'severe',
                        'allergen': allergy,
                        'ingredient': ingredient,
                        'warning': f"Patient allergic to {allergy}"
                    })

        return contraindications
```

### Week 2: Surescripts API Integration

```python
# backend/services/eprescribing/surescripts_service.py
import httpx
from typing import Dict, Optional
import xml.etree.ElementTree as ET

class SurescriptsService:
    def __init__(self):
        self.base_url = os.environ.get('SURESCRIPTS_API_URL')
        self.client_id = os.environ.get('SURESCRIPTS_CLIENT_ID')
        self.client_secret = os.environ.get('SURESCRIPTS_CLIENT_SECRET')
        self.timeout = 30.0

    async def send_new_prescription(
        self,
        prescription: Dict,
        patient: Dict,
        provider: Dict,
        pharmacy: Dict
    ) -> Dict:
        """
        Send new prescription to pharmacy via Surescripts
        Uses NCPDP SCRIPT 10.6 format
        """
        # Build NCPDP SCRIPT XML message
        xml_message = self._build_newrx_message(
            prescription, patient, provider, pharmacy
        )

        # Send to Surescripts
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rxhub/transmit",
                content=xml_message,
                headers={
                    'Content-Type': 'application/xml',
                    'Authorization': f'Basic {self._get_auth_token()}'
                }
            )

        if response.status_code == 200:
            return {
                'success': True,
                'message_id': self._extract_message_id(response.text),
                'status': 'sent'
            }
        else:
            return {
                'success': False,
                'error': response.text,
                'status': 'failed'
            }

    def _build_newrx_message(
        self,
        prescription: Dict,
        patient: Dict,
        provider: Dict,
        pharmacy: Dict
    ) -> str:
        """Build NCPDP SCRIPT 10.6 NewRx message"""
        root = ET.Element('Message', {
            'xmlns': 'http://www.ncpdp.org/schema/SCRIPT',
            'version': '10.6'
        })

        # Header
        header = ET.SubElement(root, 'Header')
        ET.SubElement(header, 'To').text = pharmacy['ncpdp_id']
        ET.SubElement(header, 'From').text = provider['npi']
        ET.SubElement(header, 'MessageID').text = str(uuid.uuid4())
        ET.SubElement(header, 'SentTime').text = datetime.utcnow().isoformat()

        # Body - NewRx
        body = ET.SubElement(root, 'Body')
        newrx = ET.SubElement(body, 'NewRx')

        # Patient
        patient_elem = ET.SubElement(newrx, 'Patient')
        name = ET.SubElement(patient_elem, 'Name')
        ET.SubElement(name, 'FirstName').text = patient['first_name']
        ET.SubElement(name, 'LastName').text = patient['last_name']
        ET.SubElement(patient_elem, 'DateOfBirth').text = patient['date_of_birth']
        ET.SubElement(patient_elem, 'Gender').text = patient['sex']

        address = ET.SubElement(patient_elem, 'Address')
        ET.SubElement(address, 'AddressLine1').text = patient.get('address_line1', '')
        ET.SubElement(address, 'City').text = patient.get('city', '')
        ET.SubElement(address, 'State').text = patient.get('state', '')
        ET.SubElement(address, 'ZipCode').text = patient.get('zip_code', '')

        # Prescriber
        prescriber_elem = ET.SubElement(newrx, 'Prescriber')
        ET.SubElement(prescriber_elem, 'NPI').text = provider['npi']
        if provider.get('dea_number'):
            ET.SubElement(prescriber_elem, 'DEA').text = provider['dea_number']

        pres_name = ET.SubElement(prescriber_elem, 'Name')
        ET.SubElement(pres_name, 'FirstName').text = provider['first_name']
        ET.SubElement(pres_name, 'LastName').text = provider['last_name']

        # Medication
        med = ET.SubElement(newrx, 'MedicationPrescribed')
        ET.SubElement(med, 'DrugDescription').text = prescription['drug_name']
        ET.SubElement(med, 'DrugCoded', {'CodeType': 'NDC'}).text = prescription['drug_ndc']
        ET.SubElement(med, 'Quantity').text = str(prescription['quantity'])
        ET.SubElement(med, 'DaysSupply').text = str(prescription['days_supply'])
        ET.SubElement(med, 'Refills').text = str(prescription['refills'])
        ET.SubElement(med, 'Sig', {'SigText': prescription['sig']})

        # Pharmacy
        pharm_elem = ET.SubElement(newrx, 'Pharmacy')
        ET.SubElement(pharm_elem, 'NCPDPID').text = pharmacy['ncpdp_id']
        ET.SubElement(pharm_elem, 'StoreName').text = pharmacy['name']

        return ET.tostring(root, encoding='unicode')

    async def search_pharmacies(
        self,
        zip_code: str,
        radius_miles: int = 10
    ) -> List[Dict]:
        """Search for pharmacies near zip code"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/rxhub/pharmacy/search",
                params={
                    'zipCode': zip_code,
                    'radius': radius_miles
                },
                headers={'Authorization': f'Basic {self._get_auth_token()}'}
            )

        if response.status_code == 200:
            return self._parse_pharmacy_results(response.text)
        return []

    async def get_medication_history(
        self,
        patient_first_name: str,
        patient_last_name: str,
        date_of_birth: str,
        zip_code: str
    ) -> List[Dict]:
        """
        Get patient's medication history from pharmacy benefit managers
        """
        xml_request = self._build_medication_history_request(
            patient_first_name, patient_last_name, date_of_birth, zip_code
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rxhub/medicationhistory",
                content=xml_request,
                headers={
                    'Content-Type': 'application/xml',
                    'Authorization': f'Basic {self._get_auth_token()}'
                }
            )

        if response.status_code == 200:
            return self._parse_medication_history(response.text)
        return []
```

### Week 3: E-Prescribing UI

```typescript
// frontend/src/components/prescriptions/PrescriptionDialog.tsx
'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';

export function PrescriptionDialog({
  patientId,
  onClose
}: {
  patientId: string;
  onClose: () => void;
}) {
  const [step, setStep] = useState<'search' | 'details' | 'pharmacy' | 'review'>('search');
  const [drugSearch, setDrugSearch] = useState('');
  const [selectedDrug, setSelectedDrug] = useState<Drug | null>(null);
  const [prescriptionDetails, setPrescriptionDetails] = useState({
    quantity: '',
    days_supply: '',
    refills: 0,
    sig: ''
  });
  const [selectedPharmacy, setSelectedPharmacy] = useState<Pharmacy | null>(null);

  // Search drugs
  const { data: drugs, isLoading: searchingDrugs } = useQuery({
    queryKey: ['drugs', drugSearch],
    queryFn: () => apiClient.searchDrugs(drugSearch),
    enabled: drugSearch.length > 2
  });

  // Check interactions
  const { data: interactions } = useQuery({
    queryKey: ['interactions', selectedDrug?.ndc, patientId],
    queryFn: () => apiClient.checkDrugInteractions(selectedDrug!.ndc, patientId),
    enabled: !!selectedDrug
  });

  // Search pharmacies
  const { data: pharmacies } = useQuery({
    queryKey: ['pharmacies', patientId],
    queryFn: async () => {
      const patient = await apiClient.getPatient(patientId);
      return apiClient.searchPharmacies(patient.data.zip_code);
    }
  });

  // Send prescription
  const sendPrescription = useMutation({
    mutationFn: (data: CreatePrescriptionRequest) =>
      apiClient.createPrescription(data),
    onSuccess: () => {
      toast.success('Prescription sent successfully');
      onClose();
    },
    onError: (error) => {
      toast.error(`Failed to send prescription: ${error.message}`);
    }
  });

  const handleSend = () => {
    if (!selectedDrug || !selectedPharmacy) return;

    sendPrescription.mutate({
      patient_id: patientId,
      drug_ndc: selectedDrug.ndc,
      drug_name: selectedDrug.name,
      quantity: parseFloat(prescriptionDetails.quantity),
      days_supply: parseInt(prescriptionDetails.days_supply),
      refills: prescriptionDetails.refills,
      sig: prescriptionDetails.sig,
      pharmacy_ncpdp: selectedPharmacy.ncpdp_id
    });
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>New Prescription</DialogTitle>
        </DialogHeader>

        {/* Step 1: Search Drug */}
        {step === 'search' && (
          <div className="space-y-4">
            <Input
              placeholder="Search medication..."
              value={drugSearch}
              onChange={(e) => setDrugSearch(e.target.value)}
            />

            {searchingDrugs && <LoadingSpinner />}

            {drugs && (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {drugs.data.map((drug: Drug) => (
                  <button
                    key={drug.ndc}
                    onClick={() => {
                      setSelectedDrug(drug);
                      setStep('details');
                    }}
                    className="w-full p-4 text-left border rounded hover:bg-gray-50"
                  >
                    <div className="font-medium">{drug.name}</div>
                    <div className="text-sm text-gray-600">
                      {drug.strength} {drug.dosage_form}
                    </div>
                    {drug.dea_schedule && (
                      <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                        Schedule {drug.dea_schedule}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Prescription Details */}
        {step === 'details' && selectedDrug && (
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded">
              <div className="font-medium">{selectedDrug.name}</div>
              <div className="text-sm text-gray-600">
                {selectedDrug.strength} {selectedDrug.dosage_form}
              </div>
            </div>

            {/* Interaction Warnings */}
            {interactions?.data && interactions.data.length > 0 && (
              <Alert variant="destructive">
                <AlertTitle>Drug Interactions Detected</AlertTitle>
                <AlertDescription>
                  {interactions.data.map((int: any) => (
                    <div key={int.interacting_drug_ndc} className="mt-2">
                      <strong className="capitalize">{int.severity}:</strong> {int.description}
                      {int.management && (
                        <div className="text-sm mt-1">Management: {int.management}</div>
                      )}
                    </div>
                  ))}
                </AlertDescription>
              </Alert>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Quantity</Label>
                <Input
                  type="number"
                  value={prescriptionDetails.quantity}
                  onChange={(e) => setPrescriptionDetails({
                    ...prescriptionDetails,
                    quantity: e.target.value
                  })}
                />
              </div>

              <div>
                <Label>Days Supply</Label>
                <Input
                  type="number"
                  value={prescriptionDetails.days_supply}
                  onChange={(e) => setPrescriptionDetails({
                    ...prescriptionDetails,
                    days_supply: e.target.value
                  })}
                />
              </div>
            </div>

            <div>
              <Label>Refills</Label>
              <Select
                value={prescriptionDetails.refills.toString()}
                onValueChange={(val) => setPrescriptionDetails({
                  ...prescriptionDetails,
                  refills: parseInt(val)
                })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[0, 1, 2, 3, 4, 5, 6, 11].map(num => (
                    <SelectItem key={num} value={num.toString()}>
                      {num === 11 ? 'PRN' : num}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Directions (Sig)</Label>
              <Textarea
                placeholder="Take 1 tablet by mouth twice daily"
                value={prescriptionDetails.sig}
                onChange={(e) => setPrescriptionDetails({
                  ...prescriptionDetails,
                  sig: e.target.value
                })}
                rows={3}
              />
            </div>

            <Button onClick={() => setStep('pharmacy')} className="w-full">
              Continue to Pharmacy Selection
            </Button>
          </div>
        )}

        {/* Step 3: Select Pharmacy */}
        {step === 'pharmacy' && (
          <div className="space-y-4">
            <h3 className="font-medium">Select Pharmacy</h3>

            {pharmacies?.data.map((pharmacy: Pharmacy) => (
              <button
                key={pharmacy.ncpdp_id}
                onClick={() => {
                  setSelectedPharmacy(pharmacy);
                  setStep('review');
                }}
                className="w-full p-4 text-left border rounded hover:bg-gray-50"
              >
                <div className="font-medium">{pharmacy.name}</div>
                <div className="text-sm text-gray-600">
                  {pharmacy.address_line1}, {pharmacy.city}, {pharmacy.state}
                </div>
                <div className="text-sm text-gray-500">{pharmacy.phone}</div>
                {pharmacy.is_24_hour && (
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                    24 Hour
                  </span>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Step 4: Review & Send */}
        {step === 'review' && (
          <div className="space-y-4">
            <h3 className="font-medium">Review Prescription</h3>

            <div className="p-4 border rounded space-y-2">
              <div>
                <strong>Medication:</strong> {selectedDrug?.name}
              </div>
              <div>
                <strong>Quantity:</strong> {prescriptionDetails.quantity}
              </div>
              <div>
                <strong>Days Supply:</strong> {prescriptionDetails.days_supply}
              </div>
              <div>
                <strong>Refills:</strong> {prescriptionDetails.refills}
              </div>
              <div>
                <strong>Directions:</strong> {prescriptionDetails.sig}
              </div>
              <div>
                <strong>Pharmacy:</strong> {selectedPharmacy?.name}
              </div>
            </div>

            <Button
              onClick={handleSend}
              disabled={sendPrescription.isPending}
              className="w-full"
            >
              {sendPrescription.isPending ? 'Sending...' : 'Send Prescription'}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
```

---

## Phase 2: Patient Portal (Weeks 4-6)

### Architecture

**Separate Next.js App** for patient portal:
```
health-ai-platform/
├── frontend/          # Provider portal (existing)
├── patient-portal/    # NEW - Patient-facing portal
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── auth/
│   │   │   │   ├── login/
│   │   │   │   ├── register/
│   │   │   │   └── forgot-password/
│   │   │   ├── dashboard/
│   │   │   ├── appointments/
│   │   │   ├── records/
│   │   │   ├── messages/
│   │   │   └── billing/
│   │   ├── components/
│   │   └── lib/
│   └── package.json
└── backend/
    └── api/
        └── v1/
            └── patient_portal/    # NEW endpoints
```

### Week 4: Patient Authentication & Backend

```python
# backend/models/patient_user.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

class PatientUser(Base):
    """
    Separate user model for patients accessing portal
    Links to existing Patient records
    """
    __tablename__ = 'patient_users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False, unique=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Security
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)

    # Tracking
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    patient = relationship('Patient', back_populates='portal_user')
```

```python
# backend/services/patient_portal/auth_service.py
import bcrypt
import jwt
from datetime import datetime, timedelta
import secrets

class PatientAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_patient(
        self,
        patient_id: str,
        email: str,
        password: str
    ) -> Dict:
        """
        Register existing patient for portal access
        Requires patient to exist in system
        """
        # Verify patient exists
        patient = await patient_service.get_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Check if already registered
        existing = await self.db.execute(
            select(PatientUser).where(PatientUser.patient_id == patient_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Patient already registered")

        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Generate email verification token
        verification_token = secrets.token_urlsafe(32)

        # Create patient user
        patient_user = PatientUser(
            patient_id=patient_id,
            email=email,
            password_hash=password_hash.decode(),
            email_verification_token=verification_token
        )

        self.db.add(patient_user)
        await self.db.commit()

        # Send verification email
        await email_service.send_email(
            to_email=email,
            subject="Verify Your Email",
            html_content=f"""
                <p>Click the link below to verify your email:</p>
                <a href="{PORTAL_URL}/auth/verify?token={verification_token}">
                    Verify Email
                </a>
            """
        )

        return {'success': True, 'message': 'Verification email sent'}

    async def login(self, email: str, password: str) -> Dict:
        """Authenticate patient and return JWT"""
        # Get patient user
        result = await self.db.execute(
            select(PatientUser).where(PatientUser.email == email)
        )
        patient_user = result.scalar_one_or_none()

        if not patient_user:
            raise ValueError("Invalid credentials")

        # Check if locked
        if patient_user.locked_until and patient_user.locked_until > datetime.utcnow():
            raise ValueError("Account temporarily locked")

        # Verify password
        if not bcrypt.checkpw(password.encode(), patient_user.password_hash.encode()):
            # Increment failed attempts
            patient_user.failed_login_attempts += 1
            if patient_user.failed_login_attempts >= 5:
                patient_user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            await self.db.commit()
            raise ValueError("Invalid credentials")

        # Check email verified
        if not patient_user.email_verified:
            raise ValueError("Please verify your email first")

        # Reset failed attempts
        patient_user.failed_login_attempts = 0
        patient_user.last_login = datetime.utcnow()
        await self.db.commit()

        # Generate JWT
        token_payload = {
            'patient_user_id': str(patient_user.id),
            'patient_id': str(patient_user.patient_id),
            'email': patient_user.email,
            'type': 'patient_portal',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }

        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')

        return {
            'token': token,
            'patient_id': str(patient_user.patient_id)
        }
```

### Week 5: Appointment Booking

```python
# backend/api/v1/patient_portal/appointments.py
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter(prefix="/patient-portal/appointments", tags=["Patient Portal - Appointments"])

@router.get("/available-slots")
async def get_available_slots(
    provider_id: Optional[str] = None,
    date: str = None,  # YYYY-MM-DD
    current_patient = Depends(get_current_patient_user)
):
    """
    Get available appointment slots
    Patients can only see available (not booked) slots
    """
    # Parse date
    target_date = datetime.strptime(date, '%Y-%m-%d') if date else datetime.now()

    # Get provider schedules
    if provider_id:
        schedules = await provider_schedule_service.get_provider_schedule(
            provider_id, target_date
        )
    else:
        # All providers
        schedules = await provider_schedule_service.get_all_schedules(target_date)

    # Get existing appointments
    existing_appointments = await appointment_service.get_appointments_by_date(
        target_date
    )

    # Calculate available slots
    available_slots = []
    for schedule in schedules:
        # Generate 15-minute slots
        start_time = schedule.start_time
        end_time = schedule.end_time

        current_time = start_time
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=15)

            # Check if slot is booked
            is_booked = any(
                apt.start_time <= current_time < apt.end_time
                for apt in existing_appointments
                if apt.provider_id == schedule.provider_id
            )

            if not is_booked:
                available_slots.append({
                    'provider_id': schedule.provider_id,
                    'provider_name': schedule.provider.full_name,
                    'date': target_date.strftime('%Y-%m-%d'),
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M'),
                    'duration': 15
                })

            current_time = slot_end

    return {'data': available_slots}

@router.post("")
async def book_appointment(
    request: PatientAppointmentRequest,
    current_patient = Depends(get_current_patient_user)
):
    """
    Book appointment for patient
    """
    # Verify slot still available
    slot_available = await appointment_service.check_slot_available(
        provider_id=request.provider_id,
        start_time=request.start_time,
        duration=request.duration
    )

    if not slot_available:
        raise HTTPException(400, "Slot no longer available")

    # Create appointment
    appointment = await appointment_service.create_appointment({
        'practice_id': current_patient.patient.practice_id,
        'patient_id': current_patient.patient_id,
        'provider_id': request.provider_id,
        'appointment_date': request.date,
        'start_time': request.start_time,
        'end_time': request.end_time,
        'appointment_type': request.appointment_type,
        'reason': request.reason,
        'status': 'scheduled'
    })

    # Send confirmation email
    await email_service.send_appointment_confirmation(
        current_patient.email,
        appointment
    )

    return {'data': appointment, 'message': 'Appointment booked successfully'}

@router.get("/my-appointments")
async def get_my_appointments(
    current_patient = Depends(get_current_patient_user)
):
    """Get patient's appointments"""
    appointments = await appointment_service.get_patient_appointments(
        current_patient.patient_id
    )

    return {'data': appointments}

@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: str,
    current_patient = Depends(get_current_patient_user)
):
    """Cancel appointment"""
    appointment = await appointment_service.get_by_id(appointment_id)

    # Verify belongs to patient
    if appointment.patient_id != current_patient.patient_id:
        raise HTTPException(403, "Not authorized")

    # Cancel
    await appointment_service.update_appointment(
        appointment_id,
        {'status': 'cancelled', 'cancelled_by': 'patient'}
    )

    return {'message': 'Appointment cancelled'}
```

### Week 6: Patient Portal Frontend

```typescript
// patient-portal/src/app/appointments/book/page.tsx
'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Calendar } from '@/components/ui/calendar';
import { Button } from '@/components/ui/button';

export default function BookAppointmentPage() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<any>(null);

  // Get available slots
  const { data: slots, isLoading } = useQuery({
    queryKey: ['available-slots', selectedDate, selectedProvider],
    queryFn: () => patientPortalApi.getAvailableSlots({
      date: selectedDate.toISOString().split('T')[0],
      provider_id: selectedProvider
    })
  });

  // Book appointment
  const bookAppointment = useMutation({
    mutationFn: (data) => patientPortalApi.bookAppointment(data),
    onSuccess: () => {
      toast.success('Appointment booked!');
      router.push('/appointments');
    }
  });

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Book Appointment</h1>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Calendar */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Select Date</h2>
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={setSelectedDate}
            disabled={(date) => date < new Date()}
            className="border rounded-lg"
          />
        </div>

        {/* Available Slots */}
        <div>
          <h2 className="text-xl font-semibold mb-4">
            Available Times - {selectedDate.toLocaleDateString()}
          </h2>

          {isLoading && <LoadingSpinner />}

          {slots?.data && (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {slots.data.map((slot: any) => (
                <button
                  key={`${slot.provider_id}-${slot.start_time}`}
                  onClick={() => setSelectedSlot(slot)}
                  className={`w-full p-4 text-left border rounded hover:bg-blue-50 ${
                    selectedSlot === slot ? 'bg-blue-100 border-blue-500' : ''
                  }`}
                >
                  <div className="font-medium">{slot.start_time}</div>
                  <div className="text-sm text-gray-600">
                    with {slot.provider_name}
                  </div>
                </button>
              ))}
            </div>
          )}

          {selectedSlot && (
            <div className="mt-6 p-4 border rounded">
              <h3 className="font-medium mb-4">Appointment Details</h3>

              <div className="space-y-2 mb-4">
                <div>
                  <strong>Date:</strong> {selectedDate.toLocaleDateString()}
                </div>
                <div>
                  <strong>Time:</strong> {selectedSlot.start_time}
                </div>
                <div>
                  <strong>Provider:</strong> {selectedSlot.provider_name}
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label>Reason for Visit</Label>
                  <Textarea
                    placeholder="Brief description of your concern..."
                    rows={3}
                  />
                </div>

                <Button
                  onClick={() => bookAppointment.mutate({
                    provider_id: selectedSlot.provider_id,
                    date: selectedDate.toISOString().split('T')[0],
                    start_time: selectedSlot.start_time,
                    appointment_type: 'office_visit',
                    reason: 'Patient entered reason'
                  })}
                  className="w-full"
                >
                  Confirm Booking
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## Phase 3: Infrastructure Setup (Week 7)

### Monitoring with Datadog

```python
# backend/main.py
from ddtrace import tracer, patch_all
from ddtrace.contrib.fastapi import patch as fastapi_patch

# Enable automatic instrumentation
patch_all()
fastapi_patch()

app = FastAPI()

# Add custom metrics
from datadog import statsd

@app.middleware("http")
async def track_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    # Track metrics
    statsd.increment('api.requests',
        tags=[f'endpoint:{request.url.path}', f'status:{response.status_code}']
    )
    statsd.histogram('api.response_time', duration,
        tags=[f'endpoint:{request.url.path}']
    )

    return response
```

### Production Environment Variables

```bash
# .env.production

# Database
DATABASE_URL=postgresql://user:pass@prod-db.rds.amazonaws.com:5432/healthai

# Redis
REDIS_URL=redis://prod-redis.cache.amazonaws.com:6379

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=healthai-prod-documents

# Email
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=noreply@youreHR.com

# SMS
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+15551234567

# E-Prescribing
SURESCRIPTS_API_URL=https://api.surescripts.com
SURESCRIPTS_CLIENT_ID=your_client_id
SURESCRIPTS_CLIENT_SECRET=your_client_secret

# Monitoring
DATADOG_API_KEY=your_datadog_key
SENTRY_DSN=your_sentry_dsn

# Security
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_fernet_key
```

---

This is the comprehensive plan. Should I now start implementing Phase 0 (Critical Fixes)?
