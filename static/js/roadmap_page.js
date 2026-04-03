function cleanAIResponse(text) {
  if (!text) return "";
  return text.replace(/\s+/g, " ").trim();
}

function formatToList(text) {
  if (!text) return "";
  return text
    .split("\n")
    .filter(Boolean)
    .map(line => `<p>${cleanAIResponse(line)}</p>`)
    .join("");
}

async function generateRoadmap(topic = null) {
  const inputField = document.getElementById("roadmapInput");
  const container = document.getElementById("roadmap-container");
  const prompt = topic || inputField.value.trim();

  if (!prompt) {
    alert("Please enter a topic (example: MERN Roadmap).");
    return;
  }

  inputField.value = prompt;
  container.innerHTML = `<div class="roadmap-loading">Generating roadmap for <b>${prompt}</b>...</div>`;

  try {
    const response = await fetch("/api/generate-roadmap/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      container.innerHTML = `<div class="roadmap-error">${result.error || "Roadmap generation failed"}</div>`;
      return;
    }

    displayRoadmap(result.data);
  } catch (error) {
    console.error(error);
    container.innerHTML = `<p class="roadmap-error">Backend not responding</p>`;
  }
}

function displayRoadmap(roadmap) {
  const container = document.getElementById("roadmap-container");
  container.innerHTML = "";

  const title = document.createElement("h2");
  title.className = "roadmap-title";
  title.textContent = cleanAIResponse(roadmap.roadmap_title);
  container.appendChild(title);

  roadmap.steps.forEach((step, index) => {
    const stepDiv = document.createElement("div");
    stepDiv.className = "roadmap-step";
    stepDiv.innerHTML = `
      <h3>Step ${index + 1}: ${cleanAIResponse(step.title)}</h3>
      ${formatToList(step.description)}
      <ul>
        ${(step.resources || [])
          .map(resource => `<li><a href="${resource.link}" target="_blank" rel="noopener noreferrer">${cleanAIResponse(resource.title)}</a></li>`)
          .join("")}
      </ul>
    `;
    container.appendChild(stepDiv);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const generateButton = document.getElementById("generateRoadmapBtn");

  if (generateButton) {
    generateButton.addEventListener("click", () => generateRoadmap());
  }

  document.querySelectorAll(".roadmap-trigger").forEach(button => {
    button.addEventListener("click", () => generateRoadmap(button.dataset.roadmapTopic));
  });
});
