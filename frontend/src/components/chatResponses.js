const RESPONSE_FALLBACK = "I couldn't prepare a response. Please try again.";
const STRUCTURED_STATUSES = new Set(["weather", "crop", "fertilizer", "image_analysis"]);

function isStructuredPayload(value) {
  return value !== null
    && typeof value === "object"
    && !Array.isArray(value)
    && Object.keys(value).length > 0;
}

/** Convert the Flask chat envelope into renderable message fields. */
export function mapChatResponse(response) {
  const status = typeof response?.status === "string" ? response.status : undefined;
  const message = typeof response?.message === "string" ? response.message : "";
  const data = response?.data;
  const hasStructuredResult = STRUCTURED_STATUSES.has(status) && isStructuredPayload(data);

  return {
    text: message.trim() ? message : hasStructuredResult ? "" : RESPONSE_FALLBACK,
    status,
    data,
  };
}

export function formatChatError(error) {
  const reason = (error?.message || "check your connection and try again").trim().replace(/[.!?]+$/, "");
  return `Could not get a response: ${reason}.`;
}
