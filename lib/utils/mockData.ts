import { Patient, Appointment, Provider, Claim } from "@/lib/types";

// Helper function to generate random IDs
const generateId = () => Math.random().toString(36).substring(2, 11);

// Mock Providers
export const mockProviders: Provider[] = [
  {
    id: "provider-1",
    npi: "1234567890",
    firstName: "Sarah",
    lastName: "Johnson",
    title: "MD",
    specialty: "Family Medicine",
    email: "sarah.johnson@example.com",
    phone: "(555) 123-4567",
    photo: undefined,
    status: "active",
    schedule: [
      { dayOfWeek: 1, startTime: "09:00", endTime: "17:00" },
      { dayOfWeek: 2, startTime: "09:00", endTime: "17:00" },
      { dayOfWeek: 3, startTime: "09:00", endTime: "17:00" },
      { dayOfWeek: 4, startTime: "09:00", endTime: "17:00" },
      { dayOfWeek: 5, startTime: "09:00", endTime: "15:00" },
    ],
    acceptingNewPatients: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "provider-2",
    npi: "0987654321",
    firstName: "Michael",
    lastName: "Smith",
    title: "DO",
    specialty: "Internal Medicine",
    email: "michael.smith@example.com",
    phone: "(555) 234-5678",
    photo: undefined,
    status: "active",
    schedule: [
      { dayOfWeek: 1, startTime: "08:00", endTime: "16:00" },
      { dayOfWeek: 2, startTime: "08:00", endTime: "16:00" },
      { dayOfWeek: 3, startTime: "08:00", endTime: "16:00" },
      { dayOfWeek: 4, startTime: "08:00", endTime: "16:00" },
    ],
    acceptingNewPatients: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
];

// Mock Patients
export const mockPatients: Patient[] = [
  {
    id: "patient-1",
    mrn: "MRN001",
    firstName: "John",
    lastName: "Doe",
    dateOfBirth: new Date("1985-06-15"),
    gender: "male",
    email: "john.doe@example.com",
    phone: "(555) 111-2222",
    address: {
      street: "123 Main St",
      city: "Springfield",
      state: "IL",
      zipCode: "62701",
      country: "USA",
    },
    emergencyContact: {
      name: "Jane Doe",
      relationship: "Spouse",
      phone: "(555) 111-3333",
    },
    insurance: [
      {
        id: "ins-1",
        provider: "Blue Cross Blue Shield",
        policyNumber: "BCBS123456",
        groupNumber: "GRP789",
        subscriberName: "John Doe",
        subscriberRelationship: "Self",
        isPrimary: true,
        effectiveDate: new Date("2023-01-01"),
        status: "active",
      },
    ],
    tags: ["diabetes", "hypertension"],
    communicationPreference: "email",
    status: "active",
    assignedProvider: "provider-1",
    createdAt: new Date("2023-03-15"),
    updatedAt: new Date("2024-11-01"),
  },
  {
    id: "patient-2",
    mrn: "MRN002",
    firstName: "Jane",
    lastName: "Smith",
    dateOfBirth: new Date("1990-03-22"),
    gender: "female",
    email: "jane.smith@example.com",
    phone: "(555) 222-3333",
    address: {
      street: "456 Oak Ave",
      city: "Springfield",
      state: "IL",
      zipCode: "62702",
      country: "USA",
    },
    emergencyContact: {
      name: "Robert Smith",
      relationship: "Father",
      phone: "(555) 222-4444",
    },
    insurance: [
      {
        id: "ins-2",
        provider: "Aetna",
        policyNumber: "AET987654",
        groupNumber: "GRP456",
        subscriberName: "Jane Smith",
        subscriberRelationship: "Self",
        isPrimary: true,
        effectiveDate: new Date("2023-01-01"),
        status: "active",
      },
    ],
    tags: ["asthma"],
    communicationPreference: "sms",
    status: "active",
    assignedProvider: "provider-1",
    createdAt: new Date("2023-05-20"),
    updatedAt: new Date("2024-10-15"),
  },
];

// Mock Appointments
export const mockAppointments: Appointment[] = [
  {
    id: "apt-1",
    patientId: "patient-1",
    patientName: "John Doe",
    providerId: "provider-1",
    providerName: "Dr. Sarah Johnson",
    appointmentType: "consultation",
    date: new Date(),
    startTime: "09:00",
    endTime: "09:30",
    duration: 30,
    status: "confirmed",
    reason: "Annual physical",
    room: "Room 101",
    isRecurring: false,
    remindersSent: [
      {
        type: "email",
        sentAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
        delivered: true,
        opened: true,
      },
    ],
    createdAt: new Date("2024-10-01"),
    updatedAt: new Date("2024-10-01"),
  },
  {
    id: "apt-2",
    patientId: "patient-2",
    patientName: "Jane Smith",
    providerId: "provider-1",
    providerName: "Dr. Sarah Johnson",
    appointmentType: "follow-up",
    date: new Date(),
    startTime: "10:30",
    endTime: "11:00",
    duration: 30,
    status: "checked-in",
    reason: "Follow-up for asthma",
    room: "Room 102",
    isRecurring: false,
    checkedInAt: new Date(),
    remindersSent: [
      {
        type: "sms",
        sentAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
        delivered: true,
      },
    ],
    createdAt: new Date("2024-10-15"),
    updatedAt: new Date(),
  },
];

// Generator functions
export function generateMockPatients(count: number): Patient[] {
  const patients: Patient[] = [];
  const firstNames = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Lisa"];
  const lastNames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"];

  for (let i = 0; i < count; i++) {
    patients.push({
      id: `patient-${generateId()}`,
      mrn: `MRN${String(i + 1).padStart(6, '0')}`,
      firstName: firstNames[Math.floor(Math.random() * firstNames.length)],
      lastName: lastNames[Math.floor(Math.random() * lastNames.length)],
      dateOfBirth: new Date(1950 + Math.floor(Math.random() * 50), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
      gender: Math.random() > 0.5 ? "male" : "female",
      email: `patient${i + 1}@example.com`,
      phone: `(555) ${String(Math.floor(Math.random() * 900) + 100)}-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      address: {
        street: `${Math.floor(Math.random() * 9999) + 1} Main St`,
        city: "Springfield",
        state: "IL",
        zipCode: "62701",
        country: "USA",
      },
      emergencyContact: {
        name: "Emergency Contact",
        relationship: "Family",
        phone: "(555) 999-9999",
      },
      insurance: [],
      tags: [],
      communicationPreference: "email",
      status: "active",
      assignedProvider: mockProviders[Math.floor(Math.random() * mockProviders.length)].id,
      createdAt: new Date(),
      updatedAt: new Date(),
    });
  }

  return patients;
}

export function generateMockAppointments(count: number): Appointment[] {
  const appointments: Appointment[] = [];
  const types: Appointment["appointmentType"][] = ["consultation", "follow-up", "procedure", "physical-exam"];
  const statuses: Appointment["status"][] = ["scheduled", "confirmed", "checked-in", "completed"];

  for (let i = 0; i < count; i++) {
    const date = new Date();
    date.setDate(date.getDate() + Math.floor(Math.random() * 30) - 15);

    appointments.push({
      id: `apt-${generateId()}`,
      patientId: mockPatients[Math.floor(Math.random() * mockPatients.length)].id,
      patientName: "Patient Name",
      providerId: mockProviders[Math.floor(Math.random() * mockProviders.length)].id,
      providerName: "Provider Name",
      appointmentType: types[Math.floor(Math.random() * types.length)],
      date,
      startTime: `${String(Math.floor(Math.random() * 8) + 9).padStart(2, '0')}:00`,
      endTime: `${String(Math.floor(Math.random() * 8) + 9).padStart(2, '0')}:30`,
      duration: 30,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      reason: "Medical consultation",
      isRecurring: false,
      remindersSent: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    });
  }

  return appointments;
}
