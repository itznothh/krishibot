"""Shared bounds and normalization for short-lived chat context."""

MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_ITEM_CHARS = 1200
MAX_HISTORY_TOTAL_CHARS = 4000


def normalize_history(history, current_message=None):
    if not isinstance(history, list):
        return []
    normalized = []
    for entry in history:
        if not isinstance(entry, dict) or entry.get("role") not in ("user", "assistant"):
            continue
        content = entry.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        content = content.strip()[-MAX_HISTORY_ITEM_CHARS:]
        if normalized and normalized[-1] == {"role": entry["role"], "content": content}:
            continue
        normalized.append({"role": entry["role"], "content": content})

    # Older clients may include the current user turn in history as well as
    # sending it separately. Drop that final duplicate to avoid double context.
    if current_message and normalized and normalized[-1] == {"role": "user", "content": current_message.strip()[-MAX_HISTORY_ITEM_CHARS:]}:
        normalized.pop()

    bounded = []
    total = 0
    for entry in reversed(normalized[-MAX_HISTORY_MESSAGES:]):
        remaining = MAX_HISTORY_TOTAL_CHARS - total
        if remaining <= 0:
            break
        content = entry["content"][-min(MAX_HISTORY_ITEM_CHARS, remaining):]
        bounded.append({"role": entry["role"], "content": content})
        total += len(content)
    return list(reversed(bounded))
