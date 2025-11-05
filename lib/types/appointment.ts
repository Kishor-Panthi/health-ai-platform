export interface Appointment {
  id: string;
  patientId: string;
  patientName: string;
  providerId: string;
  providerName: string;
  appointmentType: AppointmentType;
  date: Date;
  startTime: string;
  endTime: string;
  duration: number; // in minutes
  status: AppointmentStatus;
  reason: string;
  notes?: string;
  room?: string;
  isRecurring: boolean;
  recurringDetails?: RecurringDetails;
  checkedInAt?: Date;
  completedAt?: Date;
  cancelledAt?: Date;
  cancellationReason?: string;
  remindersSent: ReminderStatus[];
  createdAt: Date;
  updatedAt: Date;
}

export type AppointmentType =
  | "consultation"
  | "follow-up"
  | "procedure"
  | "physical-exam"
  | "lab-work"
  | "imaging"
  | "vaccination"
  | "therapy"
  | "telehealth"
  | "urgent-care";

export type AppointmentStatus =
  | "scheduled"
  | "confirmed"
  | "checked-in"
  | "in-progress"
  | "completed"
  | "cancelled"
  | "no-show"
  | "rescheduled";

export interface RecurringDetails {
  frequency: "daily" | "weekly" | "bi-weekly" | "monthly";
  interval: number;
  endDate?: Date;
  occurrences?: number;
  daysOfWeek?: number[]; // 0-6, where 0 is Sunday
  seriesId: string;
}

export interface ReminderStatus {
  type: "email" | "sms" | "phone";
  sentAt: Date;
  delivered: boolean;
  opened?: boolean;
}

export interface TimeSlot {
  start: Date;
  end: Date;
  available: boolean;
  providerId: string;
  room?: string;
}

export interface ProviderSchedule {
  providerId: string;
  dayOfWeek: number; // 0-6
  startTime: string; // HH:mm format
  endTime: string;
  breakTimes?: BreakTime[];
  isAvailable: boolean;
}

export interface BreakTime {
  startTime: string;
  endTime: string;
  reason?: string;
}

export interface WaitlistEntry {
  id: string;
  patientId: string;
  patientName: string;
  providerId: string;
  appointmentType: AppointmentType;
  preferredDates: Date[];
  preferredTimes: string[];
  priority: "low" | "medium" | "high" | "urgent";
  reason: string;
  addedAt: Date;
  notifiedAt?: Date;
}
