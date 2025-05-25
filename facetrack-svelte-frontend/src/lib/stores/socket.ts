import { io, Socket } from "socket.io-client";
import { writable } from "svelte/store";
import { BACKEND_URL } from "$lib/config";
import { showNotification } from "$lib/stores/notifications";

export interface RecognitionStatus {
  running: boolean;
  scheduled: boolean;
}

export interface RecognitionEvent {
  customer_id: string;
  new: boolean;
}

export const recognitionStatus = writable<RecognitionStatus>({
  running: false,
  scheduled: false,
});
export const lastRecognition = writable<RecognitionEvent | null>(null);

let socket: Socket;

// Function to fetch initial status via API
async function getInitialStatus() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/recognition/status`, {
      headers: { "X-API-KEY": import.meta.env.VITE_API_KEY ?? "" },
    });
    if (response.ok) {
      const data = await response.json();
      recognitionStatus.set(data);
    } else {
      console.error("Failed to fetch initial recognition status");
    }
  } catch (error) {
    console.error("Error fetching initial status:", error);
  }
}

export function initializeSocket() {
  if (typeof window === "undefined" || socket) return; // Prevent server-side or multiple initializations

  socket = io(BACKEND_URL, {
    // You might need withCredentials or extraHeaders if you add more complex auth later
    transports: ["websocket", "polling"], // Ensure websocket is preferred
  });

  socket.on("connect", () => {
    console.log("Socket connected:", socket.id);
    showNotification("Connected to real-time server.", "success");
    getInitialStatus(); // Get status once connected
  });

  socket.on("disconnect", () => {
    console.log("Socket disconnected");
    showNotification("Disconnected from real-time server.", "error");
    recognitionStatus.set({ running: false, scheduled: false }); // Assume stopped on disconnect
  });

  socket.on("rec_status_update", (status: RecognitionStatus) => {
    console.log("Status Update:", status);
    recognitionStatus.set(status);
  });

  socket.on("new_recognition", (data: { results: RecognitionEvent[] }) => {
    console.log("New Recognition:", data);
    if (data.results && data.results.length > 0) {
      lastRecognition.set(data.results[0] || null);
      showNotification(
        `Recognized: ${
          data.results[0]?.new ? "New" : "Existing"
        } - ${data.results[0]?.customer_id.substring(0, 8)}...`,
        "info"
      );
    }
  });

  socket.on("connect_error", (err) => {
    console.error("Socket Connection Error:", err);
    showNotification("Cannot connect to real-time server.", "error");
  });
}
