const MAX_MESSAGES = 8;
const MAX_ITEM_CHARS = 1200;
const MAX_TOTAL_CHARS = 4000;

export function buildConversationHistory(messages) {
  if (!Array.isArray(messages)) return [];
  const normalized = [];
  for (const message of messages) {
    if (!message || !["user", "bot"].includes(message.role) || message.status === "error" || typeof message.text !== "string" || !message.text.trim()) continue;
    const entry = {
      role:message.role === "bot" ? "assistant" : "user",
      content:message.text.trim().slice(-MAX_ITEM_CHARS),
    };
    if (normalized.length && normalized[normalized.length - 1].role === entry.role && normalized[normalized.length - 1].content === entry.content) continue;
    normalized.push(entry);
  }
  let total = 0;
  const bounded = [];
  for (const entry of normalized.slice(-MAX_MESSAGES).reverse()) {
    const remaining = MAX_TOTAL_CHARS - total;
    if (!remaining) break;
    const content = entry.content.slice(-Math.min(MAX_ITEM_CHARS, remaining));
    bounded.push({ role:entry.role, content });
    total += content.length;
  }
  return bounded.reverse();
}
