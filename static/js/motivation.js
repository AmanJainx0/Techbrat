// ═════════════ DOM ELEMENTS ═════════════
const categoryFilter = document.getElementById('categoryFilter');
const limitFilter = document.getElementById('limitFilter');
const filterBtn = document.getElementById('filterBtn');
const tipsContainer = document.getElementById('tipsContainer');
const tipCount = document.getElementById('tipCount');
const tipCardTemplate = document.getElementById('tipCardTemplate');

// ═════════════ ICONS MAPPING ═════════════
const categoryIcons = {
  'productivity': 'fa-fire',
  'learning_strategy': 'fa-brain',
  'coding_practice': 'fa-code',
  'career_growth': 'fa-rocket',
  'consistency': 'fa-check-circle',
  'mindset': 'fa-lightbulb',
};

// ═════════════ INITIALIZATION ═════════════
function init() {
  fetchTips();
}

// ═════════════ FETCH TIPS ═════════════
async function fetchTips() {
  const category = categoryFilter.value;
  const limit = limitFilter.value;

  // Clear previous results
  tipsContainer.innerHTML = '<div class="loading-spinner"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

  try {
    const response = await fetch('/api/filter-tips/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({
        category: category,
        limit: parseInt(limit)
      })
    });

    const data = await response.json();

    if (data.success) {
      displayTips(data.tips);
      tipCount.textContent = `${data.count} tip${data.count !== 1 ? 's' : ''} loaded`;
    } else {
      showError(data.error || 'Failed to fetch tips');
    }
  } catch (error) {
    console.error('Error fetching tips:', error);
    showError('An error occurred while fetching tips. Please try again.');
  }
}

// ═════════════ DISPLAY TIPS ═════════════
function displayTips(tips) {
  if (!tips || tips.length === 0) {
    tipsContainer.innerHTML = `
      <div style="grid-column: 1 / -1;">
        <div class="empty-state">
          <i class="fas fa-inbox"></i>
          <h4>No tips found</h4>
          <p>Try adjusting your filters or come back later for more tips</p>
        </div>
      </div>
    `;
    return;
  }

  tipsContainer.innerHTML = '';
  tips.forEach(tip => {
    const card = createTipCard(tip);
    tipsContainer.appendChild(card);
  });
}

// ═════════════ CREATE TIP CARD ═════════════
function createTipCard(tip) {
  const clone = tipCardTemplate.content.cloneNode(true);
  
  const icon = categoryIcons[tip.category] || 'fa-lightbulb';
  clone.getElementById('tipIcon').innerHTML = `<i class="fas ${icon}"></i>`;
  clone.getElementById('tipCategory').textContent = tip.category.replace('_', ' ').toUpperCase();
  clone.getElementById('tipTitle').textContent = tip.title;
  clone.getElementById('tipExplanation').textContent = tip.explanation;
  clone.getElementById('tipAction').textContent = tip.action_step;

  return clone;
}

// ═════════════ SHOW ERROR ═════════════
function showError(message) {
  tipsContainer.innerHTML = `
    <div style="grid-column: 1 / -1;">
      <div class="empty-state">
        <i class="fas fa-exclamation-circle"></i>
        <h4>Error</h4>
        <p>${message}</p>
      </div>
    </div>
  `;
}

// ═════════════ GET CSRF TOKEN ═════════════
function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] ||
         '';
}

// ═════════════ EVENT LISTENERS ═════════════
filterBtn.addEventListener('click', fetchTips);
categoryFilter.addEventListener('change', fetchTips);
limitFilter.addEventListener('change', fetchTips);

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
