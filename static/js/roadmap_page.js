function cleanAIResponse(text) {
  if (!text) return "";
  return text.replace(/\s+/g, " ").trim();
}

let currentRoadmap = null;
let currentPrompt = "";

function getCsrfToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.cookie.split(";").find((cookie) => cookie.trim().startsWith("csrftoken="))?.split("=")[1] ||
    "";
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
  currentPrompt = prompt;
  container.innerHTML = `<div class="roadmap-loading">Generating roadmap for <b>${prompt}</b>...</div>`;

  try {
    const response = await fetch("/api/generate-roadmap/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken()
      },
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
  currentRoadmap = roadmap;
  container.innerHTML = "";

  const title = document.createElement("h2");
  title.className = "roadmap-title";
  title.textContent = cleanAIResponse(roadmap.roadmap_title);
  container.appendChild(title);

  const saveWrap = document.createElement("div");
  saveWrap.className = "mb-4";
  saveWrap.innerHTML = `
    <button type="button" class="save-toggle-btn" id="saveRoadmapBtn">
      <i class="far fa-bookmark"></i>
      <span data-save-label>Save Roadmap</span>
    </button>
  `;
  container.appendChild(saveWrap);

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

async function toggleRoadmapSave() {
  const saveButton = document.getElementById("saveRoadmapBtn");
  if (!saveButton || !currentRoadmap || !currentPrompt) {
    return;
  }

  saveButton.disabled = true;

  try {
    const response = await fetch("/save/roadmap/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken()
      },
      body: JSON.stringify({ prompt: currentPrompt, roadmap: currentRoadmap })
    });

    if (response.status === 401) {
      window.location.href = "/signin/";
      return;
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Could not save this roadmap.");
    }

    saveButton.classList.toggle("is-saved", data.saved);
    saveButton.innerHTML = `
      <i class="${data.saved ? "fas" : "far"} fa-bookmark"></i>
      <span data-save-label>${data.saved ? "Saved Roadmap" : "Save Roadmap"}</span>
    `;
  } catch (error) {
    console.error("Roadmap save failed:", error);
    alert(error.message || "Could not save this roadmap.");
  } finally {
    saveButton.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const generateButton = document.getElementById("generateRoadmapBtn");

  if (generateButton) {
    generateButton.addEventListener("click", () => generateRoadmap());
  }

  document.querySelectorAll(".roadmap-trigger").forEach(button => {
    button.addEventListener("click", () => generateRoadmap(button.dataset.roadmapTopic));
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("#saveRoadmapBtn")) {
      toggleRoadmapSave();
    }
  });
});
