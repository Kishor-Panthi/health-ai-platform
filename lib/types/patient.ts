export interface Patient {
  id: string;
  mrn: string; // Medical Record Number
  firstName: string;
  lastName: string;
  dateOfBirth: Date;
  gender: "male" | "female" | "other" | "prefer-not-to-say";
  email: string;
  phone: string;
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  emergencyContact: {
    name: string;
    relationship: string;
    phone: string;
  };
  insurance: InsuranceInfo[];
  tags: string[];
  communicationPreference: "email" | "sms" | "phone" | "portal";
  status: "active" | "inactive" | "deceased";
  assignedProvider: string; // Provider ID
  createdAt: Date;
  updatedAt: Date;
}

export interface InsuranceInfo {
  id: string;
  provider: string;
  policyNumber: string;
  groupNumber: string;
  subscriberName: string;
  subscriberRelationship: string;
  isPrimary: boolean;
  effectiveDate: Date;
  expirationDate?: Date;
  status: "active" | "inactive" | "pending";
  verifiedAt?: Date;
}

export interface MedicalHistory {
  id: string;
  patientId: string;
  allergies: Allergy[];
  medications: Medication[];
  conditions: Condition[];
  surgeries: Surgery[];
  familyHistory: FamilyHistory[];
  socialHistory: SocialHistory;
  immunizations: Immunization[];
}

export interface Allergy {
  id: string;
  allergen: string;
  reaction: string;
  severity: "mild" | "moderate" | "severe";
  onsetDate?: Date;
  notes?: string;
}

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  startDate: Date;
  endDate?: Date;
  prescribedBy: string;
  status: "active" | "discontinued" | "completed";
  notes?: string;
}

export interface Condition {
  id: string;
  name: string;
  icdCode: string;
  diagnosedDate: Date;
  status: "active" | "resolved" | "chronic";
  notes?: string;
}

export interface Surgery {
  id: string;
  procedure: string;
  date: Date;
  surgeon: string;
  hospital: string;
  notes?: string;
}

export interface FamilyHistory {
  id: string;
  relationship: string;
  condition: string;
  ageOfOnset?: number;
  notes?: string;
}

export interface SocialHistory {
  smokingStatus: "never" | "former" | "current";
  alcoholUse: "none" | "occasional" | "moderate" | "heavy";
  drugUse: "none" | "former" | "current";
  occupation: string;
  maritalStatus: string;
  livingArrangement: string;
}

export interface Immunization {
  id: string;
  vaccine: string;
  date: Date;
  administeredBy: string;
  lotNumber?: string;
  expirationDate?: Date;
  site?: string;
  route?: string;
}
