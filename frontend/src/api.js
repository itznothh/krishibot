const configuredBackend = import.meta.env.VITE_BACKEND_URL || "https://krishibot-api.onrender.com";

export const BACKEND = configuredBackend.replace(/\/$/, "");

export async function readApiResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || data.error || `Request failed (${response.status})`);
  return data;
}
