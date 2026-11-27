import test from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { WeatherCard } from "./WeatherCard.js";

const conditions = {
  location:"Farm Town", temperature:0, condition:"Clear", description:"Clear sky",
  humidity:0, wind_speed:0, farming_advice:"Check soil moisture before irrigating.",
  retrieved_at:"2025-01-02T03:04:05+00:00", source:"OpenWeatherMap", data_type:"current",
};

test("renders mapped weather, advice, zero readings and retrieval timestamp", () => {
  const html = renderToStaticMarkup(createElement(WeatherCard, { data:conditions }));
  assert.match(html, /Farm Town/);
  assert.match(html, /Clear sky/);
  assert.match(html, /0°C/);
  assert.match(html, /0% humidity/);
  assert.match(html, /0 m\/s wind/);
  assert.match(html, /Check soil moisture/);
  assert.match(html, /OpenWeatherMap/);
  assert.match(html, /Retrieved/);
  assert.match(html, /Current conditions/);
});

test("labels forecast data distinctly from current conditions", () => {
  const html = renderToStaticMarkup(createElement(WeatherCard, { data:{ ...conditions, data_type:"forecast" } }));
  assert.match(html, /Forecast/);
  assert.match(html, /Forecast conditions/);
});
