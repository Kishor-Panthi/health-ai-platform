export interface Provider {
  id: string;
  npi: string;
  firstName: string;
  lastName: string;
  title: string; // MD, DO, NP, PA, etc.
  specialty: string;
  email: string;
  phone: string;
  department?: string;
  photo?: string;
  status: "active" | "inactive" | "on-leave";
  schedule: ProviderScheduleSimple[];
  acceptingNewPatients: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ProviderScheduleSimple {
  dayOfWeek: number; // 0-6
  startTime: string;
  endTime: string;
  location?: string;
}

export interface Staff {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: StaffRole;
  department?: string;
  photo?: string;
  permissions: Permission[];
  status: "active" | "inactive";
  createdAt: Date;
  updatedAt: Date;
}

export type StaffRole =
  | "admin"
  | "receptionist"
  | "nurse"
  | "medical-assistant"
  | "billing-specialist"
  | "practice-manager"
  | "it-support";

export interface Permission {
  resource: string;
  actions: ("read" | "create" | "update" | "delete")[];
}

export interface Practice {
  id: string;
  name: string;
  taxId: string;
  npi: string;
  address: Address;
  phone: string;
  fax?: string;
  email: string;
  website?: string;
  logo?: string;
  primaryColor?: string;
  secondaryColor?: string;
  timezone: string;
  businessHours: BusinessHours[];
  specialties: string[];
  settings: PracticeSettings;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

export interface BusinessHours {
  dayOfWeek: number;
  isOpen: boolean;
  openTime?: string;
  closeTime?: string;
}

export interface PracticeSettings {
  appointmentDuration: number; // default in minutes
  appointmentBuffer: number; // buffer between appointments
  allowOnlineBooking: boolean;
  requireAppointmentConfirmation: boolean;
  sendReminders: boolean;
  reminderTiming: number[]; // days before appointment
  cancelationPolicy: string;
  maxAdvanceBooking: number; // days
  enableWaitlist: boolean;
  enableTelehealth: boolean;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  type: TaskType;
  priority: "low" | "normal" | "high" | "urgent";
  status: "pending" | "in-progress" | "completed" | "cancelled";
  assignedTo: string;
  assignedBy: string;
  relatedTo?: {
    type: "patient" | "appointment" | "claim" | "referral";
    id: string;
  };
  dueDate?: Date;
  completedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export type TaskType =
  | "follow-up"
  | "insurance-verification"
  | "lab-result-review"
  | "prescription-refill"
  | "referral-follow-up"
  | "billing-issue"
  | "documentation"
  | "other";

export interface Analytics {
  date: Date;
  totalAppointments: number;
  completedAppointments: number;
  cancelledAppointments: number;
  noShows: number;
  newPatients: number;
  revenue: number;
  collections: number;
  claimsSubmitted: number;
  claimsDenied: number;
  averageWaitTime: number; // minutes
  patientSatisfaction?: number;
}

export interface AutomationRule {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  trigger: AutomationTrigger;
  conditions: AutomationCondition[];
  actions: AutomationAction[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
  lastRun?: Date;
  executionCount: number;
}

export interface AutomationTrigger {
  type:
    | "appointment-booked"
    | "appointment-completed"
    | "patient-registered"
    | "claim-denied"
    | "no-show"
    | "scheduled-time";
  config?: Record<string, any>;
}

export interface AutomationCondition {
  field: string;
  operator: "equals" | "not-equals" | "contains" | "greater-than" | "less-than";
  value: any;
}

export interface AutomationAction {
  type: "send-message" | "create-task" | "update-status" | "trigger-webhook";
  config: Record<string, any>;
}
