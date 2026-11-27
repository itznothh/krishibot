import test from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { SafeMarkdown } from "./SafeMarkdown.js";

test("renders formatting while treating generated HTML as text", () => {
  const content = '<img src=x onerror="alert(1)">\n<script>alert(1)</script>\n**PM-KISAN**\n- Check eligibility';
  const markup = renderToStaticMarkup(createElement(SafeMarkdown, { text:content }));

  assert.match(markup, /&lt;img src=x onerror=/);
  assert.match(markup, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.doesNotMatch(markup, /<img\b|<script\b|<[^>]+\bonerror\s*=/i);
  assert.match(markup, /<strong[^>]*>PM-KISAN<\/strong>/);
  assert.match(markup, /Check eligibility/);
});
