document.addEventListener("DOMContentLoaded", () => {
  const tabsWrapper = document.querySelector(".auth-tabs");
  const newTab = document.getElementById("tab-new");
  const existingTab = document.getElementById("tab-existing");
  const signupPanel = document.getElementById("signup-panel");
  const signinPanel = document.getElementById("signin-panel");

  if (!tabsWrapper || !newTab || !existingTab || !signupPanel || !signinPanel) {
    return;
  }

  function setMode(mode) {
    const isSignin = mode === "signin";

    newTab.classList.toggle("active", !isSignin);
    existingTab.classList.toggle("active", isSignin);
    signupPanel.classList.toggle("d-none", isSignin);
    signinPanel.classList.toggle("d-none", !isSignin);
  }

  setMode(tabsWrapper.dataset.authMode || "signup");

  newTab.addEventListener("click", () => setMode("signup"));
  existingTab.addEventListener("click", () => setMode("signin"));
});
