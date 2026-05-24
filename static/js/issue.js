issueForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const issue = document.getElementById("issueDescription").value;

  responseArea.style.display = "block";
  responseContent.innerHTML =
    `<p class="text-center text-secondary">Analyzing your issue...</p>`;

  try {
    const res = await fetch("/api/issue-assistance/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ issue }),
    });

    const text = await res.text(); // ✅ ALWAYS read text first
    console.log("Raw backend response:", text);

    let data;
    try {
      data = JSON.parse(text);
    } catch (err) {
      responseContent.innerHTML = `
        <p class="text-danger text-center">
          ❌ Server returned invalid response.
        </p>
        <pre style="white-space:pre-wrap;">${text.slice(0, 300)}</pre>
      `;
      return;
    }

    // ✅ Backend-level errors (non-tech, validation, etc.)
    if (!res.ok || data.error) {
      responseContent.innerHTML = `
        <p class="text-danger text-center">
          ❌ ${data.error || "Unable to process your request."}
        </p>
      `;
      return;
    }

    // ✅ SUCCESS
    responseContent.innerHTML = `
      <p><strong>Issue Detected:</strong> ${cleanAIResponse(data.issue_detected) || "N/A"}</p>

      <p><strong>Simple Explanation:</strong></p>
      <div class="mb-3">${formatToList(data.simple_explanation)}</div>

      <p><strong>Alternative Learning:</strong></p>
      <div class="mb-3">${formatToList(data.alternative_learning)}</div>

      <p><strong>Practice / Example:</strong></p>
      <div class="mb-3">${formatToList(data.practice_or_example)}</div>

      <p><strong>Motivation Boost:</strong> ${cleanAIResponse(data.motivation_boost) || "N/A"}</p>
    `;

  } catch (err) {
    console.error("Fetch failed:", err);
    responseContent.innerHTML = `
      <p class="text-danger text-center">
        ⚠️ Server unreachable or crashed.
      </p>
    `;
  }
});
