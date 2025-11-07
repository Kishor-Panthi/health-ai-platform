"""API router aggregator for v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    appointments,
    auth,
    billing,
    clinical_notes,
    dashboards,
    documents,
    health,
    insurance,
    medical_records,
    messages,
    notifications,
    patients,
    providers,
    reports,
    staff,
    tasks,
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix='/auth', tags=['Authentication'])

# Core entities
api_router.include_router(patients.router, prefix='/patients', tags=['Patients'])
api_router.include_router(appointments.router, prefix='/appointments', tags=['Appointments'])
api_router.include_router(providers.router, prefix='/providers', tags=['Providers'])
api_router.include_router(staff.router, prefix='/staff', tags=['Staff'])

# Medical records
api_router.include_router(medical_records.router, prefix='/medical-records', tags=['Medical Records'])

# Insurance
api_router.include_router(insurance.router, prefix='/insurance', tags=['Insurance'])

# Billing
api_router.include_router(billing.router, prefix='/billing', tags=['Billing'])

# Clinical documentation
api_router.include_router(clinical_notes.router, prefix='/clinical-notes', tags=['Clinical Notes'])

# Documents
api_router.include_router(documents.router, prefix='/documents', tags=['Documents'])

# Communications & Automation
api_router.include_router(messages.router, prefix='/messages', tags=['Messages'])
api_router.include_router(notifications.router, prefix='/notifications', tags=['Notifications'])
api_router.include_router(tasks.router, prefix='/tasks', tags=['Tasks'])

# Analytics & Reporting
api_router.include_router(reports.router, prefix='/reports', tags=['Reports'])
api_router.include_router(dashboards.router, prefix='/dashboards', tags=['Dashboards'])

# Health check
api_router.include_router(health.router, prefix='/health', tags=['Health'])
