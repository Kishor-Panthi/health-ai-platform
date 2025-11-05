import {
  Patient,
  Appointment,
  Provider,
  Claim,
  Staff,
  Referral,
  Message,
  MessageTemplate,
  Specialist,
  AutomationRule,
  Practice,
  InsuranceInfo
} from "@/lib/types";

// Helper function to generate random IDs
const generateId = () => Math.random().toString(36).substring(2, 11);

// Mock Practice Info
export const mockPractice: Practice = {
  id: "practice-1",
  name: "Springfield Family Medicine",
  npi: "1234567890",
  taxId: "12-3456789",
  phone: "(555) 100-2000",
  fax: "(555) 100-2001",
  email: "info@springfieldfm.com",
  website: "https://springfieldfm.com",
  address: {
    street: "100 Medical Plaza",
    city: "Springfield",
    state: "IL",
    zipCode: "62701",
    country: "USA",
  },
  businessHours: [
    { dayOfWeek: 1, openTime: "08:00", closeTime: "17:00", isClosed: false },
    { dayOfWeek: 2, openTime: "08:00", closeTime: "17:00", isClosed: false },
    { dayOfWeek: 3, openTime: "08:00", closeTime: "17:00", isClosed: false },
    { dayOfWeek: 4, openTime: "08:00", closeTime: "17:00", isClosed: false },
    { dayOfWeek: 5, openTime: "08:00", closeTime: "15:00", isClosed: false },
    { dayOfWeek: 6, openTime: "09:00", closeTime: "12:00", isClosed: false },
    { dayOfWeek: 0, openTime: "00:00", closeTime: "00:00", isClosed: true },
  ],
  settings: {
    appointmentDuration: 30,
    appointmentBuffer: 0,
    allowOnlineBooking: true,
    requireInsuranceVerification: true,
    sendAutomatedReminders: true,
    reminderHours: [24, 2],
    timezone: "America/Chicago",
  },
  logo: undefined,
  createdAt: new Date("2023-01-01"),
  updatedAt: new Date("2024-11-01"),
};

// Insurance Companies
export const insuranceCompanies = [
  "Blue Cross Blue Shield",
  "Aetna",
  "UnitedHealthcare",
  "Cigna",
  "Humana",
  "Medicare",
  "Medicaid",
  "Kaiser Permanente",
  "Anthem",
  "WellCare",
];

// CPT Codes (Common Procedure Codes)
export const cptCodes = [
  { code: "99201", description: "Office visit, new patient, level 1", fee: 50 },
  { code: "99202", description: "Office visit, new patient, level 2", fee: 80 },
  { code: "99203", description: "Office visit, new patient, level 3", fee: 130 },
  { code: "99204", description: "Office visit, new patient, level 4", fee: 180 },
  { code: "99205", description: "Office visit, new patient, level 5", fee: 250 },
  { code: "99211", description: "Office visit, established patient, level 1", fee: 35 },
  { code: "99212", description: "Office visit, established patient, level 2", fee: 65 },
  { code: "99213", description: "Office visit, established patient, level 3", fee: 105 },
  { code: "99214", description: "Office visit, established patient, level 4", fee: 155 },
  { code: "99215", description: "Office visit, established patient, level 5", fee: 205 },
  { code: "99385", description: "Initial preventive visit, 18-39 years", fee: 180 },
  { code: "99386", description: "Initial preventive visit, 40-64 years", fee: 200 },
  { code: "99387", description: "Initial preventive visit, 65+ years", fee: 220 },
  { code: "99395", description: "Periodic preventive visit, 18-39 years", fee: 160 },
  { code: "99396", description: "Periodic preventive visit, 40-64 years", fee: 180 },
  { code: "99397", description: "Periodic preventive visit, 65+ years", fee: 200 },
  { code: "80053", description: "Comprehensive metabolic panel", fee: 25 },
  { code: "85025", description: "Complete blood count with differential", fee: 18 },
  { code: "80061", description: "Lipid panel", fee: 30 },
  { code: "83036", description: "Hemoglobin A1C", fee: 22 },
];

// ICD-10 Codes (Diagnosis Codes)
export const icd10Codes = [
  { code: "E11.9", description: "Type 2 diabetes mellitus without complications" },
  { code: "I10", description: "Essential (primary) hypertension" },
  { code: "J45.909", description: "Unspecified asthma, uncomplicated" },
  { code: "E78.5", description: "Hyperlipidemia, unspecified" },
  { code: "M79.3", description: "Panniculitis, unspecified" },
  { code: "R50.9", description: "Fever, unspecified" },
  { code: "J02.9", description: "Acute pharyngitis, unspecified" },
  { code: "M25.511", description: "Pain in right shoulder" },
  { code: "M25.512", description: "Pain in left shoulder" },
  { code: "R51", description: "Headache" },
  { code: "R05", description: "Cough" },
  { code: "J06.9", description: "Acute upper respiratory infection, unspecified" },
  { code: "N39.0", description: "Urinary tract infection, site not specified" },
  { code: "K21.9", description: "Gastro-esophageal reflux disease without esophagitis" },
  { code: "F41.9", description: "Anxiety disorder, unspecified" },
];

// Mock Providers
export const mockProviders: Provider[] = [
  {
    id: "provider-1",
    npi: "1234567890",
    firstName: "Sarah",
    lastName: "Johnson",
    title: "MD",
    specialty: "Family Medicine",
    email: "sarah.johnson@springfieldfm.com",
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
    email: "michael.smith@springfieldfm.com",
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
  {
    id: "provider-3",
    npi: "1122334455",
    firstName: "Emily",
    lastName: "Chen",
    title: "MD",
    specialty: "Pediatrics",
    email: "emily.chen@springfieldfm.com",
    phone: "(555) 345-6789",
    photo: undefined,
    status: "active",
    schedule: [
      { dayOfWeek: 1, startTime: "08:30", endTime: "16:30" },
      { dayOfWeek: 2, startTime: "08:30", endTime: "16:30" },
      { dayOfWeek: 3, startTime: "08:30", endTime: "16:30" },
      { dayOfWeek: 4, startTime: "08:30", endTime: "16:30" },
      { dayOfWeek: 5, startTime: "08:30", endTime: "12:30" },
    ],
    acceptingNewPatients: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "provider-4",
    npi: "2233445566",
    firstName: "David",
    lastName: "Martinez",
    title: "PA-C",
    specialty: "Family Medicine",
    email: "david.martinez@springfieldfm.com",
    phone: "(555) 456-7890",
    photo: undefined,
    status: "active",
    schedule: [
      { dayOfWeek: 1, startTime: "10:00", endTime: "18:00" },
      { dayOfWeek: 2, startTime: "10:00", endTime: "18:00" },
      { dayOfWeek: 3, startTime: "10:00", endTime: "18:00" },
      { dayOfWeek: 4, startTime: "10:00", endTime: "18:00" },
      { dayOfWeek: 5, startTime: "10:00", endTime: "18:00" },
    ],
    acceptingNewPatients: true,
    createdAt: new Date("2023-06-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "provider-5",
    npi: "3344556677",
    firstName: "Lisa",
    lastName: "Patel",
    title: "NP",
    specialty: "Family Medicine",
    email: "lisa.patel@springfieldfm.com",
    phone: "(555) 567-8901",
    photo: undefined,
    status: "active",
    schedule: [
      { dayOfWeek: 1, startTime: "09:00", endTime: "17:00" },
      { dayOfWeek: 3, startTime: "09:00", endTime: "17:00" },
      { dayOfWeek: 5, startTime: "09:00", endTime: "17:00" },
    ],
    acceptingNewPatients: true,
    createdAt: new Date("2023-08-01"),
    updatedAt: new Date("2024-01-01"),
  },
];

// Mock Staff
export const mockStaff: Staff[] = [
  {
    id: "staff-1",
    firstName: "Amanda",
    lastName: "Williams",
    email: "amanda.williams@springfieldfm.com",
    phone: "(555) 678-9012",
    role: "receptionist",
    status: "active",
    permissions: ["view_appointments", "create_appointments", "view_patients"],
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "staff-2",
    firstName: "Robert",
    lastName: "Taylor",
    email: "robert.taylor@springfieldfm.com",
    phone: "(555) 789-0123",
    role: "nurse",
    status: "active",
    permissions: ["view_appointments", "view_patients", "update_patients", "view_medical_records"],
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "staff-3",
    firstName: "Jennifer",
    lastName: "Brown",
    email: "jennifer.brown@springfieldfm.com",
    phone: "(555) 890-1234",
    role: "billing",
    status: "active",
    permissions: ["view_billing", "create_claims", "view_payments", "create_statements"],
    createdAt: new Date("2023-02-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "staff-4",
    firstName: "Jessica",
    lastName: "Anderson",
    email: "jessica.anderson@springfieldfm.com",
    phone: "(555) 901-2345",
    role: "office_manager",
    status: "active",
    permissions: ["all"],
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
];

// Mock Specialists (for referrals)
export const mockSpecialists: Specialist[] = [
  {
    id: "specialist-1",
    npi: "4455667788",
    firstName: "James",
    lastName: "Wilson",
    title: "MD",
    specialty: "Cardiology",
    practiceName: "Springfield Cardiology Associates",
    phone: "(555) 111-2222",
    fax: "(555) 111-2223",
    email: "jwilson@springfieldcardio.com",
    address: {
      street: "200 Heart Lane",
      city: "Springfield",
      state: "IL",
      zipCode: "62701",
      country: "USA",
    },
    acceptingReferrals: true,
  },
  {
    id: "specialist-2",
    npi: "5566778899",
    firstName: "Maria",
    lastName: "Rodriguez",
    title: "MD",
    specialty: "Endocrinology",
    practiceName: "Springfield Diabetes & Endocrine Center",
    phone: "(555) 222-3333",
    fax: "(555) 222-3334",
    email: "mrodriguez@springfieldendo.com",
    address: {
      street: "300 Metabolic Way",
      city: "Springfield",
      state: "IL",
      zipCode: "62702",
      country: "USA",
    },
    acceptingReferrals: true,
  },
  {
    id: "specialist-3",
    npi: "6677889900",
    firstName: "Thomas",
    lastName: "Lee",
    title: "MD",
    specialty: "Orthopedic Surgery",
    practiceName: "Springfield Orthopedics",
    phone: "(555) 333-4444",
    fax: "(555) 333-4445",
    email: "tlee@springfieldortho.com",
    address: {
      street: "400 Bone Street",
      city: "Springfield",
      state: "IL",
      zipCode: "62703",
      country: "USA",
    },
    acceptingReferrals: true,
  },
  {
    id: "specialist-4",
    npi: "7788990011",
    firstName: "Patricia",
    lastName: "Kim",
    title: "MD",
    specialty: "Dermatology",
    practiceName: "Springfield Dermatology Clinic",
    phone: "(555) 444-5555",
    fax: "(555) 444-5556",
    email: "pkim@springfieldderm.com",
    address: {
      street: "500 Skin Avenue",
      city: "Springfield",
      state: "IL",
      zipCode: "62704",
      country: "USA",
    },
    acceptingReferrals: true,
  },
  {
    id: "specialist-5",
    npi: "8899001122",
    firstName: "Christopher",
    lastName: "Garcia",
    title: "MD",
    specialty: "Gastroenterology",
    practiceName: "Springfield Digestive Health",
    phone: "(555) 555-6666",
    fax: "(555) 555-6667",
    email: "cgarcia@springfieldgi.com",
    address: {
      street: "600 GI Boulevard",
      city: "Springfield",
      state: "IL",
      zipCode: "62705",
      country: "USA",
    },
    acceptingReferrals: true,
  },
];

// Message Templates
export const messageTemplates: MessageTemplate[] = [
  {
    id: "template-1",
    name: "Appointment Reminder",
    category: "appointment",
    subject: "Reminder: Upcoming Appointment",
    body: "Hi {{patientName}},\n\nThis is a reminder about your upcoming appointment with {{providerName}} on {{appointmentDate}} at {{appointmentTime}}.\n\nPlease arrive 15 minutes early to complete any necessary paperwork.\n\nIf you need to reschedule, please call us at {{practicePhone}}.\n\nThank you,\n{{practiceName}}",
    variables: ["patientName", "providerName", "appointmentDate", "appointmentTime", "practicePhone", "practiceName"],
    isActive: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "template-2",
    name: "Appointment Confirmation",
    category: "appointment",
    subject: "Appointment Confirmed",
    body: "Hi {{patientName}},\n\nYour appointment has been confirmed:\n\nDate: {{appointmentDate}}\nTime: {{appointmentTime}}\nProvider: {{providerName}}\nLocation: {{practiceAddress}}\n\nSee you soon!\n{{practiceName}}",
    variables: ["patientName", "appointmentDate", "appointmentTime", "providerName", "practiceAddress", "practiceName"],
    isActive: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "template-3",
    name: "Lab Results Available",
    category: "results",
    subject: "Your Lab Results Are Ready",
    body: "Hi {{patientName}},\n\nYour recent lab results are now available in your patient portal.\n\nPlease log in to review them, or call our office if you have any questions.\n\nThank you,\n{{practiceName}}",
    variables: ["patientName", "practiceName"],
    isActive: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "template-4",
    name: "Preventive Care Reminder",
    category: "preventive",
    subject: "Time for Your Annual Checkup",
    body: "Hi {{patientName}},\n\nIt's been about a year since your last visit. It's time to schedule your annual preventive care appointment.\n\nCall us at {{practicePhone}} or book online at {{practiceWebsite}}.\n\nStaying on top of your health is important!\n\n{{practiceName}}",
    variables: ["patientName", "practicePhone", "practiceWebsite", "practiceName"],
    isActive: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "template-5",
    name: "Payment Receipt",
    category: "billing",
    subject: "Payment Receipt",
    body: "Hi {{patientName}},\n\nThank you for your payment of ${{amount}} on {{paymentDate}}.\n\nPayment Method: {{paymentMethod}}\nConfirmation Number: {{confirmationNumber}}\n\nThank you,\n{{practiceName}}",
    variables: ["patientName", "amount", "paymentDate", "paymentMethod", "confirmationNumber", "practiceName"],
    isActive: true,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
];

// Automation Rules
export const automationRules: AutomationRule[] = [
  {
    id: "rule-1",
    name: "Send appointment reminder 24 hours before",
    description: "Automatically send appointment reminders via preferred communication method",
    trigger: {
      type: "time_based",
      event: "appointment_scheduled",
      conditions: [
        { field: "hours_until_appointment", operator: "equals", value: 24 },
      ],
    },
    conditions: [
      { field: "appointment_status", operator: "equals", value: "confirmed" },
    ],
    actions: [
      {
        type: "send_message",
        messageType: "automatic",
        templateId: "template-1",
        channel: "preferred",
      },
    ],
    isActive: true,
    priority: 1,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "rule-2",
    name: "Send confirmation after booking",
    description: "Send appointment confirmation immediately after booking",
    trigger: {
      type: "event_based",
      event: "appointment_created",
      conditions: [],
    },
    conditions: [],
    actions: [
      {
        type: "send_message",
        messageType: "automatic",
        templateId: "template-2",
        channel: "preferred",
      },
    ],
    isActive: true,
    priority: 1,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
  {
    id: "rule-3",
    name: "Annual wellness reminder",
    description: "Remind patients about annual checkup 11 months after last visit",
    trigger: {
      type: "time_based",
      event: "last_visit",
      conditions: [
        { field: "months_since_last_visit", operator: "equals", value: 11 },
      ],
    },
    conditions: [],
    actions: [
      {
        type: "send_message",
        messageType: "automatic",
        templateId: "template-4",
        channel: "email",
      },
    ],
    isActive: true,
    priority: 2,
    createdAt: new Date("2023-01-01"),
    updatedAt: new Date("2024-01-01"),
  },
];

// Mock Patients - Expanded list with varied demographics
const firstNames = [
  "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
  "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
  "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
  "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
  "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
  "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
  "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
];

const lastNames = [
  "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
  "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
  "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
  "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
  "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
  "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
];

export const mockPatients: Patient[] = [
  {
    id: "patient-1",
    mrn: "MRN000001",
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
    mrn: "MRN000002",
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
  const patients: Patient[] = [...mockPatients];

  for (let i = mockPatients.length; i < count; i++) {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const gender = Math.random() > 0.5 ? "male" : "female";
    const insuranceProvider = insuranceCompanies[Math.floor(Math.random() * insuranceCompanies.length)];

    const hasInsurance = Math.random() > 0.1; // 90% have insurance
    const insurance: InsuranceInfo[] = hasInsurance ? [
      {
        id: `ins-${generateId()}`,
        provider: insuranceProvider,
        policyNumber: `${insuranceProvider.substring(0, 3).toUpperCase()}${Math.floor(Math.random() * 1000000)}`,
        groupNumber: `GRP${Math.floor(Math.random() * 10000)}`,
        subscriberName: `${firstName} ${lastName}`,
        subscriberRelationship: "Self",
        isPrimary: true,
        effectiveDate: new Date(2022 + Math.floor(Math.random() * 3), Math.floor(Math.random() * 12), 1),
        status: "active",
      },
    ] : [];

    const tags: string[] = [];
    if (Math.random() > 0.7) tags.push("diabetes");
    if (Math.random() > 0.7) tags.push("hypertension");
    if (Math.random() > 0.8) tags.push("asthma");
    if (Math.random() > 0.85) tags.push("high-risk");
    if (Math.random() > 0.9) tags.push("chronic-pain");

    patients.push({
      id: `patient-${generateId()}`,
      mrn: `MRN${String(i + 1).padStart(6, "0")}`,
      firstName,
      lastName,
      dateOfBirth: new Date(
        1940 + Math.floor(Math.random() * 65),
        Math.floor(Math.random() * 12),
        Math.floor(Math.random() * 28) + 1
      ),
      gender,
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`,
      phone: `(555) ${String(Math.floor(Math.random() * 900) + 100)}-${String(
        Math.floor(Math.random() * 9000) + 1000
      )}`,
      address: {
        street: `${Math.floor(Math.random() * 9999) + 1} ${["Main", "Oak", "Maple", "Pine", "Elm", "Cedar"][Math.floor(Math.random() * 6)]} ${["St", "Ave", "Blvd", "Dr", "Way"][Math.floor(Math.random() * 5)]}`,
        city: "Springfield",
        state: "IL",
        zipCode: `627${String(Math.floor(Math.random() * 10)).padStart(2, "0")}`,
        country: "USA",
      },
      emergencyContact: {
        name: `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastName}`,
        relationship: ["Spouse", "Parent", "Sibling", "Child", "Friend"][Math.floor(Math.random() * 5)],
        phone: `(555) ${String(Math.floor(Math.random() * 900) + 100)}-${String(
          Math.floor(Math.random() * 9000) + 1000
        )}`,
      },
      insurance,
      tags,
      communicationPreference: ["email", "sms", "phone"][Math.floor(Math.random() * 3)] as "email" | "sms" | "phone",
      status: Math.random() > 0.05 ? "active" : "inactive",
      assignedProvider: mockProviders[Math.floor(Math.random() * mockProviders.length)].id,
      createdAt: new Date(2023, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
      updatedAt: new Date(2024, Math.floor(Math.random() * 11), Math.floor(Math.random() * 28) + 1),
    });
  }

  return patients;
}

export function generateMockAppointments(count: number, patients: Patient[]): Appointment[] {
  const appointments: Appointment[] = [...mockAppointments];
  const types: Appointment["appointmentType"][] = ["consultation", "follow-up", "procedure", "physical-exam"];
  const statuses: Appointment["status"][] = ["scheduled", "confirmed", "checked-in", "completed", "cancelled", "no-show"];
  const rooms = ["Room 101", "Room 102", "Room 103", "Room 104", "Room 105"];
  const reasons = [
    "Annual physical",
    "Follow-up visit",
    "Sick visit",
    "Medication refill",
    "Blood pressure check",
    "Diabetes management",
    "Lab review",
    "Vaccination",
    "Sports physical",
    "Well-child visit",
    "Chronic condition management",
    "New patient visit",
    "Consultation",
  ];

  for (let i = mockAppointments.length; i < count; i++) {
    // Generate appointments across past 1 month and future 2 months
    const date = new Date();
    date.setDate(date.getDate() + Math.floor(Math.random() * 90) - 30);

    const hour = Math.floor(Math.random() * 8) + 9; // 9 AM to 5 PM
    const minute = Math.random() > 0.5 ? "00" : "30";
    const startTime = `${String(hour).padStart(2, "0")}:${minute}`;
    const endTime = `${String(hour).padStart(2, "0")}:${Number(minute) + 30 === 60 ? "00" : String(Number(minute) + 30).padStart(2, "0")}`;

    const patient = patients[Math.floor(Math.random() * patients.length)];
    const provider = mockProviders[Math.floor(Math.random() * mockProviders.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];

    // Past appointments are more likely to be completed
    const isPast = date < new Date();
    const finalStatus = isPast
      ? (Math.random() > 0.2 ? "completed" : (Math.random() > 0.5 ? "no-show" : "cancelled"))
      : status;

    appointments.push({
      id: `apt-${generateId()}`,
      patientId: patient.id,
      patientName: `${patient.firstName} ${patient.lastName}`,
      providerId: provider.id,
      providerName: `Dr. ${provider.firstName} ${provider.lastName}`,
      appointmentType: types[Math.floor(Math.random() * types.length)],
      date,
      startTime,
      endTime,
      duration: 30,
      status: finalStatus,
      reason: reasons[Math.floor(Math.random() * reasons.length)],
      room: rooms[Math.floor(Math.random() * rooms.length)],
      isRecurring: false,
      remindersSent: finalStatus !== "cancelled" ? [
        {
          type: patient.communicationPreference === "sms" ? "sms" : "email",
          sentAt: new Date(date.getTime() - 24 * 60 * 60 * 1000),
          delivered: true,
          opened: Math.random() > 0.3,
        },
      ] : [],
      createdAt: new Date(date.getTime() - 7 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(),
    });
  }

  return appointments.sort((a, b) => a.date.getTime() - b.date.getTime());
}

export function generateMockReferrals(count: number, patients: Patient[]): Referral[] {
  const referrals: Referral[] = [];
  const statuses: Referral["status"][] = ["pending", "sent", "accepted", "declined", "completed", "cancelled"];
  const priorities: Referral["priority"][] = ["routine", "urgent", "stat"];
  const reasons = [
    "Chest pain evaluation",
    "Elevated blood sugar",
    "Joint pain",
    "Skin lesion",
    "Abdominal pain",
    "Shortness of breath",
    "Irregular heartbeat",
    "Specialist consultation",
  ];

  for (let i = 0; i < count; i++) {
    const patient = patients[Math.floor(Math.random() * patients.length)];
    const provider = mockProviders[Math.floor(Math.random() * mockProviders.length)];
    const specialist = mockSpecialists[Math.floor(Math.random() * mockSpecialists.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const createdDate = new Date();
    createdDate.setDate(createdDate.getDate() - Math.floor(Math.random() * 60));

    referrals.push({
      id: `ref-${generateId()}`,
      patientId: patient.id,
      patientName: `${patient.firstName} ${patient.lastName}`,
      referringProviderId: provider.id,
      referringProviderName: `Dr. ${provider.firstName} ${provider.lastName}`,
      specialistId: specialist.id,
      specialistName: `Dr. ${specialist.firstName} ${specialist.lastName}`,
      specialty: specialist.specialty,
      reason: reasons[Math.floor(Math.random() * reasons.length)],
      status,
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      notes: "Please evaluate and advise on treatment options.",
      createdAt: createdDate,
      updatedAt: new Date(),
      sentAt: status !== "pending" ? new Date(createdDate.getTime() + 24 * 60 * 60 * 1000) : undefined,
      completedAt: status === "completed" ? new Date(createdDate.getTime() + 14 * 24 * 60 * 60 * 1000) : undefined,
    });
  }

  return referrals.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
}

export function generateMockClaims(count: number, patients: Patient[]): Claim[] {
  const claims: Claim[] = [];
  const statuses: Claim["status"][] = ["draft", "submitted", "accepted", "rejected", "paid", "appealed"];

  for (let i = 0; i < count; i++) {
    const patient = patients[Math.floor(Math.random() * patients.length)];
    const provider = mockProviders[Math.floor(Math.random() * mockProviders.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const cptCode = cptCodes[Math.floor(Math.random() * cptCodes.length)];
    const icdCode = icd10Codes[Math.floor(Math.random() * icd10Codes.length)];
    const serviceDate = new Date();
    serviceDate.setDate(serviceDate.getDate() - Math.floor(Math.random() * 90));

    const billedAmount = cptCode.fee;
    const allowedAmount = billedAmount * (0.7 + Math.random() * 0.3); // 70-100% of billed
    const paidAmount = status === "paid" ? allowedAmount : 0;
    const patientResponsibility = allowedAmount - paidAmount;

    claims.push({
      id: `claim-${generateId()}`,
      claimNumber: `CLM${String(i + 1).padStart(8, "0")}`,
      patientId: patient.id,
      patientName: `${patient.firstName} ${patient.lastName}`,
      providerId: provider.id,
      providerName: `Dr. ${provider.firstName} ${provider.lastName}`,
      serviceDate,
      submittedDate: status !== "draft" ? new Date(serviceDate.getTime() + 3 * 24 * 60 * 60 * 1000) : undefined,
      status,
      insurancePayer: patient.insurance[0]?.provider || "Self-Pay",
      billedAmount,
      allowedAmount,
      paidAmount,
      patientResponsibility,
      diagnosisCodes: [
        {
          code: icdCode.code,
          description: icdCode.description,
          isPrimary: true,
        },
      ],
      procedureCodes: [
        {
          code: cptCode.code,
          description: cptCode.description,
          quantity: 1,
          unitPrice: cptCode.fee,
        },
      ],
      createdAt: serviceDate,
      updatedAt: new Date(),
    });
  }

  return claims.sort((a, b) => b.serviceDate.getTime() - a.serviceDate.getTime());
}

export function generateMockMessages(count: number, patients: Patient[]): Message[] {
  const messages: Message[] = [];
  const types: Message["type"][] = ["email", "sms", "internal", "automated"];
  const statuses: Message["status"][] = ["sent", "delivered", "read", "failed"];
  const subjects = [
    "Appointment Reminder",
    "Lab Results",
    "Prescription Refill",
    "Follow-up Required",
    "Insurance Information Needed",
    "Payment Received",
    "Appointment Confirmation",
  ];

  for (let i = 0; i < count; i++) {
    const patient = patients[Math.floor(Math.random() * patients.length)];
    const type = types[Math.floor(Math.random() * types.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const sentDate = new Date();
    sentDate.setDate(sentDate.getDate() - Math.floor(Math.random() * 60));

    messages.push({
      id: `msg-${generateId()}`,
      type,
      from: "practice",
      to: patient.id,
      recipientName: `${patient.firstName} ${patient.lastName}`,
      subject: type !== "sms" ? subjects[Math.floor(Math.random() * subjects.length)] : undefined,
      body: "This is a mock message body. In a real system, this would contain the actual message content.",
      status,
      sentAt: sentDate,
      deliveredAt: status !== "failed" ? new Date(sentDate.getTime() + 5 * 60 * 1000) : undefined,
      readAt: status === "read" ? new Date(sentDate.getTime() + 60 * 60 * 1000) : undefined,
      createdAt: sentDate,
      updatedAt: new Date(),
    });
  }

  return messages.sort((a, b) => b.sentAt.getTime() - a.sentAt.getTime());
}

// Pre-generate large datasets
export const allMockPatients = generateMockPatients(50);
export const allMockAppointments = generateMockAppointments(200, allMockPatients);
export const allMockReferrals = generateMockReferrals(30, allMockPatients);
export const allMockClaims = generateMockClaims(100, allMockPatients);
export const allMockMessages = generateMockMessages(150, allMockPatients);
