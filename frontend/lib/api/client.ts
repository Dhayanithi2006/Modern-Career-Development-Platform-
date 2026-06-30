import { useAuthStore } from "@/stores/auth-store";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (typeof window !== "undefined"
    ? `http://${window.location.hostname}:8000/api/v1`
    : "http://localhost:8000/api/v1");

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const requestId = Date.now();

  try {
    const token = useAuthStore.getState().accessToken;

    const headers = new Headers(options.headers);

    if (
      !headers.has("Content-Type") &&
      !(options.body instanceof FormData)
    ) {
      headers.set("Content-Type", "application/json");
    }

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const url = `${API_BASE_URL}${path}`;

    console.log("");
    console.log("======================================");
    console.log(`REQUEST ID: ${requestId}`);
    console.log("API REQUEST START");
    console.log("URL:", url);
    console.log("METHOD:", options.method || "GET");
    console.log("TOKEN:", token ? "Present" : "Missing");
    console.log("HEADERS:", Object.fromEntries(headers.entries()));

    if (options.body) {
      console.log("BODY:", options.body);
    }

    console.log("======================================");

    const startTime = performance.now();

    const response = await fetch(url, {
      ...options,
      headers,
    });

    const endTime = performance.now();

    console.log("");
    console.log("======================================");
    console.log(`REQUEST ID: ${requestId}`);
    console.log("API RESPONSE RECEIVED");
    console.log("STATUS:", response.status);
    console.log("STATUS TEXT:", response.statusText);
    console.log("OK:", response.ok);
    console.log("TIME:", `${Math.round(endTime - startTime)} ms`);
    console.log("======================================");

    const responseText = await response.text();

    console.log("");
    console.log("RESPONSE BODY:");
    console.log(responseText);
    console.log("======================================");

    if (!response.ok) {
      if (response.status === 401) {
        useAuthStore.getState().logout();
        if (typeof window !== "undefined") {
          window.location.href = "/auth/login";
        }
      }
      throw new Error(
        `HTTP ${response.status}\n${responseText}`
      );
    }

    if (!responseText.trim()) {
      return {} as T;
    }

    try {
      return JSON.parse(responseText) as T;
    } catch (jsonError) {
      console.error("JSON PARSE ERROR");
      console.error(jsonError);
      console.error("RAW RESPONSE:");
      console.log(responseText);
      throw jsonError;
    }

  } catch (error: any) {
    console.log("");
    console.log("======================================");
    console.log(`REQUEST ID: ${requestId}`);
    console.log("FETCH FAILED");
    console.log("======================================");

    console.warn("ERROR OBJECT:");
    console.warn(error);

    console.warn("NAME:", error?.name);
    console.warn("MESSAGE:", error?.message);

    if (error instanceof TypeError) {
      console.warn("POSSIBLE CAUSES: Backend down, CORS, or Network issue.");
    }

    throw error;
  }
}