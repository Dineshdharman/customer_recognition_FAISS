import { API_URL, API_KEY } from "$lib/config";
import { showNotification } from "$lib/stores/notifications";

export async function apiCall(
  endpoint: string,
  method = "GET",
  body: object | null = null
): Promise<any | null> {
  try {
    const options: RequestInit = {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY,
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_URL}${endpoint}`, options);
    const data = await response.json(); // Always try to parse JSON

    if (!response.ok) {
      const errorMessage =
        data.error ||
        data.message ||
        `Server error! Status: ${response.status}`;
      showNotification(errorMessage, "error");
      console.error("API Error Response:", data);
      return null;
    }
    return data;
  } catch (error) {
    console.error(`API Call Error (${endpoint}):`, error);
    if (error instanceof SyntaxError) {
      showNotification(
        "Failed to process server response (Not Found or Server Error).",
        "error"
      );
    } else {
      showNotification("Network or server connection error.", "error");
    }
    return null;
  }
}

// Specific API call functions
export const fetchDashboardStats = () => apiCall("/dashboard/stats");
export const fetchVisitTrend = () => apiCall("/dashboard/visit-trend");
export const fetchTopVisitors = () => apiCall("/dashboard/top-visitors");
export const fetchRecStatus = () => apiCall("/recognition/status");
export const startRecognition = (startTime?: string, endTime?: string) =>
  apiCall(
    "/recognition/start",
    "POST",
    startTime ? { start_time: startTime, end_time: endTime } : {}
  );
export const stopRecognition = () => apiCall("/recognition/stop", "POST");
export const postChatMessage = (question: string) =>
  apiCall("/chat", "POST", { question });
export const generateReport = (startDate: string, endDate: string) =>
  apiCall("/reports/generate", "POST", {
    start_date: startDate,
    end_date: endDate,
  });
