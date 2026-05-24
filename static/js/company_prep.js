document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("companyPrepForm");
  const resultContainer = document.getElementById("result-container");
  const submitButton = document.getElementById("companyPrepSubmitBtn");
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  let lastPayload = null;
  let lastPlanText = "";

  if (!form || !resultContainer || !submitButton) {
    return;
  }

  function renderSections(text) {
    const sections = text
      .split(/\n\s*\n/)
      .map((section) => section.trim())
      .filter(Boolean);

    return sections
      .map((section) => {
        const lines = section.split("\n").map((line) => line.trim()).filter(Boolean);
        const heading = lines.shift() || "Plan";
        const items = lines
          .map((line) => `<li>${line.replace(/^-+\s*/, "")}</li>`)
          .join("");

        return `
          <div class="mb-4">
            <h4 class="text-primary mb-3">${heading}</h4>
            <ul class="ps-3 mb-0">${items}</ul>
          </div>
        `;
      })
      .join("");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      company: document.getElementById("company").value,
      role: document.getElementById("role").value,
      experience_level: document.getElementById("experience_level").value,
      skills: document.getElementById("skills").value,
      strong_areas: document.getElementById("strong_areas").value,
      weak_areas: document.getElementById("weak_areas").value,
      hours_per_day: document.getElementById("hours_per_day").value,
      total_time: document.getElementById("total_time").value,
      current_status: document.getElementById("current_status").value,
      target_package: document.getElementById("target_package").value,
    };

    submitButton.disabled = true;
    resultContainer.innerHTML = `
      <div class="text-center py-5 text-secondary">
        Generating your preparation plan...
      </div>
    `;

    try {
      const response = await fetch("/company-prep/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Unable to generate the preparation plan.");
      }

      lastPayload = payload;
      lastPlanText = data.data;
      resultContainer.innerHTML = renderSections(data.data);
      resultContainer.insertAdjacentHTML(
        "afterbegin",
        `
          <div class="d-flex justify-content-end mb-4">
            <button type="button" class="save-toggle-btn" id="saveCompanyPrepBtn">
              <i class="far fa-bookmark"></i>
              <span data-save-label>Save Plan</span>
            </button>
          </div>
        `
      );
    } catch (error) {
      resultContainer.innerHTML = `
        <div class="alert alert-danger mb-0">${error.message}</div>
      `;
    } finally {
      submitButton.disabled = false;
    }
  });

  resultContainer.addEventListener("click", async (event) => {
    const saveButton = event.target.closest("#saveCompanyPrepBtn");
    if (!saveButton || !lastPayload || !lastPlanText) {
      return;
    }

    saveButton.disabled = true;

    try {
      const response = await fetch("/save/company-prep/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          company: lastPayload.company,
          role: lastPayload.role,
          prep_inputs: lastPayload,
          plan_text: lastPlanText,
        }),
      });

      if (response.status === 401) {
        window.location.href = "/signin/";
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Could not save this plan.");
      }

      saveButton.classList.toggle("is-saved", data.saved);
      saveButton.innerHTML = `
        <i class="${data.saved ? "fas" : "far"} fa-bookmark"></i>
        <span data-save-label>${data.saved ? "Saved Plan" : "Save Plan"}</span>
      `;
    } catch (error) {
      alert(error.message || "Could not save this plan.");
    } finally {
      saveButton.disabled = false;
    }
  });
});
