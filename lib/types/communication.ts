export interface Message {
  id: string;
  threadId?: string;
  patientId: string;
  patientName: string;
  senderId: string;
  senderName: string;
  senderType: "patient" | "provider" | "staff" | "system";
  recipientId: string;
  recipientName: string;
  recipientType: "patient" | "provider" | "staff";
  type: MessageType;
  subject?: string;
  content: string;
  status: MessageStatus;
  priority: "low" | "normal" | "high" | "urgent";
  sentAt: Date;
  deliveredAt?: Date;
  readAt?: Date;
  attachments?: Attachment[];
  metadata?: Record<string, any>;
  createdAt: Date;
}

export type MessageType =
  | "email"
  | "sms"
  | "portal"
  | "internal"
  | "automated";

export type MessageStatus =
  | "draft"
  | "queued"
  | "sent"
  | "delivered"
  | "read"
  | "failed"
  | "bounced";

export interface Attachment {
  id: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
  url: string;
}

export interface MessageTemplate {
  id: string;
  name: string;
  category: TemplateCategory;
  type: MessageType;
  subject?: string;
  content: string;
  variables: string[];
  isActive: boolean;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export type TemplateCategory =
  | "appointment-reminder"
  | "appointment-confirmation"
  | "appointment-cancellation"
  | "follow-up"
  | "preventive-care"
  | "lab-results"
  | "billing"
  | "general"
  | "emergency";

export interface AutomatedReminder {
  id: string;
  patientId: string;
  appointmentId?: string;
  type: "appointment" | "medication" | "follow-up" | "preventive-care" | "birthday";
  templateId: string;
  scheduledFor: Date;
  sentAt?: Date;
  status: "scheduled" | "sent" | "failed" | "cancelled";
  channel: MessageType;
  retry?: number;
  createdAt: Date;
}

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  priority: "low" | "normal" | "high" | "urgent";
  isRead: boolean;
  readAt?: Date;
  actionUrl?: string;
  actionLabel?: string;
  relatedId?: string;
  relatedType?: string;
  createdAt: Date;
}

export type NotificationType =
  | "appointment"
  | "patient"
  | "claim"
  | "referral"
  | "task"
  | "system"
  | "alert";

export interface CommunicationLog {
  id: string;
  patientId: string;
  type: MessageType;
  direction: "inbound" | "outbound";
  subject?: string;
  summary: string;
  timestamp: Date;
  initiatedBy: string;
  duration?: number; // for phone calls
  outcome?: string;
}
