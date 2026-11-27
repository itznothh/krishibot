import { createElement } from "react";

function renderInline(text) {
  return text.split(/(\*\*.*?\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return createElement("strong", { key:index, style:{ color:"#b5d6a0" } }, part.slice(2, -2));
    }
    return part;
  });
}

export function SafeMarkdown({ text }) {
  const lines = String(text ?? "").split("\n");
  return createElement("div", null, lines.map((line, index) => {
    if (!line) return createElement("br", { key:index });
    if (line.startsWith("- ")) {
      return createElement("div", {
        key:index,
        style:{ display:"flex", gap:8, margin:"4px 0" },
      },
      createElement("span", { style:{ color:"#6aaa7a" } }, "•"),
      createElement("span", null, ...renderInline(line.slice(2))));
    }
    return createElement("div", { key:index }, ...renderInline(line));
  }));
}
