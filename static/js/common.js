document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".future-feature").forEach(feature => {
    feature.addEventListener("click", e => {
      e.preventDefault();
      alert("This feature is coming in the future! Stay tuned.");
    });
  });
});

/* ===========================
   SHARED AI RESPONSE HELPERS
   =========================== */

window.cleanAIResponse = function (text) {
  if (!text) return "";
  return text
    .replace(/```[a-z]*/gi, "")
    .replace(/```/g, "")
    .replace(/\*\*/g, "")
    .replace(/###/g, "")
    .replace(/`/g, "")
    .replace(/\r\n/g, "\n")
    .trim();
};

window.formatToList = function (text) {
  if (!text) return "";

  const lines = text
    .split("\n")
    .map(l => l.trim())
    .filter(Boolean);

  if (lines.length === 1) {
    return `<p>${cleanAIResponse(lines[0])}</p>`;
  }

  return `
    <ul>
      ${lines.map(line =>
        `<li>${cleanAIResponse(line.replace(/^[\u2022\-*]\s*/, ""))}</li>`
      ).join("")}
    </ul>
  `;
};
