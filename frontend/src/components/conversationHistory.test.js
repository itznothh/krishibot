import test from "node:test";
import assert from "node:assert/strict";
import { buildConversationHistory } from "./conversationHistory.js";

test("bounds history and maps bot turns to assistant", () => {
  const messages = Array.from({ length:12 }, (_, index) => ({ role:index % 2 ? "bot" : "user", text:`turn ${index}` }));
  const history = buildConversationHistory(messages);
  assert.equal(history.length, 8);
  assert.equal(history[0].content, "turn 4");
  assert.equal(history.at(-1).role, "assistant");
});

test("removes adjacent duplicate turns, malformed entries and error messages", () => {
  const history = buildConversationHistory([
    { role:"user", text:"I grow tomatoes" },
    { role:"user", text:"I grow tomatoes" },
    { role:"bot", text:"Please share your photo", status:"error" },
    null,
    { role:"bot", text:"What symptoms do you see?" },
  ]);
  assert.deepEqual(history, [
    { role:"user", content:"I grow tomatoes" },
    { role:"assistant", content:"What symptoms do you see?" },
  ]);
});

test("caps each item and total character count", () => {
  const history = buildConversationHistory(Array.from({ length:8 }, (_, i) => ({ role:i % 2 ? "bot" : "user", text:"x".repeat(2000) })));
  assert.ok(history.every(turn => turn.content.length <= 1200));
  assert.ok(history.reduce((total, turn) => total + turn.content.length, 0) <= 4000);
});
