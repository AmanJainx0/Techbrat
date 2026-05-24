document.addEventListener("DOMContentLoaded", () => {
  const csrfToken =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.cookie.split(";").find((cookie) => cookie.trim().startsWith("csrftoken="))?.split("=")[1] ||
    "";

  function updateProgressSummary(payload) {
    const percentNode = document.querySelector("[data-roadmap-progress-percent]");
    const progressBar = document.querySelector("[data-roadmap-progress-bar]");

    if (percentNode) {
      percentNode.textContent = `${payload.completion_percentage}%`;
    }

    if (progressBar) {
      progressBar.style.width = `${payload.completion_percentage}%`;
      progressBar.setAttribute("aria-valuenow", String(payload.completion_percentage));
    }
  }

  function updateWeeklySummary(payload) {
    const completedNode = document.querySelector("[data-weekly-completed]");
    const targetNode = document.querySelector("[data-weekly-target]");
    const remainingNode = document.querySelector("[data-weekly-remaining]");
    const progressBar = document.querySelector("[data-weekly-progress-bar]");
    const streakDays = document.querySelector("[data-streak-days]");
    const streakHero = document.querySelector("[data-streak-hero]");

    if (completedNode && payload.weekly_completed_steps !== undefined) {
      completedNode.textContent = payload.weekly_completed_steps;
    }
    if (targetNode && payload.weekly_target_steps !== undefined) {
      targetNode.textContent = payload.weekly_target_steps;
    }
    if (remainingNode && payload.weekly_target_steps !== undefined && payload.weekly_completed_steps !== undefined) {
      remainingNode.textContent = Math.max(payload.weekly_target_steps - payload.weekly_completed_steps, 0);
    }
    if (progressBar && payload.weekly_completion_percentage !== undefined) {
      progressBar.style.width = `${payload.weekly_completion_percentage}%`;
      progressBar.setAttribute("aria-valuenow", String(payload.weekly_completion_percentage));
    }
    if (streakDays && payload.streak_days !== undefined) {
      streakDays.textContent = `${payload.streak_days} day${payload.streak_days === 1 ? "" : "s"}`;
    }
    if (streakHero && payload.streak_days !== undefined) {
      streakHero.textContent = payload.streak_days;
    }
  }

  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-roadmap-step-toggle]");
    if (!button) {
      return;
    }

    button.disabled = true;

    try {
      const response = await fetch("/api/roadmap-progress/toggle/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          snapshot_id: button.dataset.snapshotId,
          step_index: button.dataset.stepIndex,
        }),
      });

      if (response.status === 401) {
        window.location.href = "/signin/";
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Could not update step progress.");
      }

      const isCompleted = Boolean(data.completed);
      const card = button.closest("[data-roadmap-step-card]");
      const statusBadge = card?.querySelector("[data-roadmap-step-status]");
      const icon = button.querySelector("i");
      const label = button.querySelector("span");

      button.classList.toggle("btn-success", isCompleted);
      button.classList.toggle("btn-outline-primary", !isCompleted);

      if (icon) {
        icon.className = `fas ${isCompleted ? "fa-check-circle" : "fa-circle"} me-2`;
      }

      if (label) {
        label.textContent = isCompleted ? "Mark as Incomplete" : "Mark as Complete";
      }

      if (statusBadge) {
        statusBadge.className = `badge ${isCompleted ? "text-bg-success" : "text-bg-light text-secondary border"}`;
        statusBadge.textContent = isCompleted ? "Completed" : "Pending";
      }

      updateProgressSummary(data);
      updateWeeklySummary(data);
    } catch (error) {
      alert(error.message || "Could not update step progress.");
    } finally {
      button.disabled = false;
    }
  });

  const weeklyGoalForm = document.getElementById("weeklyGoalForm");
  const weeklyGoalInput = document.getElementById("weeklyGoalInput");

  weeklyGoalForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const targetSteps = weeklyGoalInput?.value?.trim();
    if (!targetSteps) {
      return;
    }

    const submitButton = weeklyGoalForm.querySelector("button[type='submit']");
    if (submitButton) {
      submitButton.disabled = true;
    }

    try {
      const response = await fetch("/api/weekly-goal/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ target_steps: targetSteps }),
      });

      if (response.status === 401) {
        window.location.href = "/signin/";
        return;
      }

      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || "Could not update weekly goal.");
      }

      updateWeeklySummary({
        weekly_completed_steps: data.completed_this_week,
        weekly_target_steps: data.target_steps,
        weekly_completion_percentage: data.completion_percentage,
      });
    } catch (error) {
      alert(error.message || "Could not update weekly goal.");
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
});
