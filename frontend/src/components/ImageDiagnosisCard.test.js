import test from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ImageDiagnosisCard } from "./ImageDiagnosisCard.js";

const base = {
  success:true,
  crop:"Tomato",
  visible_symptoms:["Small brown leaf spots"],
  suspected_disease:"Possible early blight",
  severity:"Mild",
  confidence_status:"moderate",
  possible_causes:["Fungal infection"],
  treatment:{ chemical:["Consult a local officer before chemical treatment"], organic:["Remove badly affected leaves"], immediate_steps:["Photograph both sides of a leaf"] },
  prevention:["Avoid wetting foliage"],
  additional_information_needed:[],
};

test("renders a successful structured diagnosis in readable sections", () => {
  const markup = renderToStaticMarkup(createElement(ImageDiagnosisCard, { diagnosis:base }));
  assert.match(markup, /Crop image assessment/);
  assert.match(markup, /Possible early blight/);
  assert.match(markup, /Small brown leaf spots/);
  assert.match(markup, /Organic approaches/);
  assert.match(markup, /Image-based guidance is preliminary/);
});

test("visually distinguishes an uncertain diagnosis and shows requested details", () => {
  const diagnosis = {
    ...base,
    suspected_disease:null,
    confidence_status:"uncertain",
    severity:null,
    additional_information_needed:["Send a closer photo of the leaf underside"],
  };
  const markup = renderToStaticMarkup(createElement(ImageDiagnosisCard, { diagnosis }));
  assert.match(markup, /Image assessment is uncertain/);
  assert.match(markup, /Uncertain crop image assessment/);
  assert.match(markup, /Send a closer photo of the leaf underside/);
});
