// Tools & Platforms Page Script

// Get DOM elements
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const difficultyFilter = document.getElementById('difficultyFilter');
const useCaseFilter = document.getElementById('useCaseFilter');
const filterBtn = document.getElementById('filterBtn');
const filteredToolsContainer = document.getElementById('filteredTools');
const aiToolsContainer = document.getElementById('aiTools');
const errorDiv = document.getElementById('toolError');
const errorMsg = document.getElementById('errorMessage');
const toolCount = document.getElementById('toolCount');
const toolCardTemplate = document.getElementById('toolCardTemplate');

// Initialize - Load all tools on page load
function init() {
  fetchTools();
}

// Fetch and display tools
async function fetchTools() {
  const searchQuery = searchInput.value.trim();
  const category = categoryFilter.value;
  const difficulty = difficultyFilter.value;
  const useCase = useCaseFilter.value;

  // Clear previous results
  filteredToolsContainer.innerHTML = '<div class="loading-spinner"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  errorDiv.classList.add('d-none');

  try {
    const response = await fetch('/api/filter-tools/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({
        search: searchQuery,
        category: category,
        difficulty: difficulty,
        use_case: useCase
      })
    });

    const data = await response.json();

    if (data.success) {
      displayTools(data.tools);
      toolCount.textContent = `${data.count} tool${data.count !== 1 ? 's' : ''} found`;
      
      // Fetch AI recommendations after successful main fetch
      if (data.count > 0) {
        fetchAIRecommendations();
      } else {
        aiToolsContainer.innerHTML = '<div class="col-12"><p class="text-muted text-center">No additional recommendations available</p></div>';
      }
    } else {
      showError(data.message || 'Failed to fetch tools');
    }
  } catch (error) {
    console.error('Error fetching tools:', error);
    showError('An error occurred while fetching tools. Please try again.');
  }
}

// Display tools in grid
function displayTools(tools) {
  if (!tools || tools.length === 0) {
    filteredToolsContainer.innerHTML = `
      <div class="col-12">
        <div class="empty-state">
          <i class="fas fa-search"></i>
          <h5>No tools found</h5>
          <p>Try adjusting your filters or search terms</p>
        </div>
      </div>
    `;
    return;
  }

  filteredToolsContainer.innerHTML = '';
  tools.forEach(tool => {
    const card = createToolCard(tool);
    filteredToolsContainer.appendChild(card);
  });
}

// Create tool card from template
function createToolCard(tool) {
  const clone = toolCardTemplate.content.cloneNode(true);
  
  clone.getElementById('toolCategory').textContent = tool.category.replace('_', ' ').toUpperCase();
  clone.getElementById('toolName').textContent = tool.name;
  clone.getElementById('toolDesc').textContent = tool.description || 'A powerful development tool';
  clone.getElementById('toolDifficulty').textContent = tool.difficulty.toUpperCase();
  clone.getElementById('toolUseCase').textContent = tool.use_case.toUpperCase();
  
  const link = clone.getElementById('toolLink');
  link.href = tool.link || '#';
  
  if (tool.is_ai_generated) {
    clone.getElementById('aiGeneratedBadge').innerHTML = '<i class="fas fa-sparkles me-1"></i>AI-discovered';
  }

  // Add difficulty-based styling
  const diffBadge = clone.getElementById('toolDifficulty');
  if (tool.difficulty === 'intermediate') {
    diffBadge.className = 'tool-badge difficulty-intermediate';
  } else if (tool.difficulty === 'advanced') {
    diffBadge.className = 'tool-badge difficulty-advanced';
  }

  return clone;
}

// Fetch AI recommendations
async function fetchAIRecommendations() {
  const category = categoryFilter.value !== 'all' ? categoryFilter.value : null;
  const difficulty = difficultyFilter.value !== 'all' ? difficultyFilter.value : null;
  const useCase = useCaseFilter.value !== 'all' ? useCaseFilter.value : null;

  try {
    const response = await fetch('/api/tools-recommendations/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({
        category: category,
        difficulty: difficulty,
        use_case: useCase
      })
    });

    const data = await response.json();

    if (data.success) {
      displayAITools(data.tools);
    } else {
      aiToolsContainer.innerHTML = '<div class="col-12"><p class="text-muted text-center">Could not load AI recommendations</p></div>';
    }
  } catch (error) {
    console.error('Error fetching AI recommendations:', error);
    aiToolsContainer.innerHTML = '<div class="col-12"><p class="text-muted text-center">Error loading recommendations</p></div>';
  }
}

// Display AI-generated tools
function displayAITools(tools) {
  if (!tools || tools.length === 0) {
    aiToolsContainer.innerHTML = '<div class="col-12"><p class="text-muted text-center">No AI recommendations available</p></div>';
    return;
  }

  aiToolsContainer.innerHTML = '';
  tools.forEach(tool => {
    const card = createToolCard(tool);
    aiToolsContainer.appendChild(card);
  });
}

// Show error message
function showError(message) {
  errorMsg.textContent = message;
  errorDiv.classList.remove('d-none');
  filteredToolsContainer.innerHTML = `
    <div class="col-12">
      <div class="empty-state">
        <i class="fas fa-times-circle"></i>
        <p>${message}</p>
        <small class="text-muted">This platform supports only technology-related tools and platforms.</small>
      </div>
    </div>
  `;
  aiToolsContainer.innerHTML = '';
}

// Get CSRF token
function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] ||
         '';
}

// Event listeners
filterBtn.addEventListener('click', fetchTools);
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    fetchTools();
  }
});

// Filter changes trigger search
categoryFilter.addEventListener('change', fetchTools);
difficultyFilter.addEventListener('change', fetchTools);
useCaseFilter.addEventListener('change', fetchTools);

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
