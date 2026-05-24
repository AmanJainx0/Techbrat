document.addEventListener('DOMContentLoaded', () => {
  const config = window.opportunityHubConfig || {};
  const apiUrl = config.apiUrl;
  const form = document.getElementById('opportunityFilters');
  const resetButton = document.getElementById('opportunityReset');
  const results = document.getElementById('opportunityResults');
  const loading = document.getElementById('opportunityLoading');
  const error = document.getElementById('opportunityError');
  const empty = document.getElementById('opportunityEmpty');
  const notes = document.getElementById('opportunityNotes');
  const count = document.getElementById('opportunityCount');
  const fetchedAt = document.getElementById('opportunityFetchedAt');
  const pagination = document.getElementById('opportunityPagination');
  const pageInfo = document.getElementById('opportunityPageInfo');
  const prevButton = document.getElementById('opportunityPrev');
  const nextButton = document.getElementById('opportunityNext');
  const detailModalElement = document.getElementById('opportunityDetailModal');
  const detailBadges = document.getElementById('opportunityDetailBadges');
  const detailLabel = document.getElementById('opportunityDetailLabel');
  const detailCompany = document.getElementById('opportunityDetailCompany');
  const detailLocation = document.getElementById('opportunityDetailLocation');
  const detailMode = document.getElementById('opportunityDetailMode');
  const detailCompensation = document.getElementById('opportunityDetailCompensation');
  const detailPosted = document.getElementById('opportunityDetailPosted');
  const detailDeadline = document.getElementById('opportunityDetailDeadline');
  const detailSource = document.getElementById('opportunityDetailSource');
  const detailSummary = document.getElementById('opportunityDetailSummary');
  const detailLink = document.getElementById('opportunityDetailLink');
  const detailModal = detailModalElement && window.bootstrap ? new window.bootstrap.Modal(detailModalElement) : null;
  let currentPage = 1;
  const pageLimit = 12;
  let currentItems = [];

  if (!form || !apiUrl) {
    return;
  }

  const escapeHtml = (value) => String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

  const formatFetchedAt = (value) => {
    if (!value) {
      return 'Updated just now';
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return 'Updated recently';
    }

    return `Updated ${date.toLocaleString([], {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })}`;
  };

  const typeLabel = (value) => value === 'job' ? 'Job' : 'Internship';

  const renderNotes = (items) => {
    const visibleItems = (items || []).filter((item) => {
      const text = String(item || '').toLowerCase();
      return !(
        text.includes('could not be reached right now') ||
        text.includes('timed out while loading live results') ||
        text.includes('before live records can be loaded here')
      );
    });

    if (!visibleItems.length) {
      notes.classList.add('d-none');
      notes.innerHTML = '';
      return;
    }

    notes.classList.remove('d-none');
    notes.innerHTML = visibleItems.map((item) => `<div>${escapeHtml(item)}</div>`).join('');
  };

  const renderCards = (items) => {
    currentItems = items;
    results.innerHTML = items.map((item) => `
      <div class="col-lg-6 col-xl-4">
        <article class="opportunity-card h-100" data-job-id="${escapeHtml(item.job_id || '')}">
          <div class="d-flex align-items-start justify-content-between gap-3 mb-3">
            <div>
              <div class="opportunity-badges">
                <span class="badge text-bg-light border">${escapeHtml(item.source_label || 'Source')}</span>
                <span class="badge text-bg-light border">${escapeHtml(typeLabel(item.opportunity_type))}</span>
              </div>
              <h3 class="h5 fw-bold mt-3 mb-1 opportunity-card-title">${escapeHtml(item.title)}</h3>
              <div class="text-secondary">${escapeHtml(item.company || 'Not specified')}</div>
            </div>
          </div>

          <div class="opportunity-details">
            <div><i class="fas fa-location-dot"></i><span>${escapeHtml(item.location || 'Not specified')}</span></div>
            <div><i class="fas fa-laptop-house"></i><span>${escapeHtml(item.mode || 'Not specified')}</span></div>
            <div><i class="fas fa-wallet"></i><span>${escapeHtml(item.compensation || 'Not specified')}</span></div>
            <div><i class="fas fa-clock"></i><span>${escapeHtml(item.posted_at || 'Recently listed')}</span></div>
            ${item.deadline ? `<div><i class="fas fa-hourglass-half"></i><span>${escapeHtml(item.deadline)}</span></div>` : ''}
          </div>

          <p class="opportunity-summary">${escapeHtml(item.summary || 'Open the source page for more details.')}</p>

          <div class="mt-auto pt-2 opportunity-card-actions">
            <button class="btn btn-outline-primary opportunity-detail-trigger" type="button" data-job-id="${escapeHtml(item.job_id || '')}">View details</button>
            <a class="btn btn-primary" href="${escapeHtml(item.url || '#')}" target="_blank" rel="noopener noreferrer">Open source</a>
          </div>
        </article>
      </div>
    `).join('');
  };

  const openDetailModal = (jobId) => {
    const item = currentItems.find((entry) => String(entry.job_id || '') === String(jobId || ''));
    if (!item || !detailModal) {
      return;
    }

    detailBadges.innerHTML = `
      <span class="badge text-bg-light border">${escapeHtml(item.source_label || 'Source')}</span>
      <span class="badge text-bg-light border">${escapeHtml(typeLabel(item.opportunity_type))}</span>
    `;
    detailLabel.textContent = item.title || 'Opportunity details';
    detailCompany.textContent = item.company || 'Not specified';
    detailLocation.textContent = item.location || 'Not specified';
    detailMode.textContent = item.mode || 'Not specified';
    detailCompensation.textContent = item.compensation || 'Not specified';
    detailPosted.textContent = item.posted_at || 'Recently listed';
    detailDeadline.textContent = item.deadline || 'Not specified';
    detailSource.textContent = item.source_label || 'Not specified';
    detailSummary.textContent = item.summary || 'Open the source listing for full information.';
    detailLink.href = item.url || '#';
    detailLink.classList.toggle('disabled', !item.url);
    detailModal.show();
  };

  const setState = (state) => {
    loading.classList.toggle('d-none', state !== 'loading');
    error.classList.toggle('d-none', state !== 'error');
    empty.classList.toggle('d-none', state !== 'empty');
    results.classList.toggle('d-none', state !== 'results');
  };

  const getFilters = () => {
    const formData = new FormData(form);
    const params = new URLSearchParams();

    for (const [key, value] of formData.entries()) {
      if (!value) {
        continue;
      }
      params.append(key, value);
    }

    form.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
      if (!checkbox.checked) {
        params.delete(checkbox.name);
      }
    });

    params.set('page', String(currentPage));
    params.set('limit', String(pageLimit));
    return params;
  };

  const renderPagination = (data) => {
    const details = data || {};
    const totalPages = Number(details.total_pages || 1);
    const page = Number(details.page || 1);

    if (totalPages <= 1) {
      pagination.classList.add('d-none');
      pageInfo.textContent = 'Page 1';
      prevButton.disabled = true;
      nextButton.disabled = true;
      return;
    }

    pagination.classList.remove('d-none');
    pageInfo.textContent = `Page ${page} of ${totalPages} • ${Number(details.total_count || 0)} results`;
    prevButton.disabled = !details.has_previous;
    nextButton.disabled = !details.has_next;
  };

  const loadOpportunities = async () => {
    setState('loading');
    renderNotes([]);
    pagination.classList.add('d-none');
    count.textContent = '0';

    try {
      const response = await fetch(`${apiUrl}?${getFilters().toString()}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      });
      const payload = await response.json();

      if (!response.ok || !payload.success) {
        throw new Error(payload.error || 'Could not load opportunities.');
      }

      const items = payload.opportunities || [];
      const paginationData = payload.pagination || {};
      count.textContent = String(Number(paginationData.total_count || items.length));
      fetchedAt.textContent = formatFetchedAt(payload.fetched_at);
      renderNotes(payload.source_notes || []);
      renderPagination(paginationData);

      if (!items.length) {
        results.innerHTML = '';
        setState('empty');
        return;
      }

      renderCards(items);
      setState('results');
    } catch (fetchError) {
      fetchedAt.textContent = 'Live data unavailable right now';
      results.innerHTML = '';
      setState('error');
    }
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    currentPage = 1;
    loadOpportunities();
  });

  resetButton.addEventListener('click', () => {
    form.reset();
    const keywordInput = document.getElementById('opportunityKeyword');
    if (keywordInput && keywordInput.defaultValue) {
      keywordInput.value = keywordInput.defaultValue;
    }
    currentPage = 1;
    loadOpportunities();
  });

  prevButton.addEventListener('click', () => {
    if (currentPage <= 1) {
      return;
    }
    currentPage -= 1;
    loadOpportunities();
  });

  nextButton.addEventListener('click', () => {
    currentPage += 1;
    loadOpportunities();
  });

  results.addEventListener('click', (event) => {
    const trigger = event.target.closest('.opportunity-detail-trigger');
    if (!trigger) {
      return;
    }
    openDetailModal(trigger.getAttribute('data-job-id'));
  });

  loadOpportunities();
});
