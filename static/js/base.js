document.addEventListener("DOMContentLoaded", () => {
  if (window.AOS) {
    window.AOS.init({ duration: 800, offset: 100 });
  }

  const profileBtn = document.querySelector("[data-profile-toggle]");
  const profileMenu = document.getElementById("profileMenu");

  if (profileBtn && profileMenu) {
    profileBtn.addEventListener("click", event => {
      event.stopPropagation();
      profileMenu.classList.toggle("show");
    });

    document.addEventListener("click", event => {
      if (!profileMenu.contains(event.target) && !profileBtn.contains(event.target)) {
        profileMenu.classList.remove("show");
      }
    });

    document.querySelectorAll(".dropdown-item-custom").forEach(item => {
      item.addEventListener("click", () => {
        profileMenu.classList.remove("show");
      });
    });
  }
});
