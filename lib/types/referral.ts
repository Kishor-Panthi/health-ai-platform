export interface Referral {
  id: string;
  referralNumber: string;
  patientId: string;
  patientName: string;
  referringProviderId: string;
  referringProviderName: string;
  specialistId: string;
  specialistName: string;
  specialistPractice: string;
  specialty: string;
  reason: string;
  urgency: "routine" | "urgent" | "emergency";
  status: ReferralStatus;
  referralDate: Date;
  appointmentDate?: Date;
  completedDate?: Date;
  diagnoses: string[];
  attachedDocuments: string[];
  notes?: string;
  feedback?: SpecialistFeedback;
  authorizationRequired: boolean;
  authorizationNumber?: string;
  authorizationDate?: Date;
  insuranceApproved?: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export type ReferralStatus =
  | "pending"
  | "sent"
  | "accepted"
  | "declined"
  | "scheduled"
  | "completed"
  | "cancelled";

export interface SpecialistFeedback {
  receivedAt: Date;
  diagnosis?: string;
  treatment?: string;
  recommendations?: string;
  followUpRequired: boolean;
  attachments?: string[];
}

export interface Specialist {
  id: string;
  firstName: string;
  lastName: string;
  npi: string;
  specialty: string;
  practiceName: string;
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
  };
  phone: string;
  fax?: string;
  email: string;
  acceptsInsurance: string[];
  preferredContactMethod: "fax" | "email" | "phone" | "ehr";
  rating?: number;
  notes?: string;
}
