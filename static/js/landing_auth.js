document.addEventListener("DOMContentLoaded", () => {
  const tabsWrapper = document.querySelector(".auth-tabs");
  const newTab = document.getElementById("tab-new");
  const existingTab = document.getElementById("tab-existing");
  const signupPanel = document.getElementById("signup-panel");
  const signinPanel = document.getElementById("signin-panel");
  const authEntry = document.getElementById("auth-entry");

  if (!tabsWrapper || !newTab || !existingTab || !signupPanel || !signinPanel) {
    return;
  }

  function getModeFromLocation() {
    const hash = window.location.hash || "";
    const query = hash.includes("?") ? hash.split("?")[1] : window.location.search.slice(1);
    const params = new URLSearchParams(query);
    return params.get("mode");
  }

  function setMode(mode) {
    const isSignin = mode === "signin";

    newTab.classList.toggle("active", !isSignin);
    existingTab.classList.toggle("active", isSignin);
    signupPanel.classList.toggle("d-none", isSignin);
    signinPanel.classList.toggle("d-none", !isSignin);
  }

  function syncUrl(mode) {
    const url = new URL(window.location.href);
    url.searchParams.set("mode", mode);
    url.hash = "auth-entry";
    window.history.replaceState({}, "", url);
  }

  setMode(getModeFromLocation() || tabsWrapper.dataset.authMode || "signup");

  newTab.addEventListener("click", () => {
    setMode("signup");
    syncUrl("signup");
  });

  existingTab.addEventListener("click", () => {
    setMode("signin");
    syncUrl("signin");
  });

  document.querySelectorAll("[data-auth-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const mode = link.getAttribute("data-auth-link");
      setMode(mode);
      syncUrl(mode);
      authEntry?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
});
