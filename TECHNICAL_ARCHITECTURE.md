# Health AI Platform - Technical Architecture

## Architecture Overview

The Health AI Platform follows a **microservices-oriented architecture** with AI/ML capabilities as first-class citizens, designed for healthcare-grade reliability, security, and compliance.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         External Systems                            │
│  ┌────────┐  ┌─────────┐  ┌────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Payers │  │  Labs   │  │  HIE   │  │ Pharmacy │  │   EHR    │  │
│  └────┬───┘  └────┬────┘  └───┬────┘  └────┬─────┘  └────┬─────┘  │
└───────┼───────────┼───────────┼────────────┼─────────────┼─────────┘
        │           │           │            │             │
        └───────────┴───────────┴────────────┴─────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   API Gateway        │
                    │   (Kong/AWS ALB)     │
                    │   - Rate Limiting    │
                    │   - Authentication   │
                    │   - Request Routing  │
                    └───────────┬──────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐  ┌──────────▼────────┐  ┌──────────▼─────────┐
│   Web Client   │  │   Mobile App      │  │   FHIR API         │
│   (Next.js)    │  │   (React Native)  │  │   (HL7 FHIR R4)    │
│   - Patient    │  │   - iOS/Android   │  │   - REST API       │
│   - Provider   │  │   - Wearables     │  │   - SMART Auth     │
│   - Admin      │  │   - Telehealth    │  │   - CDS Hooks      │
└────────────────┘  └───────────────────┘  └────────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │  Application Layer   │
                    └──────────────────────┘
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐  ┌──────────▼────────┐  ┌──────────▼─────────┐
│   Core API     │  │   AI Services     │  │   Integration      │
│   (FastAPI)    │  │   (Python)        │  │   Services         │
│                │  │                   │  │                    │
│ ┌────────────┐ │  │ ┌───────────────┐ │  │ ┌────────────────┐ │
│ │ Patient    │ │  │ │ Claude LLM    │ │  │ │ FHIR Gateway   │ │
│ │ Management │ │  │ │ Integration   │ │  │ │ HL7 v2 Adapter │ │
│ └────────────┘ │  │ └───────────────┘ │  │ └────────────────┘ │
│ ┌────────────┐ │  │ ┌───────────────┐ │  │ ┌────────────────┐ │
│ │ Scheduling │ │  │ │ Clinical NLP  │ │  │ │ Payer APIs     │ │
│ └────────────┘ │  │ └───────────────┘ │  │ └────────────────┘ │
│ ┌────────────┐ │  │ ┌───────────────┐ │  │ ┌────────────────┐ │
│ │ Billing    │ │  │ │ Predictive    │ │  │ │ Lab/Pharmacy   │ │
│ │ & Claims   │ │  │ │ Analytics     │ │  │ │ Integrations   │ │
│ └────────────┘ │  │ └───────────────┘ │  │ └────────────────┘ │
│ ┌────────────┐ │  │ ┌───────────────┐ │  │ ┌────────────────┐ │
│ │ Clinical   │ │  │ │ Medical       │ │  │ │ Telehealth     │ │
│ │ Documentation │ │ │ Imaging AI    │ │  │ │ (WebRTC)       │ │
│ └────────────┘ │  │ └───────────────┘ │  │ └────────────────┘ │
└────────────────┘  └───────────────────┘  └────────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   Message Queue      │
                    │   (RabbitMQ/Kafka)   │
                    │   - Async Processing │
                    │   - Event Streaming  │
                    └──────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐  ┌──────────▼────────┐  ┌──────────▼─────────┐
│   Worker Pool  │  │   Background Jobs │  │   Scheduled Tasks  │
│   (Celery)     │  │                   │  │   (Cron/Airflow)   │
│                │  │ - Report Gen      │  │                    │
│ - AI Inference │  │ - Email Sending   │  │ - Data Backups     │
│ - Image Proc   │  │ - File Processing │  │ - Model Retraining │
│ - ML Training  │  │ - Notifications   │  │ - Cache Warming    │
└────────────────┘  └───────────────────┘  └────────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   Data Layer         │
                    └──────────────────────┘
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐  ┌──────────▼────────┐  ┌──────────▼─────────┐
│  PostgreSQL    │  │   Redis            │  │   S3/Object        │
│  (Primary DB)  │  │   (Cache/Session)  │  │   Storage          │
│                │  │                    │  │                    │
│ - Patient Data │  │ - User Sessions    │  │ - Medical Images   │
│ - Medical Rec  │  │ - API Cache        │  │ - Documents        │
│ - Billing      │  │ - Pub/Sub          │  │ - Backups          │
│ - Analytics    │  │ - Rate Limiting    │  │ - DICOM Files      │
└────────────────┘  └────────────────────┘  └────────────────────┘
        │                       │                       │
┌───────▼────────┐  ┌──────────▼────────┐  ┌──────────▼─────────┐
│  Vector DB     │  │   Time Series DB   │  │   Data Warehouse   │
│  (Pinecone)    │  │   (TimescaleDB)    │  │   (Snowflake)      │
│                │  │                    │  │                    │
│ - Embeddings   │  │ - Vital Signs      │  │ - Analytics        │
│ - Semantic     │  │ - Wearable Data    │  │ - Reporting        │
│   Search       │  │ - Metrics          │  │ - BI Tools         │
└────────────────┘  └────────────────────┘  └────────────────────┘

        ┌────────────────────────────────────────────────┐
        │         Monitoring & Observability             │
        │  ┌──────────┐  ┌─────────┐  ┌──────────────┐  │
        │  │ Datadog  │  │ Sentry  │  │ Prometheus + │  │
        │  │   APM    │  │  Errors │  │   Grafana    │  │
        │  └──────────┘  └─────────┘  └──────────────┘  │
        └────────────────────────────────────────────────┘

        ┌────────────────────────────────────────────────┐
        │         Security & Compliance Layer            │
        │  ┌──────────┐  ┌─────────┐  ┌──────────────┐  │
        │  │   WAF    │  │ Vault   │  │  Audit Log   │  │
        │  │ (AWS/CF) │  │ Secrets │  │   Service    │  │
        │  └──────────┘  └─────────┘  └──────────────┘  │
        └────────────────────────────────────────────────┘
```

---

## Component Details

### 1. API Gateway Layer

**Technology**: Kong API Gateway or AWS Application Load Balancer + API Gateway

**Responsibilities**:
- Request routing and load balancing
- Rate limiting and throttling (1000 req/min per user)
- SSL/TLS termination
- JWT validation and OAuth 2.0 authentication
- Request/response transformation
- API versioning (v1, v2 paths)
- CORS handling
- DDoS protection

**Configuration**:
```yaml
rate_limiting:
  - endpoint: /api/v1/ai/*
    limit: 100 requests/minute
  - endpoint: /api/v1/fhir/*
    limit: 1000 requests/minute
  - endpoint: /api/v1/public/*
    limit: 20 requests/minute

authentication:
  - path: /api/v1/patient/*
    require: JWT + patient_role
  - path: /api/v1/provider/*
    require: JWT + provider_role
  - path: /api/v1/admin/*
    require: JWT + admin_role + MFA
```

---

### 2. Frontend Applications

#### 2.1 Web Application (Next.js 16 + React 19)

**Features**:
- Server-Side Rendering (SSR) for SEO and performance
- Static Site Generation (SSG) for marketing pages
- Incremental Static Regeneration (ISR) for dynamic content
- React Server Components for reduced bundle size
- Progressive Web App (PWA) capabilities

**Key Libraries**:
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "typescript": "^5.3.0",
    "zustand": "^4.5.0",
    "@tanstack/react-query": "^5.17.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "^1.0.0",
    "recharts": "^2.10.0",
    "fullcalendar": "^6.1.0",
    "socket.io-client": "^4.6.0",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.0"
  }
}
```

**Architecture Patterns**:
- Atomic Design for component structure
- Feature-based folder organization
- Custom hooks for business logic
- React Query for server state management
- Zustand for client state management
- Code splitting with dynamic imports

**Performance Optimizations**:
- Image optimization with Next.js Image
- Font optimization with next/font
- Bundle size < 200KB initial load
- Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1

#### 2.2 Mobile Application (React Native)

**Features**:
- Native performance on iOS and Android
- Offline-first architecture with local SQLite
- Push notifications (FCM/APNS)
- Biometric authentication
- Camera integration for document scanning
- HealthKit/Google Fit integration

**Tech Stack**:
```json
{
  "dependencies": {
    "react-native": "^0.73.0",
    "expo": "^50.0.0",
    "@react-navigation/native": "^6.1.0",
    "react-native-health": "^1.20.0",
    "react-native-camera": "^4.2.0",
    "@react-native-firebase/messaging": "^18.6.0",
    "realm": "^12.5.0"
  }
}
```

---

### 3. Core API Services (FastAPI)

#### 3.1 Service Architecture

**Pattern**: Domain-Driven Design (DDD) with layered architecture

```
backend/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── patients.py       # Patient CRUD
│   │   │   ├── appointments.py   # Scheduling
│   │   │   ├── billing.py        # Claims & payments
│   │   │   ├── clinical.py       # Medical records
│   │   │   └── ai.py             # AI endpoints
│   │   └── dependencies.py       # Shared dependencies
│   └── v2/                       # Future API version
├── core/
│   ├── config.py                 # Configuration
│   ├── security.py               # Auth/encryption
│   ├── database.py               # DB connection
│   └── exceptions.py             # Custom exceptions
├── models/
│   ├── patient.py                # SQLAlchemy models
│   ├── appointment.py
│   └── ...
├── schemas/
│   ├── patient.py                # Pydantic schemas
│   └── ...
├── services/
│   ├── patient_service.py        # Business logic
│   ├── ai_service.py
│   └── ...
├── repositories/
│   ├── patient_repository.py     # Data access layer
│   └── ...
├── integrations/
│   ├── anthropic_client.py       # Claude API
│   ├── fhir_client.py
│   └── payer_api_client.py
└── utils/
    ├── encryption.py
    ├── audit_logger.py
    └── validators.py
```

#### 3.2 API Standards

**RESTful Design**:
```
GET    /api/v1/patients                 # List patients
POST   /api/v1/patients                 # Create patient
GET    /api/v1/patients/{id}            # Get patient
PUT    /api/v1/patients/{id}            # Update patient
DELETE /api/v1/patients/{id}            # Delete patient (soft)

GET    /api/v1/patients/{id}/appointments
POST   /api/v1/patients/{id}/appointments
```

**Response Format**:
```json
{
  "success": true,
  "data": {
    "id": "pat_123",
    "first_name": "John",
    "last_name": "Doe"
  },
  "meta": {
    "timestamp": "2025-11-13T10:30:00Z",
    "request_id": "req_xyz789"
  }
}
```

**Error Format**:
```json
{
  "success": false,
  "error": {
    "code": "PATIENT_NOT_FOUND",
    "message": "Patient with ID pat_123 not found",
    "details": {},
    "request_id": "req_xyz789"
  }
}
```

#### 3.3 Database Design

**PostgreSQL Schema** (16+ with pg_vector extension):

```sql
-- Core tables already implemented
CREATE TABLE practices (...);
CREATE TABLE providers (...);
CREATE TABLE patients (...);
CREATE TABLE appointments (...);
CREATE TABLE medical_records (...);
CREATE TABLE prescriptions (...);
CREATE TABLE billing_claims (...);
CREATE TABLE insurance_policies (...);

-- New AI-related tables
CREATE TABLE ai_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    patient_id UUID,
    interaction_type VARCHAR(50),  -- 'diagnosis_support', 'note_summary', etc.
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    model_version VARCHAR(50),
    tokens_used INTEGER,
    confidence_score FLOAT,
    reviewed_by UUID,              -- Provider who reviewed AI output
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE ai_model_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    deployed_at TIMESTAMP,
    performance_metrics JSONB,     -- Accuracy, precision, recall
    training_data_info JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE clinical_decision_support_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    decision_type VARCHAR(50),     -- 'diagnosis', 'treatment', 'medication'
    input_data JSONB,
    recommendations JSONB,
    provider_action VARCHAR(50),   -- 'accepted', 'rejected', 'modified'
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);

CREATE TABLE patient_risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    risk_type VARCHAR(50),         -- 'readmission', 'mortality', 'no_show'
    risk_score FLOAT CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_category VARCHAR(20),     -- 'low', 'medium', 'high', 'critical'
    contributing_factors JSONB,
    calculated_at TIMESTAMP DEFAULT NOW(),
    valid_until TIMESTAMP,
    model_version VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50),       -- 'patient', 'note', 'medication'
    entity_id UUID NOT NULL,
    embedding vector(1536),        -- For OpenAI embeddings
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings_vector ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- HIPAA audit table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,   -- 'create', 'read', 'update', 'delete'
    entity_type VARCHAR(50),
    entity_id UUID,
    ip_address INET,
    user_agent TEXT,
    changes JSONB,                 -- Before/after for updates
    phi_accessed BOOLEAN,          -- Flag for PHI access
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Partition audit_logs by month for performance
CREATE TABLE audit_logs_2025_11 PARTITION OF audit_logs
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

**Indexes for Performance**:
```sql
-- Existing essential indexes
CREATE INDEX idx_patients_mrn ON patients(medical_record_number);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_claims_status ON billing_claims(claim_status);

-- New AI-specific indexes
CREATE INDEX idx_ai_interactions_patient ON ai_interactions(patient_id);
CREATE INDEX idx_ai_interactions_type ON ai_interactions(interaction_type);
CREATE INDEX idx_risk_scores_patient ON patient_risk_scores(patient_id);
CREATE INDEX idx_risk_scores_type ON patient_risk_scores(risk_type, calculated_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
```

---

### 4. AI Services Architecture

#### 4.1 Claude LLM Integration Service

**Architecture**:
```python
# services/ai/claude_service.py
from anthropic import Anthropic
from typing import Optional, Dict, Any
import redis
from functools import lru_cache

class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.redis_client = redis.Redis(host=settings.REDIS_HOST)
        self.cache_ttl = 3600  # 1 hour cache

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        model: str = "claude-3-7-sonnet-20250219",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Claude API with caching
        """
        cache_key = self._generate_cache_key(messages, model)

        if use_cache:
            cached_response = self.redis_client.get(cache_key)
            if cached_response:
                return json.loads(cached_response)

        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages
        )

        result = {
            "content": response.content[0].text,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "stop_reason": response.stop_reason
        }

        if use_cache:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result)
            )

        # Log usage for cost tracking
        await self._log_usage(result["usage"])

        return result

    async def clinical_note_summary(
        self,
        note_text: str,
        patient_context: Optional[Dict] = None
    ) -> str:
        """
        Summarize clinical note using Claude
        """
        system_prompt = """You are a medical assistant helping physicians
        summarize clinical notes. Extract key information including:
        - Chief complaint
        - History of present illness
        - Assessment
        - Plan
        Maintain clinical accuracy and use proper medical terminology."""

        context = ""
        if patient_context:
            context = f"""
            Patient Age: {patient_context.get('age')}
            Sex: {patient_context.get('sex')}
            Known Conditions: {', '.join(patient_context.get('conditions', []))}
            """

        messages = [
            {
                "role": "user",
                "content": f"{context}\n\nClinical Note:\n{note_text}\n\nPlease provide a concise summary."
            }
        ]

        response = await self.chat_completion(
            messages=messages,
            system=system_prompt,
            temperature=0.3  # Lower temperature for medical accuracy
        )

        return response["content"]

    async def differential_diagnosis(
        self,
        symptoms: list[str],
        patient_history: Dict,
        vital_signs: Dict
    ) -> Dict[str, Any]:
        """
        Generate differential diagnosis suggestions
        """
        system_prompt = """You are a clinical decision support system.
        Provide differential diagnosis suggestions based on symptoms and patient data.
        IMPORTANT: Always include confidence levels and recommend confirmatory tests.
        This is for physician review only - not definitive diagnosis."""

        user_message = f"""
        Symptoms: {', '.join(symptoms)}

        Patient History:
        - Age: {patient_history.get('age')}
        - Sex: {patient_history.get('sex')}
        - Past Medical History: {', '.join(patient_history.get('pmh', []))}
        - Medications: {', '.join(patient_history.get('medications', []))}
        - Allergies: {', '.join(patient_history.get('allergies', []))}

        Vital Signs:
        - BP: {vital_signs.get('blood_pressure')}
        - HR: {vital_signs.get('heart_rate')}
        - Temp: {vital_signs.get('temperature')}
        - SpO2: {vital_signs.get('oxygen_saturation')}

        Please provide:
        1. Top 5 differential diagnoses with probability
        2. Recommended diagnostic tests
        3. Red flags to watch for
        4. Initial management suggestions
        """

        response = await self.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            model="claude-3-7-sonnet-20250219",  # Use most capable model
            temperature=0.2
        )

        # Parse structured output
        return self._parse_ddx_response(response["content"])

    async def coding_assistant(
        self,
        clinical_note: str,
        encounter_type: str
    ) -> Dict[str, Any]:
        """
        Suggest ICD-10 and CPT codes from clinical documentation
        """
        system_prompt = """You are a medical coding specialist.
        Analyze clinical notes and suggest appropriate ICD-10-CM and CPT codes.
        Provide justification for each code."""

        user_message = f"""
        Encounter Type: {encounter_type}

        Clinical Note:
        {clinical_note}

        Please suggest:
        1. ICD-10-CM diagnosis codes (with descriptions)
        2. CPT procedure codes (with modifiers if applicable)
        3. Level of service (E/M code) with MDM justification
        """

        response = await self.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            temperature=0.1  # Very low for coding accuracy
        )

        return self._parse_coding_response(response["content"])
```

#### 4.2 Predictive Analytics Service

**Architecture**:
```python
# services/ml/predictive_service.py
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
import shap

class PredictiveAnalyticsService:
    def __init__(self):
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Load pre-trained models"""
        self.models['readmission'] = joblib.load('models/readmission_rf_v1.pkl')
        self.models['no_show'] = joblib.load('models/no_show_xgb_v1.pkl')
        self.models['chf_progression'] = joblib.load('models/chf_gbm_v1.pkl')

    async def predict_readmission_risk(
        self,
        patient_id: str,
        admission_data: Dict
    ) -> Dict[str, Any]:
        """
        Predict 30-day readmission risk
        """
        # Feature engineering
        features = self._extract_readmission_features(admission_data)
        feature_df = pd.DataFrame([features])

        model = self.models['readmission']

        # Prediction
        risk_probability = model.predict_proba(feature_df)[0][1]
        risk_category = self._categorize_risk(risk_probability)

        # Explainability with SHAP
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(feature_df)
        top_factors = self._get_top_contributing_factors(
            features,
            shap_values[0]
        )

        # Store prediction in database
        await self._store_risk_score(
            patient_id=patient_id,
            risk_type='readmission',
            risk_score=float(risk_probability),
            risk_category=risk_category,
            contributing_factors=top_factors
        )

        return {
            "patient_id": patient_id,
            "risk_score": float(risk_probability),
            "risk_category": risk_category,
            "contributing_factors": top_factors,
            "recommendations": self._generate_recommendations(
                risk_category,
                top_factors
            ),
            "model_version": "readmission_rf_v1"
        }

    def _extract_readmission_features(self, admission_data: Dict) -> Dict:
        """Extract features for readmission prediction"""
        return {
            'age': admission_data.get('age'),
            'num_previous_admissions': admission_data.get('prior_admissions'),
            'length_of_stay': admission_data.get('los'),
            'num_diagnoses': len(admission_data.get('diagnoses', [])),
            'num_medications': len(admission_data.get('medications', [])),
            'has_diabetes': 'diabetes' in admission_data.get('diagnoses', []),
            'has_chf': 'chf' in admission_data.get('diagnoses', []),
            'emergency_admission': admission_data.get('admission_type') == 'emergency',
            'discharge_disposition': admission_data.get('discharge_disposition'),
            # More features...
        }

    def _categorize_risk(self, probability: float) -> str:
        """Categorize risk score into levels"""
        if probability >= 0.7:
            return 'critical'
        elif probability >= 0.4:
            return 'high'
        elif probability >= 0.2:
            return 'medium'
        else:
            return 'low'

    def _generate_recommendations(
        self,
        risk_category: str,
        contributing_factors: list
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if risk_category in ['high', 'critical']:
            recommendations.append("Schedule follow-up within 7 days of discharge")
            recommendations.append("Enroll in care management program")

        for factor in contributing_factors:
            if factor['factor'] == 'num_medications' and factor['impact'] > 0:
                recommendations.append("Review medication list for potential deprescribing")
            elif factor['factor'] == 'has_diabetes' and factor['impact'] > 0:
                recommendations.append("Ensure diabetes education and monitoring plan")

        return recommendations
```

#### 4.3 Medical NLP Service

**Architecture**:
```python
# services/ai/medical_nlp_service.py
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import spacy

class MedicalNLPService:
    def __init__(self):
        # Load models
        self.nlp_spacy = spacy.load("en_core_sci_md")  # ScispaCy medical model
        self.ner_model = pipeline(
            "ner",
            model="samrawal/bert-base-uncased_clinical-ner",
            aggregation_strategy="simple"
        )

    async def extract_medical_entities(self, text: str) -> Dict[str, list]:
        """
        Extract medical entities from clinical text
        """
        doc = self.nlp_spacy(text)

        entities = {
            'medications': [],
            'conditions': [],
            'procedures': [],
            'anatomy': [],
            'lab_values': []
        }

        # SpaCy NER
        for ent in doc.ents:
            if ent.label_ == 'CHEMICAL':
                entities['medications'].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.9  # SpaCy doesn't provide scores
                })
            elif ent.label_ == 'DISEASE':
                entities['conditions'].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char
                })

        # Transformer NER for additional coverage
        ner_results = self.ner_model(text)
        for ent in ner_results:
            entity_group = ent['entity_group'].lower()
            if entity_group == 'medication' and ent['score'] > 0.8:
                entities['medications'].append({
                    'text': ent['word'],
                    'start': ent['start'],
                    'end': ent['end'],
                    'confidence': ent['score']
                })

        # Deduplicate
        entities = self._deduplicate_entities(entities)

        return entities

    async def icd10_coding_suggestion(
        self,
        diagnosis_text: str
    ) -> list[Dict[str, Any]]:
        """
        Suggest ICD-10 codes from diagnosis description
        """
        # Use semantic search in vector database
        embedding = await self._get_embedding(diagnosis_text)

        # Search ICD-10 code embeddings
        similar_codes = await self._vector_search(
            embedding=embedding,
            collection='icd10_codes',
            top_k=5
        )

        return similar_codes
```

---

### 5. Data Pipeline Architecture

#### 5.1 ETL with Apache Airflow

**DAG Example**:
```python
# dags/daily_analytics_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_analytics_pipeline',
    default_args=default_args,
    description='Daily analytics ETL pipeline',
    schedule_interval='0 2 * * *',  # Run at 2 AM daily
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['analytics', 'daily']
)

def extract_patient_data(**context):
    """Extract patient data from PostgreSQL"""
    # Implementation
    pass

def transform_patient_metrics(**context):
    """Calculate patient metrics"""
    # Implementation
    pass

def load_to_warehouse(**context):
    """Load to Snowflake data warehouse"""
    # Implementation
    pass

def train_risk_models(**context):
    """Retrain risk stratification models"""
    # Implementation
    pass

extract_task = PythonOperator(
    task_id='extract_patient_data',
    python_callable=extract_patient_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_patient_metrics',
    python_callable=transform_patient_metrics,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    dag=dag
)

train_models_task = PythonOperator(
    task_id='train_risk_models',
    python_callable=train_risk_models,
    dag=dag
)

# Define dependencies
extract_task >> transform_task >> load_task >> train_models_task
```

#### 5.2 Real-Time Event Streaming (Apache Kafka)

**Topics**:
- `patient.created`
- `appointment.scheduled`
- `clinical_note.created`
- `vital_signs.updated`
- `risk_score.calculated`
- `claim.submitted`

**Consumer Example**:
```python
# consumers/risk_score_consumer.py
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'vital_signs.updated',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='risk-scoring-service'
)

async def process_vital_signs_update(message):
    """Process vital signs update and recalculate risk"""
    patient_id = message['patient_id']
    vital_signs = message['data']

    # Check for critical values
    if vital_signs.get('oxygen_saturation', 100) < 90:
        await trigger_alert(patient_id, 'critical_hypoxia')

    # Recalculate risk scores
    await predictive_service.update_patient_risk(patient_id)

    # Emit event
    await kafka_producer.send(
        'risk_score.calculated',
        value={'patient_id': patient_id, 'timestamp': datetime.now().isoformat()}
    )

for message in consumer:
    await process_vital_signs_update(message.value)
```

---

### 6. Integration Layer

#### 6.1 FHIR Gateway

**Technology**: HAPI FHIR Server

**Resources Implemented**:
- Patient
- Practitioner
- Appointment
- Encounter
- Condition
- Observation
- MedicationRequest
- DiagnosticReport
- DocumentReference

**Custom Operations**:
```http
POST /fhir/Patient/$match
POST /fhir/Observation/$lastn
POST /fhir/Encounter/$everything
```

**SMART on FHIR**:
```python
# SMART app launch endpoint
@app.get("/fhir/launch")
async def smart_launch(
    iss: str,  # FHIR server URL
    launch: str  # Launch token
):
    """SMART app launch sequence"""
    # Discover authorization endpoint
    metadata = await get_fhir_metadata(iss)
    authorize_url = metadata['authorize_endpoint']

    # Redirect to authorization server
    return RedirectResponse(
        url=f"{authorize_url}?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"launch={launch}&"
        f"scope=patient/*.read&"
        f"state={generate_state()}&"
        f"aud={iss}"
    )
```

#### 6.2 HL7 v2 Integration (Mirth Connect)

**Channels**:
- ADT Feed (A01, A03, A08 messages)
- Lab Results (ORU^R01)
- Orders (ORM^O01)

**Message Processing**:
```javascript
// Mirth transformer for ADT^A01
var pid = msg['PID'];
var patient = {
    mrn: pid['PID.3']['PID.3.1'].toString(),
    first_name: pid['PID.5']['PID.5.2'].toString(),
    last_name: pid['PID.5']['PID.5.1'].toString(),
    dob: pid['PID.7']['PID.7.1'].toString(),
    sex: pid['PID.8']['PID.8.1'].toString()
};

// Call REST API to create/update patient
var response = router.routeMessage('REST_API', JSON.stringify(patient));
return response;
```

---

### 7. Security Architecture

#### 7.1 Authentication & Authorization

**Multi-Layer Auth**:
```
┌─────────────────────────────────────────┐
│         User Authentication             │
│  ┌──────────┐  ┌──────────┐            │
│  │ Username │  │  OAuth   │            │
│  │ Password │  │  (SSO)   │            │
│  └────┬─────┘  └────┬─────┘            │
│       │             │                   │
│       └──────┬──────┘                   │
│              │                          │
│       ┌──────▼──────┐                  │
│       │     MFA     │                  │
│       │ (TOTP/SMS)  │                  │
│       └──────┬──────┘                  │
└──────────────┼──────────────────────────┘
               │
        ┌──────▼──────┐
        │  JWT Token  │
        │  (15 min)   │
        └──────┬──────┘
               │
┌──────────────▼──────────────────────────┐
│         Authorization (RBAC)            │
│  ┌──────────┐  ┌──────────┐            │
│  │  Roles   │  │ Policies │            │
│  │          │  │          │            │
│  │ - Admin  │  │ - Read   │            │
│  │ - Doctor │  │ - Write  │            │
│  │ - Nurse  │  │ - Delete │            │
│  │ - Patient│  │ - Admin  │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
```

**JWT Implementation**:
```python
# core/security.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "your-secret-key"  # From environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

# Role-based access control decorator
def require_roles(*allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@app.get("/api/v1/admin/users")
@require_roles("admin", "super_admin")
async def list_all_users(current_user: User = Depends(get_current_user)):
    return await user_service.get_all_users()
```

#### 7.2 Data Encryption

**At Rest**:
- PostgreSQL: Transparent Data Encryption (TDE)
- S3: SSE-KMS (AWS Key Management Service)
- Application-level: Fernet encryption for specific PHI fields

**In Transit**:
- TLS 1.3 for all HTTP communications
- mTLS for service-to-service communication
- VPN for external integrations

**Implementation**:
```python
# utils/encryption.py
from cryptography.fernet import Fernet
from typing import Optional

class EncryptionService:
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY.encode()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()

# SQLAlchemy model with encryption
class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID, primary_key=True)
    ssn_encrypted = Column(String)  # Encrypted SSN

    @hybrid_property
    def ssn(self):
        return encryption_service.decrypt(self.ssn_encrypted)

    @ssn.setter
    def ssn(self, value):
        self.ssn_encrypted = encryption_service.encrypt(value)
```

#### 7.3 Audit Logging

**Comprehensive Audit Trail**:
```python
# utils/audit_logger.py
async def log_audit_event(
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: Optional[str],
    changes: Optional[dict] = None,
    phi_accessed: bool = False,
    request: Request = None
):
    """Log audit event for HIPAA compliance"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get('user-agent') if request else None,
        changes=changes,
        phi_accessed=phi_accessed,
        created_at=datetime.utcnow()
    )

    await db.save(audit_log)

    # Also send to centralized logging (ELK)
    logger.info(
        f"AUDIT: {action}",
        extra={
            "user_id": user_id,
            "entity": f"{entity_type}:{entity_id}",
            "phi": phi_accessed
        }
    )

# Decorator for automatic audit logging
def audit_log(entity_type: str, action: str, phi_access: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            entity_id = kwargs.get('id') or kwargs.get('patient_id')

            # Execute function
            result = await func(*args, **kwargs)

            # Log audit event
            await log_audit_event(
                user_id=current_user.id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                phi_accessed=phi_access
            )

            return result
        return wrapper
    return decorator

# Usage
@app.get("/api/v1/patients/{patient_id}")
@audit_log(entity_type="patient", action="read", phi_access=True)
async def get_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    return await patient_service.get_by_id(patient_id)
```

---

### 8. Monitoring & Observability

#### 8.1 Application Performance Monitoring (APM)

**Datadog Integration**:
```python
# main.py
from ddtrace import tracer, patch_all
from ddtrace.contrib.fastapi import patch as fastapi_patch

# Enable automatic instrumentation
patch_all()
fastapi_patch()

# Custom traces
@app.get("/api/v1/patients/{patient_id}")
async def get_patient(patient_id: str):
    with tracer.trace("patient.get", service="health-api") as span:
        span.set_tag("patient.id", patient_id)
        patient = await patient_service.get_by_id(patient_id)
        span.set_tag("patient.age", patient.age)
        return patient

# Custom metrics
from datadog import statsd

statsd.increment('api.request.count', tags=['endpoint:patients', 'method:GET'])
statsd.histogram('api.request.duration', 125.4, tags=['endpoint:patients'])
statsd.gauge('ai.tokens.used', 1250, tags=['model:claude-3-sonnet'])
```

#### 8.2 Logging Strategy

**Structured Logging with ELK Stack**:
```python
# core/logging.py
import structlog
from pythonjsonlogger import jsonlogger

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info(
    "patient_created",
    patient_id=patient.id,
    mrn=patient.mrn,
    practice_id=practice.id,
    duration_ms=125.4
)

logger.error(
    "ai_inference_failed",
    error=str(e),
    model="claude-3-sonnet",
    patient_id=patient_id,
    traceback=traceback.format_exc()
)
```

#### 8.3 Health Checks

```python
# api/health.py
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies"""
    checks = {}

    # Database check
    try:
        await db.execute("SELECT 1")
        checks['database'] = 'healthy'
    except Exception as e:
        checks['database'] = f'unhealthy: {str(e)}'

    # Redis check
    try:
        await redis.ping()
        checks['redis'] = 'healthy'
    except Exception as e:
        checks['redis'] = f'unhealthy: {str(e)}'

    # Claude API check
    try:
        response = await claude_service.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        checks['claude_api'] = 'healthy'
    except Exception as e:
        checks['claude_api'] = f'unhealthy: {str(e)}'

    overall_status = 'healthy' if all(
        v == 'healthy' for v in checks.values()
    ) else 'degraded'

    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## Deployment Architecture

### Cloud Infrastructure (AWS)

```
┌─────────────────────────────────────────────────────────────┐
│                      Route 53 (DNS)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              CloudFront CDN + WAF                            │
│              - DDoS Protection                               │
│              - Static Asset Caching                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│         Application Load Balancer (ALB)                      │
│         - SSL Termination                                    │
│         - Path-based Routing                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼───────┐
│   ECS/EKS    │  │   ECS/EKS   │  │   Lambda    │
│  (Frontend)  │  │  (Backend)  │  │  (Functions)│
│              │  │             │  │             │
│ - Next.js    │  │ - FastAPI   │  │ - Image Proc│
│ - 3 Tasks    │  │ - 5 Tasks   │  │ - Reports   │
│ - Auto Scale │  │ - Auto Scale│  │             │
└───────┬──────┘  └──────┬──────┘  └─────┬───────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼───────┐
│   RDS        │  │ ElastiCache │  │     S3      │
│ (PostgreSQL) │  │   (Redis)   │  │  - Images   │
│ Multi-AZ     │  │ Cluster     │  │  - Documents│
│ Read Replica │  │             │  │  - Backups  │
└──────────────┘  └─────────────┘  └─────────────┘
```

### Kubernetes Deployment (for ML workloads)

```yaml
# kubernetes/ml-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
    spec:
      containers:
      - name: ml-service
        image: health-ai-platform/ml-service:v1.2.0
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: "1"
          limits:
            memory: "8Gi"
            cpu: "4000m"
            nvidia.com/gpu: "1"
        env:
        - name: MODEL_PATH
          value: "/models/readmission_rf_v1.pkl"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
spec:
  selector:
    app: ml-inference
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-inference-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Run unit tests
      run: pytest tests/unit

    - name: Run integration tests
      run: pytest tests/integration

    - name: Security scan
      run: |
        pip install bandit safety
        bandit -r backend/
        safety check

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build Docker images
      run: |
        docker build -t health-ai/backend:${{ github.sha }} backend/
        docker build -t health-ai/frontend:${{ github.sha }} frontend/

    - name: Push to ECR
      run: |
        aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
        docker push health-ai/backend:${{ github.sha }}
        docker push health-ai/frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Update ECS service
      run: |
        aws ecs update-service --cluster production --service backend --force-new-deployment
        aws ecs update-service --cluster production --service frontend --force-new-deployment

    - name: Run database migrations
      run: alembic upgrade head

    - name: Verify deployment
      run: |
        sleep 60
        curl --fail https://api.healthaiplatform.com/health || exit 1
```

---

## Cost Estimates

### Monthly Infrastructure Costs (Production, ~1000 active users)

| Service | Specification | Monthly Cost |
|---------|--------------|--------------|
| **Compute (ECS)** | 5 Backend tasks (2 vCPU, 4GB each) | $250 |
| | 3 Frontend tasks (1 vCPU, 2GB each) | $100 |
| **Database (RDS)** | db.r5.xlarge (4 vCPU, 32GB) Multi-AZ | $600 |
| | Read replica | $300 |
| **Cache (ElastiCache)** | cache.r5.large (2 nodes) | $250 |
| **S3 Storage** | 500GB data + requests | $50 |
| **Load Balancer** | ALB + data transfer | $100 |
| **CloudFront CDN** | 1TB data transfer | $85 |
| **Kubernetes (EKS)** | Control plane + 3 GPU nodes (ml.g4dn.xlarge) | $800 |
| **Monitoring (Datadog)** | Infrastructure + APM + logs (10 hosts) | $450 |
| **AI Services** | Claude API (~5M tokens/month) | $500 |
| **Backup & DR** | S3 Glacier + snapshots | $100 |
| **Other AWS Services** | SES, SNS, Secrets Manager, etc. | $150 |
| **Total** | | **~$3,735/month** |

### Per-User Cost Breakdown
- Infrastructure: $3.74/user/month
- Claude AI: $0.50/user/month (variable)
- **Total**: ~$4.24/user/month at 1000 users

### Scaling Economics
- At 10,000 users: $1.50/user/month
- At 100,000 users: $0.80/user/month

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Response Time (p95)** | < 200ms | Datadog APM |
| **API Response Time (p99)** | < 500ms | Datadog APM |
| **Page Load Time (p75)** | < 2.5s | Real User Monitoring |
| **AI Inference Latency** | < 3s | Custom metrics |
| **Database Query Time** | < 50ms | pgBadger |
| **System Uptime** | 99.9% | StatusPage |
| **Error Rate** | < 0.1% | Sentry |
| **API Rate Limit** | 1000 req/min | Kong metrics |

---

## Disaster Recovery Plan

### Backup Strategy
- **Database**: Automated daily snapshots, retained 30 days
- **S3**: Cross-region replication to backup region
- **Configurations**: Stored in version control (Git)

### Recovery Time Objectives (RTO/RPO)
- **RTO**: 4 hours
- **RPO**: 1 hour

### DR Procedures
1. Activate standby environment in backup region
2. Restore latest database snapshot
3. Update DNS to point to DR environment
4. Verify all services operational
5. Notify users of any data loss

---

This technical architecture provides a robust, scalable, and compliant foundation for a cutting-edge Health AI Platform. Every component is designed with healthcare-specific requirements in mind, prioritizing security, compliance, and reliability alongside innovation.
