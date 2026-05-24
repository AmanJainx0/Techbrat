document.addEventListener("DOMContentLoaded", () => {
  const studentForm = document.getElementById("studentForm");
  const resultsDiv = document.getElementById("results");
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || "";

  if (!studentForm || !resultsDiv) {
    return;
  }

  async function toggleCareerSave(button) {
    const rawPayload = button.dataset.careerPayload;
    if (!rawPayload) {
      return;
    }

    button.disabled = true;

    try {
      const response = await fetch("/save/career-path/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          career: JSON.parse(decodeURIComponent(rawPayload)),
        }),
      });

      if (response.status === 401) {
        window.location.href = "/signin/";
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Could not save this career path.");
      }

      button.dataset.saved = data.saved ? "true" : "false";
      button.classList.toggle("is-saved", data.saved);
      button.innerHTML = `
        <i class="${data.saved ? "fas" : "far"} fa-bookmark"></i>
        <span data-save-label>${data.saved ? "Saved Path" : "Save Path"}</span>
      `;
    } catch (error) {
      console.error("Career save failed:", error);
      alert(error.message || "Could not save this career path.");
    } finally {
      button.disabled = false;
    }
  }

  studentForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    resultsDiv.innerHTML = `<p class="text-center text-secondary">Fetching recommendations...</p>`;

    const studentData = {
      education_level: document.getElementById("education_level").value,
      interests: document.getElementById("interests").value,
      math_level: document.getElementById("math_level").value,
      logic_level: document.getElementById("logic_level").value,
      problem_solving: document.getElementById("problem_solving").value,
      skills: document.getElementById("skills").value,
      background: document.getElementById("background").value,
      learning_style: document.getElementById("learning_style").value,
      career_goal: document.getElementById("career_goal").value,
      career_goals: document.getElementById("career_goals").value,
      hours_per_week: document.getElementById("hours_per_week").value,
      timeline: document.getElementById("timeline").value,
      work_preference: document.getElementById("work_preference").value,
      risk_appetite: document.getElementById("risk_appetite").value,
      preferred_work_style: document.getElementById("preferred_work_style").value,
      location_preference: document.getElementById("location_preference").value,
    };

    try {
      const response = await fetch("/api/career-guidance/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(studentData),
      });

      const text = await response.text();
      let data;

      try {
        data = JSON.parse(text);
      } catch (error) {
        resultsDiv.innerHTML = `
          <p class="text-danger text-center">Server returned invalid JSON</p>
          <pre style="white-space:pre-wrap;">${text.slice(0, 300)}</pre>
        `;
        return;
      }

      if (!response.ok || data.error) {
        resultsDiv.innerHTML = `
          <p class="text-danger text-center">${data.error || "Unable to process your request."}</p>
        `;
        return;
      }

      if (!Array.isArray(data.recommended_careers)) {
        resultsDiv.innerHTML = `
          <p class="text-danger text-center">No career recommendations received.</p>
        `;
        return;
      }

      resultsDiv.innerHTML = data.recommended_careers
        .map(
          (career, index) => `
            <div class="card mb-3 p-3 shadow-sm">
              <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
                <h4 class="text-primary mb-0">${index + 1}. ${cleanAIResponse(career.career_name)}</h4>
                <button
                  type="button"
                  class="save-toggle-btn"
                  data-career-payload="${encodeURIComponent(JSON.stringify(career))}"
                  data-saved="false">
                  <i class="far fa-bookmark"></i>
                  <span data-save-label>Save Path</span>
                </button>
              </div>

              <div class="mb-2"><strong>Explanation:</strong></div>
              <div class="mb-3">${formatToList(career.simple_explanation)}</div>

              <div class="mb-2"><strong>Confidence Score:</strong></div>
              <div class="mb-3"><p>${cleanAIResponse(String(career.confidence_score || 0))}%</p></div>

              <div class="mb-2"><strong>Why this fits:</strong></div>
              <div class="mb-3">${formatToList(career.why_suitable)}</div>

              <div class="mb-2"><strong>Alternative Career Path:</strong></div>
              <div class="mb-3"><p>${cleanAIResponse(career.alternative_career_path || "N/A")}</p></div>

              <div class="mb-2"><strong>Future Scope:</strong></div>
              <div class="mb-3">${formatToList(career.future_scope)}</div>

              <div class="mb-2"><strong>Beginner Roadmap:</strong></div>
              <ul class="mb-3">
                ${(career.beginner_roadmap || [])
                  .map((step) => `<li>${cleanAIResponse(step)}</li>`)
                  .join("")}
              </ul>

              <div class="mb-2"><strong>Resources:</strong></div>
              <ul>
                ${(career.beginner_resources || [])
                  .map(
                    (resource) => `
                      <li>
                        <a href="${resource.link}" target="_blank" rel="noopener">
                          ${cleanAIResponse(resource.title)}
                        </a> (${cleanAIResponse(resource.type)})
                      </li>`
                  )
                  .join("")}
              </ul>

              <div class="mb-2 mt-3"><strong>Key Skills:</strong></div>
              <ul>
                ${(career.key_skills || [])
                  .map((skill) => `<li>${cleanAIResponse(skill)}</li>`)
                  .join("")}
              </ul>
            </div>
          `
        )
        .join("");
    } catch (error) {
      console.error("Career guidance request failed:", error);
      resultsDiv.innerHTML = `
        <p class="text-danger text-center">Network or server error. Please try again.</p>
      `;
    }
  });

  resultsDiv.addEventListener("click", (event) => {
    const button = event.target.closest("[data-career-payload]");
    if (!button) {
      return;
    }

    toggleCareerSave(button);
  });
});
