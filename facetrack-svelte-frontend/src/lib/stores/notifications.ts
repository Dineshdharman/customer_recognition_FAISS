import { writable } from "svelte/store";

export type NotificationType = "info" | "success" | "error" | "warning";

export interface Notification {
  id: number;
  message: string;
  type: NotificationType;
}

export const notifications = writable<Notification[]>([]);

export function showNotification(
  message: string,
  type: NotificationType = "info",
  duration = 4000
) {
  const id = Date.now();
  notifications.update((n) => [...n, { id, message, type }]);

  setTimeout(() => {
    hideNotification(id);
  }, duration);
}

export function hideNotification(id: number) {
  notifications.update((n) =>
    n.filter((notification) => notification.id !== id)
  );
}
