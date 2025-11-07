"""Comprehensive database seeding script with realistic healthcare data."""

import asyncio
import random
from datetime import datetime, timedelta, time
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import (
    Practice,
    User,
    UserRole,
    Patient,
    Provider,
    Staff,
    StaffRole,
    ProviderSchedule,
    DayOfWeek,
    Appointment,
)

# Sample data
SPECIALTIES = [
    'Family Medicine', 'Internal Medicine', 'Pediatrics', 'Cardiology',
    'Dermatology', 'Orthopedics', 'Psychiatry', 'Obstetrics and Gynecology',
    'Neurology', 'Radiology', 'Anesthesiology', 'Emergency Medicine'
]

DEPARTMENTS = ['Primary Care', 'Specialty Care', 'Surgical Services', 'Diagnostic Services', 'Administrative']

PROVIDER_NAMES = [
    ('James', 'Smith', 'MD'), ('Emily', 'Johnson', 'DO'), ('Michael', 'Williams', 'MD'),
    ('Sarah', 'Brown', 'NP'), ('David', 'Jones', 'MD'), ('Jennifer', 'Garcia', 'PA'),
    ('Robert', 'Miller', 'MD'), ('Lisa', 'Davis', 'MD'), ('William', 'Rodriguez', 'DO'),
    ('Maria', 'Martinez', 'MD')
]

STAFF_NAMES = [
    ('John', 'Anderson', StaffRole.RECEPTIONIST),
    ('Anna', 'Thomas', StaffRole.NURSE),
    ('Chris', 'Jackson', StaffRole.MEDICAL_ASSISTANT),
    ('Patricia', 'White', StaffRole.BILLING_SPECIALIST),
    ('Mark', 'Harris', StaffRole.PRACTICE_MANAGER),
    ('Linda', 'Martin', StaffRole.NURSE),
    ('Daniel', 'Thompson', StaffRole.MEDICAL_ASSISTANT),
    ('Karen', 'Garcia', StaffRole.LABORATORY_TECHNICIAN),
]

PATIENT_FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica'
]

PATIENT_LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas'
]

APPOINTMENT_TYPES = [
    'Annual Physical', 'Follow-up Visit', 'New Patient Consultation',
    'Sick Visit', 'Vaccination', 'Lab Work Review', 'Procedure',
    'Telehealth Visit', 'Urgent Care', 'Preventive Care'
]

APPOINTMENT_STATUSES = ['scheduled', 'confirmed', 'checked-in', 'completed', 'cancelled']


async def seed_database():
    """Main seeding function."""
    print("🌱 Starting comprehensive database seeding...")

    async with AsyncSessionLocal() as db:
        try:
            # Create practice
            print("\n📍 Creating practice...")
            practice = await create_practice(db)

            # Create admin user
            print("\n👤 Creating admin user...")
            admin = await create_admin_user(db, practice.id)

            # Create providers
            print("\n⚕️  Creating providers (10)...")
            providers = await create_providers(db, practice.id, admin.id)

            # Create staff
            print("\n👥 Creating staff members (8)...")
            staff = await create_staff_members(db, practice.id, admin.id)

            # Create provider schedules
            print("\n📅 Creating provider schedules...")
            await create_provider_schedules(db, providers, admin.id)

            # Create patients
            print("\n🏥 Creating patients (50)...")
            patients = await create_patients(db, practice.id, providers, admin.id)

            # Create appointments
            print("\n📋 Creating appointments (100)...")
            await create_appointments(db, practice.id, patients, providers, admin.id)

            await db.commit()
            print("\n✅ Database seeding completed successfully!")
            print(f"\n📊 Summary:")
            print(f"   - 1 Practice: Codex Health Medical Center")
            print(f"   - 1 Admin user (admin@codexhealth.local / Admin123!Secure)")
            print(f"   - {len(providers)} Providers")
            print(f"   - {len(staff)} Staff members")
            print(f"   - {len(patients)} Patients")
            print(f"   - ~100 Appointments")
            print(f"\n🔐 Login Credentials:")
            print(f"   Admin: admin@codexhealth.local / Admin123!Secure")
            print(f"   Provider: james.smith@codexhealth.local / Provider123!")
            print(f"   Staff: john.anderson@codexhealth.local / Staff123!")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
            raise


async def create_practice(db: AsyncSession) -> Practice:
    """Create a practice."""
    practice = Practice(
        name='Codex Health Medical Center',
        domain='codexhealth.local',
        timezone='America/New_York',
        address_line1='123 Medical Plaza Drive',
        city='New York',
        state='NY',
        postal_code='10001',
    )
    db.add(practice)
    await db.flush()
    print(f"   ✓ Created practice: {practice.name} ({practice.domain})")
    return practice


async def create_admin_user(db: AsyncSession, practice_id: UUID) -> User:
    """Create admin user."""
    admin = User(
        practice_id=practice_id,
        email='admin@codexhealth.local',
        hashed_password=get_password_hash('Admin123!Secure'),
        full_name='System Administrator',
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    print(f"   ✓ Created admin: {admin.email}")
    return admin


async def create_providers(db: AsyncSession, practice_id: UUID, created_by: UUID) -> list[Provider]:
    """Create provider users and profiles."""
    providers = []

    for i, (first, last, title) in enumerate(PROVIDER_NAMES):
        # Create user account
        user = User(
            practice_id=practice_id,
            email=f'{first.lower()}.{last.lower()}@codexhealth.local',
            hashed_password=get_password_hash('Provider123!'),
            full_name=f'Dr. {first} {last}',
            role=UserRole.PROVIDER,
            is_active=True,
        )
        db.add(user)
        await db.flush()

        # Create provider profile
        specialty = SPECIALTIES[i % len(SPECIALTIES)]
        provider = Provider(
            practice_id=practice_id,
            user_id=user.id,
            npi=f'12345678{i:02d}',
            license_number=f'MD{i+1000:05d}',
            license_state='NY',
            title=title,
            specialty=specialty,
            department=random.choice(['Primary Care', 'Specialty Care']),
            accepting_new_patients=random.choice([True, True, True, False]),
            years_of_experience=random.randint(3, 30),
            education=f'{random.choice(["Harvard", "Johns Hopkins", "Stanford", "Yale"])} Medical School',
            board_certifications=f'Board Certified in {specialty}',
            phone_direct=f'(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}',
            email_work=user.email,
            bio=f'Dr. {first} {last} is a dedicated {specialty} specialist with extensive experience in patient care.',
            languages_spoken='English, Spanish',
            is_active=True,
        )
        db.add(provider)
        await db.flush()
        providers.append(provider)
        print(f"   ✓ Created provider: Dr. {first} {last} ({specialty})")

    return providers


async def create_staff_members(db: AsyncSession, practice_id: UUID, created_by: UUID) -> list[Staff]:
    """Create staff users and profiles."""
    staff_members = []

    for i, (first, last, role) in enumerate(STAFF_NAMES):
        # Create user account
        user = User(
            practice_id=practice_id,
            email=f'{first.lower()}.{last.lower()}@codexhealth.local',
            hashed_password=get_password_hash('Staff123!'),
            full_name=f'{first} {last}',
            role=UserRole.STAFF,
            is_active=True,
        )
        db.add(user)
        await db.flush()

        # Create staff profile
        staff = Staff(
            practice_id=practice_id,
            user_id=user.id,
            role=role,
            employee_id=f'EMP{i+1000:04d}',
            job_title=role.value.replace('_', ' ').title(),
            department=random.choice(DEPARTMENTS),
            hire_date=f'202{random.randint(0, 4)}-{random.randint(1, 12):02d}-01',
            phone_work=f'(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}',
            email_work=user.email,
            is_full_time=random.choice([True, True, True, False]),
            is_active=True,
        )
        db.add(staff)
        await db.flush()
        staff_members.append(staff)
        print(f"   ✓ Created staff: {first} {last} ({role.value})")

    return staff_members


async def create_provider_schedules(db: AsyncSession, providers: list[Provider], created_by: UUID):
    """Create weekly schedules for providers."""
    schedule_count = 0
    for provider in providers:
        # Most providers work Monday-Friday
        working_days = [0, 1, 2, 3, 4]  # Mon-Fri
        if random.random() < 0.3:  # 30% also work Saturday
            working_days.append(5)

        for day in working_days:
            schedule = ProviderSchedule(
                provider_id=provider.id,
                day_of_week=day,
                start_time=time(8, 0),
                end_time=time(17, 0) if day < 5 else time(13, 0),
                location='Main Clinic',
                is_available=True,
                slot_duration_minutes=random.choice([15, 20, 30]),
                max_patients_per_slot=1,
                lunch_break_start=time(12, 0),
                lunch_break_end=time(13, 0),
            )
            db.add(schedule)
            schedule_count += 1

    await db.flush()
    print(f"   ✓ Created {schedule_count} schedule blocks")


async def create_patients(
    db: AsyncSession,
    practice_id: UUID,
    providers: list[Provider],
    created_by: UUID
) -> list[Patient]:
    """Create patients."""
    patients = []

    for i in range(50):
        first_name = random.choice(PATIENT_FIRST_NAMES)
        last_name = random.choice(PATIENT_LAST_NAMES)

        # Random date of birth (ages 1-90)
        age_years = random.randint(1, 90)
        dob = datetime.now().date() - timedelta(days=age_years * 365)

        patient = Patient(
            practice_id=practice_id,
            mrn=f'MRN{i+10000:06d}',
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            email=f'{first_name.lower()}.{last_name.lower()}{i}@email.com',
            phone=f'(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}',
            address_line1=f'{random.randint(100, 9999)} {random.choice(["Main", "Oak", "Maple", "Cedar"])} Street',
            city='New York',
            state='NY',
            postal_code=f'100{random.randint(10, 99)}',
            emergency_contact_name=f'{random.choice(PATIENT_FIRST_NAMES)} {random.choice(PATIENT_LAST_NAMES)}',
            emergency_contact_phone=f'(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}',
            is_deleted=False,
        )
        db.add(patient)
        await db.flush()
        patients.append(patient)

        if (i + 1) % 10 == 0:
            print(f"   ✓ Created {i + 1} patients...")

    return patients


async def create_appointments(
    db: AsyncSession,
    practice_id: UUID,
    patients: list[Patient],
    providers: list[Provider],
    created_by: UUID
):
    """Create appointments."""
    start_date = datetime.now() - timedelta(days=30)  # 30 days ago
    end_date = datetime.now() + timedelta(days=60)    # 60 days future

    for i in range(100):
        # Random date between start and end
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        appt_date = start_date + timedelta(days=random_days)

        # Set to business hours (8 AM - 5 PM)
        hour = random.randint(8, 16)
        minute = random.choice([0, 15, 30, 45])
        appt_datetime = appt_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Determine status based on date
        if appt_datetime < datetime.now():
            status = random.choice(['completed', 'completed', 'completed', 'no-show', 'cancelled'])
        elif appt_datetime < datetime.now() + timedelta(days=7):
            status = random.choice(['scheduled', 'confirmed', 'confirmed'])
        else:
            status = 'scheduled'

        appointment = Appointment(
            practice_id=practice_id,
            patient_id=random.choice(patients).id,
            provider_id=random.choice(providers).user_id,  # appointments reference user_id
            scheduled_at=appt_datetime,
            duration_minutes=random.choice([15, 30, 45, 60]),
            appointment_type=random.choice(APPOINTMENT_TYPES),
            status=status,
            notes=f'Appointment for {random.choice(APPOINTMENT_TYPES).lower()}',
            is_deleted=False,
        )
        db.add(appointment)

        if (i + 1) % 20 == 0:
            print(f"   ✓ Created {i + 1} appointments...")

    await db.flush()


async def main():
    """Run the seeding script."""
    await seed_database()


if __name__ == '__main__':
    asyncio.run(main())
