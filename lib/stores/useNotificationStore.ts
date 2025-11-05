import { create } from "zustand";
import { Notification } from "@/lib/types";

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Notification) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  unreadCount: 0,
  addNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: notification.isRead ? state.unreadCount : state.unreadCount + 1,
    })),
  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id && !n.isRead ? { ...n, isRead: true, readAt: new Date() } : n
      ),
      unreadCount: state.notifications.find((n) => n.id === id && !n.isRead)
        ? state.unreadCount - 1
        : state.unreadCount,
    })),
  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        !n.isRead ? { ...n, isRead: true, readAt: new Date() } : n
      ),
      unreadCount: 0,
    })),
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
      unreadCount: state.notifications.find((n) => n.id === id && !n.isRead)
        ? state.unreadCount - 1
        : state.unreadCount,
    })),
}));
