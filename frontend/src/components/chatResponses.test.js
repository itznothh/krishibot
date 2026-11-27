import test from "node:test";
import assert from "node:assert/strict";
import { formatChatError, mapChatResponse } from "./chatResponses.js";

test("successful weather payload maps to a card without a generic assistant message", () => {
  const weather = {
    city:"Kanija Bhavan", condition:"Clouds", data_type:"current",
    description:"Scattered clouds", humidity:63, temperature:27,
    wind_speed:2.57, source:"OpenWeatherMap",
  };
  const result = mapChatResponse({ status:"weather", data:weather });

  assert.equal(result.text, "");
  assert.equal(result.status, "weather");
  assert.equal(result.data, weather);
  assert.equal(result.data.data_type, "current");
  assert.equal("rain_probability" in result.data, false);
  assert.notEqual(result.text, "I couldn't prepare a response. Please try again.");
});

test("normal text and message-backed chat statuses keep their assistant text", () => {
  assert.deepEqual(mapChatResponse({ status:"ai_response", message:"Check the soil before watering." }), {
    text:"Check the soil before watering.", status:"ai_response", data:undefined,
  });
  assert.equal(mapChatResponse({ status:"needs_location", message:"Please share your location." }).text, "Please share your location.");
  assert.equal(mapChatResponse({ status:"pest_advice", message:"Inspect the underside of the leaves." }).text, "Inspect the underside of the leaves.");
});

test("other supported structured statuses do not gain a text fallback", () => {
  for (const status of ["crop", "fertilizer", "image_analysis"]) {
    const result = mapChatResponse({ status, data:{ result:"structured value" } });
    assert.equal(result.text, "", `${status} should remain a structured response`);
    assert.equal(result.status, status);
  }

  assert.equal(mapChatResponse({ status:"weather", data:{} }).text, "I couldn't prepare a response. Please try again.");
});

test("genuine API failures remain visible as error messages", () => {
  const errorBubble = formatChatError(new Error("Weather service is temporarily unavailable."));
  assert.equal(errorBubble, "Could not get a response: Weather service is temporarily unavailable.");
  assert.match(formatChatError(new Error()), /check your connection and try again/);
});
