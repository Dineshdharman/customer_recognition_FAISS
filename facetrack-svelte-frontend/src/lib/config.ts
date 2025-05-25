// Ensure your .env file is in the root of your SvelteKit project
export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL ?? "http://localhost:5000";
export const API_URL = `${BACKEND_URL}/api`;
export const API_KEY = import.meta.env.VITE_API_KEY ?? "";

if (!API_KEY) {
  console.error(
    "VITE_API_KEY is not set in your .env file! API calls will fail."
  );
  alert("Frontend Error: VITE_API_KEY not set. Check .env and console.");
}
if (!BACKEND_URL || BACKEND_URL === "http://localhost:5000") {
  console.warn(
    "Using default BACKEND_URL. Ensure VITE_BACKEND_URL is set if needed."
  );
}
