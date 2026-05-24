document.addEventListener("DOMContentLoaded", () => {
  const issueForm = document.getElementById("issueForm");
  const issueDescription = document.getElementById("issueDescription");
  const responseArea = document.getElementById("responseArea");
  const responseContent = document.getElementById("responseContent");
  const csrfToken =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.cookie.split(";").find((cookie) => cookie.trim().startsWith("csrftoken="))?.split("=")[1] ||
    "";
  let lastIssue = "";
  let lastGuidance = null;

  if (!issueForm || !issueDescription || !responseArea || !responseContent) {
    return;
  }

  issueForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const issue = issueDescription.value.trim();

    responseArea.classList.remove("d-none");

    if (!issue) {
      responseContent.innerHTML = `
        <p class="text-danger text-center">
          Please describe the issue you want help with.
        </p>
      `;
      return;
    }

    responseContent.innerHTML = `
      <p class="text-center text-secondary">Analyzing your issue...</p>
    `;

    try {
      const response = await fetch("/api/issue-assistance/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ issue }),
      });

      const text = await response.text();
      let data;

      try {
        data = JSON.parse(text);
      } catch (error) {
        responseContent.innerHTML = `
          <p class="text-danger text-center">
            Server returned an invalid response.
          </p>
          <pre class="issue-debug-pre">${text.slice(0, 300)}</pre>
        `;
        return;
      }

      if (!response.ok || data.error) {
        responseContent.innerHTML = `
          <p class="text-danger text-center">
            ${cleanAIResponse(data.error || "Unable to process your request.")}
          </p>
        `;
        return;
      }

      lastIssue = issue;
      lastGuidance = data;
      responseContent.innerHTML = `
        <div class="d-flex justify-content-end mb-3">
          <button type="button" class="save-toggle-btn" id="saveIssueBtn">
            <i class="far fa-bookmark"></i>
            <span data-save-label>Save Guidance</span>
          </button>
        </div>
        <p><strong>Issue Detected:</strong> ${cleanAIResponse(data.issue_detected) || "N/A"}</p>

        <p><strong>Simple Explanation:</strong></p>
        <div class="mb-3">${formatToList(data.simple_explanation)}</div>

        <p><strong>Alternative Learning:</strong></p>
        <div class="mb-3">${formatToList(data.alternative_learning)}</div>

        <p><strong>Practice / Example:</strong></p>
        <div class="mb-3">${formatToList(data.practice_or_example)}</div>

        <p><strong>Motivation Boost:</strong> ${cleanAIResponse(data.motivation_boost) || "N/A"}</p>
      `;
    } catch (error) {
      console.error("Issue assistance request failed:", error);
      responseContent.innerHTML = `
        <p class="text-danger text-center">
          Server unreachable or the request failed. Please try again.
        </p>
      `;
    }
  });

  responseContent.addEventListener("click", async (event) => {
    const saveButton = event.target.closest("#saveIssueBtn");
    if (!saveButton || !lastIssue || !lastGuidance) {
      return;
    }

    saveButton.disabled = true;

    try {
      const response = await fetch("/save/issue-assistance/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          issue: lastIssue,
          guidance: lastGuidance,
        }),
      });

      if (response.status === 401) {
        window.location.href = "/signin/";
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Could not save this guidance.");
      }

      saveButton.classList.toggle("is-saved", data.saved);
      saveButton.innerHTML = `
        <i class="${data.saved ? "fas" : "far"} fa-bookmark"></i>
        <span data-save-label>${data.saved ? "Saved Guidance" : "Save Guidance"}</span>
      `;
    } catch (error) {
      console.error("Issue guidance save failed:", error);
      alert(error.message || "Could not save this guidance.");
    } finally {
      saveButton.disabled = false;
    }
  });
});
