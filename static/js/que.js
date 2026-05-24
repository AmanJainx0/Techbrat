console.log("cleanAIResponse exists:", typeof cleanAIResponse);
console.log("formatToList exists:", typeof formatToList);
console.log("✅ que.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ DOM loaded, que.js active");

  const studentForm = document.getElementById("studentForm");
  const resultsDiv = document.getElementById("results");

  if (!studentForm) {
    console.error("❌ studentForm not found");
    return;
  }

  studentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("✅ Form submitted");

    // UI: loading
    resultsDiv.innerHTML =
      `<p class="text-center text-secondary">Fetching recommendations...</p>`;

    const studentData = {
      education_level: document.getElementById("education_level").value,
      interests: document.getElementById("interests").value,
      skills: document.getElementById("skills").value,
      learning_style: document.getElementById("learning_style").value,
      career_goal: document.getElementById("career_goal").value,
    };

    try {
      const response = await fetch("/api/career-guidance/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector(
            '[name=csrfmiddlewaretoken]'
          ).value,
        },
        body: JSON.stringify(studentData),
      });

      // ALWAYS read text first
      const text = await response.text();
      console.log("📦 Raw backend response:", text);

      let data;
      try {
        data = JSON.parse(text);
      } catch (err) {
        resultsDiv.innerHTML = `
          <p class="text-danger text-center">
            ❌ Server returned invalid JSON
          </p>
          <pre style="white-space:pre-wrap;">${text.slice(0, 300)}</pre>
        `;
        return;
      }

      // Backend-level errors (non-tech, validation, etc.)
      if (!response.ok || data.error) {
        resultsDiv.innerHTML = `
          <p class="text-danger text-center">
            ❌ ${data.error || "Unable to process your request."}
          </p>
        `;
        return;
      }

      // Safety check
      if (!Array.isArray(data.recommended_careers)) {
        resultsDiv.innerHTML = `
          <p class="text-danger text-center">
            ❌ No career recommendations received.
          </p>
        `;
        return;
      }

      // ✅ SUCCESS: render results
      resultsDiv.innerHTML = data.recommended_careers
        .map(
          (career, index) => `
            <div class="card mb-3 p-3 shadow-sm">
              <h4 class="text-primary">
                ${index + 1}. ${cleanAIResponse(career.career_name)}
              </h4>

              <div class="mb-2"><strong>Explanation:</strong></div>
              <div class="mb-3">${formatToList(career.simple_explanation)}</div>

              <div class="mb-2"><strong>Why suitable:</strong></div>
              <div class="mb-3">${formatToList(career.why_suitable)}</div>

              <div class="mb-2"><strong>Future Scope:</strong></div>
              <div class="mb-3">${formatToList(career.future_scope)}</div>

              <div class="mb-2"><strong>Beginner Roadmap:</strong></div>
              <ul class="mb-3">
                ${(career.beginner_roadmap || [])
                  .map(step => `<li>${cleanAIResponse(step)}</li>`)
                  .join("")}
              </ul>

              <div class="mb-2"><strong>Resources:</strong></div>
              <ul>
                ${(career.beginner_resources || [])
                  .map(
                    r => `
                      <li>
                        <a href="${r.link}" target="_blank">
                          ${cleanAIResponse(r.title)}
                        </a> (${cleanAIResponse(r.type)})
                      </li>`
                  )
                  .join("")}
              </ul>
            </div>
          `
        )
        .join("");

    } catch (err) {
      console.error("❌ Fetch failed:", err);
      resultsDiv.innerHTML = `
        <p class="text-danger text-center">
          ⚠️ Network or server error. Please try again.
        </p>
      `;
    }
  });
});
