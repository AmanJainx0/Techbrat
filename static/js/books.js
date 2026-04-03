// Books page client logic
const pageData = document.getElementById("booksPageData");
const aiSection = document.getElementById("aiBooks");
const filteredSection = document.getElementById("filteredBooks");
const errorBox = document.getElementById("bookError");
const userLevel = pageData?.dataset.userLevel || "";
const userGoal = pageData?.dataset.userGoal || "";

let userDomains = [];
try {
  userDomains = JSON.parse(pageData?.dataset.userDomains || "[]");
} catch (error) {
  userDomains = [];
}

function cardHtml(b) {
  const aiBadge = b.is_ai_generated
    ? `<span class="badge bg-light text-primary mb-2"><i class="fas fa-magic me-1"></i>AI Recommended</span>`
    : "";

  return `
    <div class="col-md-6 col-lg-4">
      <div class="card book-card h-100 border-0 shadow-sm p-4">
        <div class="card-body d-flex flex-column p-0">
          ${aiBadge}
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="fw-bold text-primary mb-0">${b.title}</h5>
            <span class="badge bg-light text-secondary border small">${b.level || "Any"}</span>
          </div>
          <p class="text-dark fw-semibold mb-2">${b.author}</p>
          <p class="text-secondary small flex-grow-1 mb-3">${b.description || "No description available."}</p>
          <div class="d-flex gap-2 flex-wrap mb-3">
            <span class="badge bg-info-subtle text-info border border-info-subtle">${b.domain || "General"}</span>
            <span class="badge bg-success-subtle text-success border border-success-subtle">${b.book_type || "Book"}</span>
          </div>
          <a href="${b.link}" target="_blank" class="btn btn-success mt-auto w-100" style="border-radius: 8px;">
            View Book <i class="fas fa-external-link-alt ms-1" style="font-size: 0.75rem;"></i>
          </a>
        </div>
      </div>
    </div>`;
}

function showError(msg) {
  errorBox.classList.remove("d-none");
  errorBox.textContent = msg;
}

function clearError() {
  errorBox.classList.add("d-none");
  errorBox.textContent = "";
}

async function fetchAI() {
  clearError();
  aiSection.innerHTML = `<div class="col-12 text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>`;
  try {
    const csrf = document.querySelector("input[name=csrfmiddlewaretoken]")?.value || "";
    const headers = { "Content-Type": "application/json" };
    if (csrf) headers["X-CSRFToken"] = csrf;

    const res = await fetch("/api/book-recommendations/", {
      method: "POST",
      headers,
      body: JSON.stringify({ level: userLevel, domains: userDomains, goal: userGoal })
    });
    const raw = await res.text();
    let data;
    try {
      data = JSON.parse(raw);
    } catch (parseErr) {
      throw new Error("Unexpected response from server. Please retry.");
    }
    if (!res.ok || !data.success) throw new Error(data.error || "Failed to load AI books");
    aiSection.innerHTML = data.data.length
      ? data.data.map(cardHtml).join("")
      : `<div class="col-12 text-center py-5">
           <h5 class="text-muted">No books found</h5>
           <p class="text-secondary">Try updating your profile domains to get better matches.</p>
         </div>`;
  } catch (e) {
    showError(e.message);
    aiSection.innerHTML = "";
  }
}

async function fetchFiltered() {
  clearError();
  filteredSection.innerHTML = `<div class="col-12 text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>`;
  const level = document.getElementById("levelFilter").value;
  const domain = document.getElementById("domainFilter").value;
  const type = document.getElementById("typeFilter").value;
  const params = new URLSearchParams({ level, domain, type });
  try {
    const res = await fetch(`/api/filter-books/?${params.toString()}`);
    const raw = await res.text();
    let data;
    try {
      data = JSON.parse(raw);
    } catch (parseErr) {
      throw new Error("Unexpected response from server. Please retry.");
    }
    if (!res.ok || !data.success) throw new Error(data.error || "Failed to load books");
    filteredSection.innerHTML = data.data.length
      ? data.data.map(cardHtml).join("")
      : `<div class="col-12 text-center py-5">
           <h5 class="text-muted">No books found</h5>
           <p class="text-secondary">Try adjusting filters or explore AI recommendations below.</p>
         </div>`;
  } catch (e) {
    showError(e.message);
    filteredSection.innerHTML = "";
  }
}

document.getElementById("filterBtn").addEventListener("click", (e) => {
  e.preventDefault();
  fetchFiltered();
});

// Load main content first, then AI suggestions as enhancement.
fetchFiltered().finally(() => {
  fetchAI();
});
