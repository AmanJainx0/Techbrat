document.addEventListener("DOMContentLoaded", () => {
  const csrfToken =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.cookie.split(";").find((cookie) => cookie.trim().startsWith("csrftoken="))?.split("=")[1] ||
    "";

  function updateButton(button, saved) {
    button.dataset.saved = saved ? "true" : "false";
    button.classList.toggle("is-saved", saved);

    const icon = button.querySelector("i");
    const label = button.querySelector("[data-save-label]");

    if (icon) {
      icon.className = saved ? "fas fa-bookmark" : "far fa-bookmark";
    }

    if (label) {
      label.textContent = saved ? "Saved" : "Save";
    }
  }

  function updateSavedCount(count) {
    document.querySelectorAll("[data-saved-count]").forEach((node) => {
      node.textContent = count;
    });
  }

  function ensureSavedEmptyState() {
    const gallery = document.querySelector("[data-saved-gallery]");
    if (!gallery) {
      return;
    }

    const remainingCards = gallery.querySelectorAll("[data-saved-card]");
    if (remainingCards.length > 0) {
      return;
    }

    gallery.innerHTML = `
      <div class="col-12">
        <div class="saved-gallery-card p-5 text-center">
          <h2 class="h4 fw-bold mb-2">No saved items yet</h2>
          <p class="text-muted mb-4">Use the save button on courses, books, tools, tips, or generated plans to build your shortlist.</p>
          <a href="/courses/" class="btn btn-primary">Explore Resources</a>
        </div>
      </div>
    `;
  }

  document.querySelectorAll(".save-toggle-btn").forEach((button) => {
    updateButton(button, button.dataset.saved === "true");
  });

  document.addEventListener("click", async (event) => {
    const button = event.target.closest(".save-toggle-btn");
    if (!button) {
      return;
    }

    event.preventDefault();

    const objectId = button.dataset.objectId;
    const contentType = button.dataset.contentType;

    if (!objectId || !contentType) {
      return;
    }

    button.disabled = true;

    try {
      const response = await fetch("/save/toggle/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          object_id: objectId,
          content_type: contentType,
        }),
      });

      if (response.status === 401) {
        window.location.href = "/signin/";
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Could not update saved state.");
      }

      document
        .querySelectorAll(`.save-toggle-btn[data-content-type="${contentType}"][data-object-id="${objectId}"]`)
        .forEach((matchedButton) => updateButton(matchedButton, data.saved));

      if (typeof data.saved_count === "number") {
        updateSavedCount(data.saved_count);
      }

      if (!data.saved && button.dataset.removeCardOnUnsave === "true") {
        button.closest("[data-saved-card]")?.remove();
        ensureSavedEmptyState();
      }
    } catch (error) {
      console.error("Save toggle failed:", error);
      alert(error.message || "Could not save this item right now.");
    } finally {
      button.disabled = false;
    }
  });
});
