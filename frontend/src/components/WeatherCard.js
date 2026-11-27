import { createElement as h } from "react";

export function WeatherCard({ data }) {
  if (!data) return null;
  const retrieved = data.retrieved_at ? new Date(data.retrieved_at) : null;
  const retrievedLabel = retrieved && !Number.isNaN(retrieved.getTime()) ? retrieved.toLocaleString() : "Timestamp unavailable";
  const statStyle = { color:"rgba(232,240,228,0.5)", fontSize:"0.78rem", fontWeight:600 };
  return h("section", {
    className:"weather-card",
    "aria-label":`${data.data_type === "forecast" ? "Forecast" : "Current weather"} for ${data.location || data.city || "your location"}`,
    style:{ background:"rgba(106,170,122,0.06)", border:"1px solid rgba(106,170,122,0.17)", borderRadius:13, padding:"13px 15px", marginTop:4, maxWidth:340 },
  },
  h("div", { style:{ display:"flex", alignItems:"center", gap:10, marginBottom:10 } },
    h("span", { style:{ fontSize:"1.5rem" } }, "🌦️"),
    h("div", { style:{ flex:1 } },
      h("div", { style:{ fontWeight:700, color:"#b5d6a0", fontSize:"0.9rem" } }, data.location || data.city || "Weather"),
      h("div", { style:{ color:"rgba(232,240,228,0.45)", fontSize:"0.76rem" } }, `${data.description || data.condition || ""} · ${data.data_type === "forecast" ? "Forecast conditions" : "Current conditions"}`)),
    data.temperature !== null && data.temperature !== undefined && h("div", { style:{ fontFamily:"'Sora',sans-serif", fontSize:"1.5rem", fontWeight:800, color:"#6aaa7a" } }, `${Math.round(data.temperature)}°C`)),
  (data.humidity !== null && data.humidity !== undefined || data.wind_speed !== null && data.wind_speed !== undefined) && h("div", { style:{ display:"flex", gap:16, borderTop:"1px solid rgba(106,170,122,0.15)", paddingTop:10 } },
    data.humidity !== null && data.humidity !== undefined && h("span", { style:statStyle }, `💧 ${data.humidity}% humidity`),
    data.wind_speed !== null && data.wind_speed !== undefined && h("span", { style:statStyle }, `💨 ${data.wind_speed} m/s wind`)),
  data.farming_advice && h("div", { "data-testid":"weather-advisory", style:{ marginTop:11, color:"rgba(232,240,228,0.82)", fontSize:"0.82rem", lineHeight:1.55 } },
    h("strong", { style:{ color:"#b5d6a0" } }, "Farming advisory: "), data.farming_advice),
  h("div", { style:{ marginTop:8, color:"rgba(232,240,228,0.42)", fontSize:"0.68rem" } }, `${data.data_type === "forecast" ? "Forecast" : "Current weather"} · ${data.source || "Weather source unavailable"} · Retrieved ${retrievedLabel}`));
}
