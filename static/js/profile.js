document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".profile-completion-bar").forEach(bar => {
    const completion = Number.parseInt(bar.dataset.completion || "0", 10);
    const safeCompletion = Number.isNaN(completion) ? 0 : Math.max(0, Math.min(100, completion));
    bar.style.width = `${safeCompletion}%`;
  });
});
