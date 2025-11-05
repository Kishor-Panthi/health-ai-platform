export interface Claim {
  id: string;
  claimNumber: string;
  patientId: string;
  patientName: string;
  providerId: string;
  providerName: string;
  serviceDate: Date;
  submissionDate: Date;
  insuranceId: string;
  insuranceProvider: string;
  status: ClaimStatus;
  totalAmount: number;
  approvedAmount?: number;
  paidAmount?: number;
  patientResponsibility?: number;
  diagnoses: DiagnosisCode[];
  procedures: ProcedureCode[];
  denialReason?: string;
  appealedAt?: Date;
  settledAt?: Date;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export type ClaimStatus =
  | "draft"
  | "submitted"
  | "pending"
  | "in-review"
  | "approved"
  | "partially-approved"
  | "denied"
  | "appealed"
  | "settled";

export interface DiagnosisCode {
  code: string; // ICD-10 code
  description: string;
  isPrimary: boolean;
}

export interface ProcedureCode {
  code: string; // CPT code
  description: string;
  quantity: number;
  unitPrice: number;
  modifiers?: string[];
}

export interface Payment {
  id: string;
  patientId: string;
  claimId?: string;
  amount: number;
  paymentMethod: PaymentMethod;
  paymentType: "copay" | "deductible" | "coinsurance" | "self-pay" | "refund";
  status: "pending" | "completed" | "failed" | "refunded";
  transactionId?: string;
  date: Date;
  processedBy: string;
  notes?: string;
  createdAt: Date;
}

export type PaymentMethod =
  | "cash"
  | "check"
  | "credit-card"
  | "debit-card"
  | "insurance"
  | "eft"
  | "other";

export interface InsuranceVerification {
  id: string;
  patientId: string;
  insuranceId: string;
  verificationDate: Date;
  verifiedBy: string;
  eligibilityStatus: "active" | "inactive" | "pending";
  coverageDetails: {
    copay?: number;
    deductible?: number;
    deductibleMet?: number;
    outOfPocketMax?: number;
    outOfPocketMet?: number;
    coinsurance?: number;
  };
  benefits: Benefit[];
  limitations?: string[];
  expirationDate?: Date;
  notes?: string;
}

export interface Benefit {
  service: string;
  covered: boolean;
  requiresAuth: boolean;
  copay?: number;
  coinsurance?: number;
  limitations?: string;
}

export interface Statement {
  id: string;
  patientId: string;
  statementNumber: string;
  statementDate: Date;
  dueDate: Date;
  previousBalance: number;
  charges: number;
  payments: number;
  adjustments: number;
  currentBalance: number;
  ageOfAccount: number; // days
  status: "sent" | "overdue" | "paid" | "in-collections";
  lineItems: StatementLineItem[];
}

export interface StatementLineItem {
  date: Date;
  description: string;
  amount: number;
  type: "charge" | "payment" | "adjustment";
}
