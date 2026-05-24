// ==============================
// Helper Functions (GLOBAL)
// ==============================

function cleanAIResponse(text) {
  if (!text) return "";
  return text.replace(/\s+/g, " ").trim();
}

function formatToList(text) {
  if (!text) return "";
  return text
    .split("\n")
    .map(line => `<p>${line}</p>`)
    .join("");
}

// ==============================
// Generate Roadmap
// ==============================

async function generateRoadmap(topic = null) {
  const inputField = document.getElementById("roadmapInput");
  const container = document.getElementById("roadmap-container");

  const prompt = topic ? topic : inputField.value.trim();

  if (!prompt) {
    alert("❗ Please enter a topic (Example: MERN Roadmap)");
    return;
  }

  inputField.value = prompt;

  container.innerHTML = `
    <div style="color:yellow; font-size:18px;">
      ⏳ Generating roadmap for <b>${prompt}</b>...
    </div>
  `;

  try {
    const response = await fetch("/api/generate-roadmap/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    const text = await response.text();
    console.log("Raw backend response:", text);

    const result = JSON.parse(text);

    if (!result.success) {
      container.innerHTML = `
        <div style="color:red;">
          ❌ ${result.error || "Roadmap generation failed"}
        </div>
      `;
      return;
    }

    displayRoadmap(result.data);

  } catch (error) {
    container.innerHTML = `
      <p style="color:red;">⚠️ Backend not responding</p>
    `;
    console.error(error);
  }
}

// ==============================
// Render Roadmap
// ==============================

function displayRoadmap(roadmap) {
  const container = document.getElementById("roadmap-container");
  container.innerHTML = "";

  const title = document.createElement("h2");
  title.innerText = cleanAIResponse(roadmap.roadmap_title);
  title.style.color = "#00eaff";
  container.appendChild(title);

  roadmap.steps.forEach((step, index) => {
    const stepDiv = document.createElement("div");
    stepDiv.classList.add("roadmap-step");

    stepDiv.innerHTML = `
      <h3>📘 Step ${index + 1}: ${cleanAIResponse(step.title)}</h3>
      ${formatToList(step.description)}
      <ul>
        ${(step.resources || [])
          .map(r => `<li><a href="${r.link}" target="_blank">${cleanAIResponse(r.title)}</a></li>`)
          .join("")}
      </ul>
    `;

    container.appendChild(stepDiv);
  });
}
