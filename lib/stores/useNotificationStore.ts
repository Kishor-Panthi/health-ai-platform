import { create } from "zustand";
import { persist } from "zustand/middleware";
import { cookieStorage } from "@/lib/utils/cookieStorage";

interface NotificationItem {
  id: string;
  type: "appointment" | "message" | "claim" | "referral" | "general";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  link?: string;
}

interface NotificationState {
  notifications: NotificationItem[];
  addNotification: (notification: Omit<NotificationItem, "id" | "timestamp" | "read">) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
}

// Create some initial mock notifications
const initialNotifications: NotificationItem[] = [
  {
    id: "1",
    type: "appointment",
    title: "Upcoming Appointment",
    message: "John Doe has an appointment in 1 hour",
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    read: false,
    link: "/dashboard/appointments",
  },
  {
    id: "2",
    type: "message",
    title: "New Message",
    message: "You have a new message from Jane Smith",
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    read: false,
    link: "/dashboard/communications",
  },
  {
    id: "3",
    type: "claim",
    title: "Claim Approved",
    message: "Claim CLM00000042 has been approved",
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
    read: false,
    link: "/dashboard/billing",
  },
];

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set) => ({
      notifications: initialNotifications,
      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            {
              ...notification,
              id: Math.random().toString(36).substring(2, 11),
              timestamp: new Date(),
              read: false,
            },
            ...state.notifications,
          ],
        })),
      markAsRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
        })),
      markAllAsRead: () =>
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
        })),
      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),
    }),
    {
      name: "notification-storage",
      storage: cookieStorage,
    }
  )
);
