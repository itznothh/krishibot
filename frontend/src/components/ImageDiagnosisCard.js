import { createElement } from "react";

function ListSection({ title, items }) {
  if (!items?.length) return null;
  return createElement("section", { style:{ marginTop:12 } },
    createElement("h4", { style:{ margin:"0 0 5px", color:"#b5d6a0", fontSize:"0.82rem" } }, title),
    createElement("ul", { style:{ margin:0, paddingLeft:20, color:"rgba(232,240,228,0.82)", fontSize:"0.84rem", lineHeight:1.55 } },
      ...items.map((item, index) => createElement("li", { key:index }, item))));
}

export function ImageDiagnosisCard({ diagnosis }) {
  if (!diagnosis?.success) return null;
  const uncertain = diagnosis.confidence_status === "uncertain" || !diagnosis.suspected_disease;
  const treatment = diagnosis.treatment || {};
  return createElement("div", {
    className:"image-diagnosis-card",
    style:{ ...S.card, ...(uncertain ? S.uncertain : {}) },
    role:"status",
    "aria-label":uncertain ? "Uncertain crop image assessment" : "Crop image assessment",
  },
  createElement("div", { style:S.header },
    createElement("span", { style:{ fontSize:"1.25rem" } }, uncertain ? "⚠️" : "🔬"),
    createElement("div", null,
      createElement("div", { style:S.title }, uncertain ? "Image assessment is uncertain" : "Crop image assessment"),
      createElement("div", { style:S.meta },
        [diagnosis.crop, diagnosis.severity && `Severity: ${diagnosis.severity}`, `Assessment: ${diagnosis.confidence_status || "uncertain"}`].filter(Boolean).join(" · ")))),
  diagnosis.suspected_disease && createElement("p", { style:S.disease }, diagnosis.suspected_disease),
  createElement(ListSection, { title:"Visible symptoms", items:diagnosis.visible_symptoms }),
  createElement(ListSection, { title:"Possible causes", items:diagnosis.possible_causes }),
  createElement(ListSection, { title:"Immediate steps", items:treatment.immediate_steps }),
  createElement(ListSection, { title:"Organic approaches", items:treatment.organic }),
  createElement(ListSection, { title:"Chemical approaches", items:treatment.chemical }),
  createElement(ListSection, { title:"Prevention", items:diagnosis.prevention }),
  createElement(ListSection, { title:"More information that would help", items:diagnosis.additional_information_needed }),
  createElement("p", { style:S.note }, "Image-based guidance is preliminary. Confirm uncertain diagnoses and treatment choices with your local KVK or agricultural officer."));
}

const S = {
  card:{ width:"100%", padding:14, borderRadius:14, border:"1px solid rgba(106,170,122,0.24)", background:"rgba(106,170,122,0.06)" },
  uncertain:{ borderColor:"rgba(244,162,97,0.55)", background:"rgba(244,162,97,0.08)" },
  header:{ display:"flex", alignItems:"flex-start", gap:9 },
  title:{ color:"#b5d6a0", fontWeight:800, fontSize:"0.92rem" },
  meta:{ marginTop:3, color:"rgba(232,240,228,0.5)", fontSize:"0.74rem", textTransform:"capitalize" },
  disease:{ margin:"12px 0 0", color:"#e8f0e4", fontWeight:700, fontSize:"0.96rem" },
  note:{ margin:"14px 0 0", paddingTop:9, borderTop:"1px solid rgba(106,170,122,0.14)", color:"rgba(232,240,228,0.48)", fontSize:"0.74rem", lineHeight:1.5 },
};
