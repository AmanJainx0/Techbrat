import os
import re
import hashlib
from datetime import datetime
from html import unescape
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


SOURCE_LABELS = {
    'jooble': 'Jooble',
    'adzuna': 'Adzuna',
    'jsearch': 'JSearch',
}

JOOBLE_API_BASE_URL = os.getenv('JOOBLE_API_BASE_URL', 'https://jooble.org/api').rstrip('/')
JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY', '').strip()
ADZUNA_API_BASE_URL = os.getenv('ADZUNA_API_BASE_URL', 'https://api.adzuna.com/v1/api/jobs').rstrip('/')
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID', '').strip()
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY', '').strip()
ADZUNA_COUNTRIES = [value.strip() for value in os.getenv('ADZUNA_COUNTRIES', 'in,us,gb,au,ca,sg,de').split(',') if value.strip()]
JSEARCH_API_URL = os.getenv('JSEARCH_API_URL', 'https://api.api-ninjas.com/v1/jobsearch').strip()
JSEARCH_API_KEY = os.getenv('JSEARCH_API_KEY', '').strip()
JSEARCH_API_AUTH_HEADER = os.getenv('JSEARCH_API_AUTH_HEADER', 'X-Api-Key').strip() or 'X-Api-Key'
JSEARCH_API_HOST = os.getenv('JSEARCH_API_HOST', '').strip()
JSEARCH_API_HOST_HEADER = os.getenv('JSEARCH_API_HOST_HEADER', 'X-RapidAPI-Host').strip() or 'X-RapidAPI-Host'
API_TIMEOUT_SECONDS = float(os.getenv('OPPORTUNITY_API_TIMEOUT', '3.5'))
MAX_PROVIDER_WORKERS = max(int(os.getenv('OPPORTUNITY_PROVIDER_WORKERS', '3')), 1)
INDIA_LOCATION_TOKENS = [
    'india', 'bengaluru', 'bangalore', 'hyderabad', 'pune', 'mumbai',
    'delhi', 'gurgaon', 'noida', 'chennai', 'kolkata', 'ahmedabad',
]
TECH_OPPORTUNITY_KEYWORDS = {
    'software', 'developer', 'engineer', 'data', 'machine learning', 'ai',
    'backend', 'frontend', 'full stack', 'fullstack', 'web', 'cloud',
    'devops', 'python', 'java', 'react', 'node', 'analytics', 'sql',
    'data analyst', 'data engineer', 'data scientist', 'qa', 'sdet',
    'cybersecurity', 'security', 'api', 'django', 'flask', 'fastapi',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'android', 'ios'
}
STRONG_TECH_SIGNAL_KEYWORDS = {
    'software engineer', 'software developer', 'python developer', 'java developer',
    'frontend developer', 'backend developer', 'full stack developer',
    'data analyst', 'data engineer', 'data scientist', 'machine learning engineer',
    'ai engineer', 'devops engineer', 'cloud engineer', 'qa engineer', 'sdet',
    'web developer', 'mobile developer', 'android developer', 'ios developer',
    'cybersecurity analyst', 'security engineer', 'react developer', 'node developer',
    'software', 'developer', 'engineer', 'python', 'java', 'react', 'node',
    'machine learning', 'artificial intelligence', 'cloud', 'devops', 'analytics'
}
NON_TECH_OPPORTUNITY_KEYWORDS = {
    'nurse', 'registered nurse', 'therapist', 'physician', 'doctor',
    'pharmacy', 'pharmacist', 'mechanic', 'sales', 'marketing', 'hr',
    'recruiter', 'recruitment', 'legal', 'lawyer', 'social worker',
    'teacher', 'chef', 'cook', 'driver', 'delivery', 'beauty', 'fashion',
    'real estate', 'customer support', 'customer service', 'bpo',
    'telecaller', 'operations executive', 'business development'
}
STRICT_NON_TECH_ROLE_KEYWORDS = {
    'recruiter', 'recruitment', 'hr', 'human resources', 'talent acquisition',
    'sales', 'marketing', 'business development', 'customer support',
    'customer service', 'telecaller', 'bpo', 'operations executive',
    'law', 'legal', 'operations intern', 'law intern', 'social work',
    'business partner', 'leadership course', 'registered nurse', 'therapist',
    'physician', 'doctor', 'pharmacy', 'mechanic', 'social worker'
}
GENERIC_TITLE_TERMS = {'intern', 'trainee', 'associate'}
AMBIGUOUS_TITLE_TERMS = {'worker', 'architect', 'intern', 'trainee', 'associate'}

HTTP_SESSION = requests.Session()
HTTP_SESSION.trust_env = False


def _clean_text(value):
    return re.sub(r'\s+', ' ', unescape(str(value or ''))).strip()


def _fetch_html(url):
    response = HTTP_SESSION.get(
        url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            )
        },
        timeout=12,
    )
    response.raise_for_status()
    return response.text


def _guess_mode(text):
    text = (text or '').lower()
    if 'work from home' in text or 'remote' in text:
        return 'Remote'
    if 'hybrid' in text:
        return 'Hybrid'
    return 'On-site'


def _text_matches_filters(text, filters):
    keyword = (filters.get('keyword') or '').strip().lower()
    location = (filters.get('location') or '').strip().lower()
    remote_only = filters.get('remote_only')
    paid_only = filters.get('paid_only')

    haystack = (text or '').lower()
    if keyword and keyword not in haystack:
        return False
    if location and location not in haystack:
        return False
    if remote_only and not any(token in haystack for token in ['work from home', 'remote']):
        return False
    if paid_only and any(token in haystack for token in ['unpaid', 'performance based']):
        return False
    return True


def _extract_anchor_cards(html, base_url, href_patterns, opportunity_type, source_key, filters, limit=20):
    if not BeautifulSoup:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    seen = set()
    items = []

    for anchor in soup.find_all('a', href=True):
        href = anchor.get('href', '')
        if not any(pattern in href for pattern in href_patterns):
            continue

        title = _clean_text(anchor.get_text(' ', strip=True))
        if len(title) < 4:
            continue

        link = urljoin(base_url, href)
        if link in seen:
            continue

        container = anchor
        while container and len(_clean_text(container.get_text(' ', strip=True))) < 80:
            container = container.parent
        if not container:
            continue

        block_text = _clean_text(container.get_text(' ', strip=True))
        if title.lower() not in block_text.lower():
            continue
        if not _text_matches_filters(block_text, filters):
            continue

        company = ''
        if source_key == 'internshala':
            company_match = re.search(rf'{re.escape(title)}\s+(.*?)\s+(Actively hiring|[A-Z][a-z]{{2,}},|₹|Work from home|Remote)', block_text)
            if company_match:
                company = _clean_text(company_match.group(1))
        elif source_key == 'unstop':
            company_match = re.search(rf'{re.escape(title)}\s+(.*?)\s+(Applied|Application Deadline|Impressions|Work from home|Remote|Delhi,|Bangalore,|Mumbai,)', block_text)
            if company_match:
                company = _clean_text(company_match.group(1))

        location_match = re.search(r'(Work from home|Remote|Hybrid|[A-Z][A-Za-z]+(?:,\s*[A-Z][A-Za-z]+)*)', block_text)
        compensation_match = re.search(r'(₹\s*[\d,]+(?:\s*-\s*[\d,]+)?(?:\s*/month|\s*/year|\s*lump sum)?|Unpaid|Performance Based)', block_text, re.IGNORECASE)
        posted_match = re.search(r'(Just now|Today|Few hours ago|\d+\s+(?:day|days|week|weeks|month|months)\s+ago)', block_text, re.IGNORECASE)
        deadline_match = re.search(r'Application Deadline\s+([^.]+?)(?:Impressions|Eligibility|Details|$)', block_text, re.IGNORECASE)

        items.append({
            'title': title,
            'company': company or SOURCE_LABELS[source_key],
            'location': _clean_text(location_match.group(1)) if location_match else 'Not specified',
            'mode': _guess_mode(block_text),
            'compensation': _clean_text(compensation_match.group(1)) if compensation_match else 'Not specified',
            'posted_at': _clean_text(posted_match.group(1)) if posted_match else 'Recently listed',
            'deadline': _clean_text(deadline_match.group(1)) if deadline_match else '',
            'source': source_key,
            'source_label': SOURCE_LABELS[source_key],
            'opportunity_type': opportunity_type,
            'url': link,
            'summary': block_text[:420],
        })
        seen.add(link)

        if len(items) >= limit:
            break

    return items


def _fetch_internshala(filters):
    results = []
    opportunity_type = (filters.get('opportunity_type') or 'all').lower()

    if opportunity_type in ('all', 'internship'):
        html = _fetch_html('https://internshala.com/internships/')
        results.extend(
            _extract_anchor_cards(
                html,
                'https://internshala.com',
                ['/internships/', '/internship/detail'],
                'internship',
                'internshala',
                filters,
                limit=12,
            )
        )

    if opportunity_type in ('all', 'job'):
        html = _fetch_html('https://internshala.com/fresher-jobs/')
        results.extend(
            _extract_anchor_cards(
                html,
                'https://internshala.com',
                ['/jobs/', '/fresher-jobs/'],
                'job',
                'internshala',
                filters,
                limit=12,
            )
        )

    return results


def _fetch_unstop(filters):
    results = []
    opportunity_type = (filters.get('opportunity_type') or 'all').lower()

    if opportunity_type in ('all', 'internship'):
        html = _fetch_html('https://unstop.com/internships/amp')
        results.extend(
            _extract_anchor_cards(
                html,
                'https://unstop.com',
                ['/internships/'],
                'internship',
                'unstop',
                filters,
                limit=10,
            )
        )

    if opportunity_type in ('all', 'job'):
        html = _fetch_html('https://unstop.com/jobs/amp')
        results.extend(
            _extract_anchor_cards(
                html,
                'https://unstop.com',
                ['/jobs/'],
                'job',
                'unstop',
                filters,
                limit=10,
            )
        )

    return results


def _fetch_json(url, params=None, headers=None):
    response = HTTP_SESSION.get(
        url,
        params=params or {},
        headers=headers or {'Accept': 'application/json'},
        timeout=API_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _post_json(url, payload=None, headers=None):
    response = HTTP_SESSION.post(
        url,
        json=payload or {},
        headers=headers or {'Accept': 'application/json'},
        timeout=API_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _coalesce(record, *keys):
    for key in keys:
        value = record.get(key)
        if value not in (None, '', []):
            return value
    return ''


def _normalize_type(value, source_key):
    text = _clean_text(value).lower()
    if 'intern' in text:
        return 'internship'
    if any(token in text for token in ['job', 'employment', 'vacancy', 'role']):
        return 'job'
    return 'job'


def _normalize_api_record(record, source_key):
    title = _clean_text(_coalesce(record, 'title', 'job_title', 'position', 'designation', 'opportunity_title', 'internship_title', 'name'))
    if not title:
        return None

    company = _clean_text(_coalesce(record, 'company', 'company_name', 'employer_name', 'organization', 'organisation', 'industry_name')) or SOURCE_LABELS[source_key]
    location = _clean_text(_coalesce(record, 'location', 'job_location', 'city', 'state', 'district', 'place')) or 'Not specified'
    summary = _clean_text(_coalesce(record, 'snippet', 'job_description', 'description', 'internship_description', 'summary', 'details', 'skills_required'))
    compensation = _clean_text(_coalesce(record, 'compensation', 'salary', 'stipend', 'salary_range', 'pay')) or 'Not specified'
    combined_text = ' '.join([title, company, location, summary, compensation, _clean_text(_coalesce(record, 'work_mode', 'mode', 'job_nature', 'type'))])
    mode = _clean_text(_coalesce(record, 'work_mode', 'mode', 'job_nature')) or _guess_mode(combined_text)

    normalized = {
        'title': title,
        'company': company,
        'location': location,
        'mode': mode,
        'compensation': compensation,
        'posted_at': _clean_text(_coalesce(record, 'updated', 'posted_at', 'posted_on', 'published_at', 'created_at', 'date')) or 'Recently listed',
        'deadline': _clean_text(_coalesce(record, 'deadline', 'last_date', 'application_deadline', 'apply_by', 'closing_date')),
        'source': source_key,
        'source_label': SOURCE_LABELS[source_key],
        'opportunity_type': _normalize_type(
            ' '.join([
                str(_coalesce(record, 'opportunity_type', 'type', 'job_type')),
                title,
                summary,
            ]),
            source_key,
        ),
        'url': _clean_text(_coalesce(record, 'url', 'apply_url', 'job_apply_link', 'internship_apply_link', 'details_url', 'link')),
        'summary': summary or 'Open the listing for more details.',
    }
    normalized['job_id'] = generate_job_id(normalized)
    return normalized


def _normalize_adzuna_record(record):
    title = _clean_text(_coalesce(record, 'title'))
    if not title:
        return None

    location_area = record.get('location', {}).get('area') if isinstance(record.get('location'), dict) else []
    location = _clean_text(', '.join(location_area)) or _clean_text(_coalesce(record, 'location', 'city', 'state')) or 'Not specified'
    company_data = record.get('company') if isinstance(record.get('company'), dict) else {}
    company = _clean_text(company_data.get('display_name')) or SOURCE_LABELS['adzuna']
    summary = _clean_text(_coalesce(record, 'description')) or 'Open the listing for more details.'
    contract_type = _clean_text(_coalesce(record, 'contract_type'))
    compensation = 'Not specified'
    salary_min = record.get('salary_min')
    salary_max = record.get('salary_max')
    if salary_min or salary_max:
        if salary_min and salary_max:
            compensation = f"{salary_min} - {salary_max}"
        else:
            compensation = str(salary_min or salary_max)

    normalized = {
        'title': title,
        'company': company,
        'location': location,
        'mode': _guess_mode(' '.join([summary, contract_type, location])),
        'compensation': compensation,
        'posted_at': _clean_text(_coalesce(record, 'created')) or 'Recently listed',
        'deadline': '',
        'source': 'adzuna',
        'source_label': SOURCE_LABELS['adzuna'],
        'opportunity_type': _normalize_type(f'{contract_type} {title} {summary}', 'adzuna'),
        'url': _clean_text(_coalesce(record, 'redirect_url', 'url')),
        'summary': summary,
    }
    normalized['job_id'] = generate_job_id(normalized)
    return normalized


def _extract_api_records(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []

    for key in ['jobs', 'records', 'results', 'items', 'data', 'opportunities']:
        value = payload.get(key)
        if isinstance(value, list):
            return value

    result = payload.get('result')
    if isinstance(result, dict) and isinstance(result.get('records'), list):
        return result['records']
    return []


def generate_job_id(job):
    title = _clean_text(job.get('title')).lower()
    company = _clean_text(job.get('company')).lower()
    location = _clean_text(job.get('location')).lower()
    url = _clean_text(job.get('url')).lower()
    base = url or f'{title}-{company}-{location}'
    return hashlib.md5(base.encode('utf-8')).hexdigest()


def _is_india_match(text):
    text = (text or '').lower()
    return any(token in text for token in INDIA_LOCATION_TOKENS)


def _is_generic_title(title):
    normalized = _clean_text(title).lower()
    return normalized in GENERIC_TITLE_TERMS


def _is_tech_opportunity(item):
    title = (item.get('title') or '').lower()
    summary = (item.get('summary') or '').lower()
    title_has_strong_signal = any(token in title for token in STRONG_TECH_SIGNAL_KEYWORDS)
    title_has_tech_signal = any(token in title for token in TECH_OPPORTUNITY_KEYWORDS)
    summary_has_strong_signal = any(
        token in summary for token in [
            'software engineer', 'software developer', 'python developer', 'java developer',
            'frontend developer', 'backend developer', 'full stack developer',
            'data analyst', 'data engineer', 'data scientist', 'machine learning',
            'artificial intelligence', 'cloud engineer', 'devops engineer',
            'qa engineer', 'sdet', 'web developer', 'mobile developer',
            'cybersecurity', 'security engineer', 'react developer', 'node developer'
        ]
    )
    haystack = ' '.join([
        title,
        item.get('company', ''),
        summary,
        item.get('location', ''),
    ]).lower()

    if any(token in title for token in STRICT_NON_TECH_ROLE_KEYWORDS):
        return False
    if any(token in summary for token in STRICT_NON_TECH_ROLE_KEYWORDS):
        return False

    if _is_generic_title(title):
        return False

    if any(term == title.strip() for term in AMBIGUOUS_TITLE_TERMS):
        return False

    if any(token in haystack for token in NON_TECH_OPPORTUNITY_KEYWORDS):
        return False

    if title_has_strong_signal:
        return True

    if title_has_tech_signal and not any(token in title for token in STRICT_NON_TECH_ROLE_KEYWORDS):
        return True

    return summary_has_strong_signal


def _matches_item_filters(item, filters):
    keyword = (filters.get('keyword') or '').strip().lower()
    location = (filters.get('location') or '').strip().lower()
    opportunity_type = (filters.get('opportunity_type') or 'all').strip().lower()
    region = (filters.get('region') or 'all').strip().lower()
    remote_only = filters.get('remote_only')
    paid_only = filters.get('paid_only')

    haystack = ' '.join([
        item.get('title', ''),
        item.get('company', ''),
        item.get('location', ''),
        item.get('summary', ''),
        item.get('compensation', ''),
    ]).lower()

    if keyword and keyword not in haystack:
        return False
    if not _is_tech_opportunity(item):
        return False
    if location and location not in item.get('location', '').lower():
        return False
    if region == 'india':
        if not _is_india_match(haystack):
            return False
    if region == 'abroad':
        if _is_india_match(haystack):
            return False
    if opportunity_type in {'internship', 'job'} and item.get('opportunity_type') != opportunity_type:
        return False
    if remote_only and 'remote' not in (item.get('mode') or '').lower():
        return False
    if paid_only and any(token in (item.get('compensation') or '').lower() for token in ['unpaid', 'not specified', '0']):
        return False
    return True


def _fetch_jooble(filters):
    if not JOOBLE_API_KEY:
        raise RuntimeError('Jooble API is not configured.')

    region = (filters.get('region') or 'all').strip().lower()
    location = (filters.get('location') or '').strip()
    if region == 'india' and not location:
        location = 'India'

    payload = _post_json(
        f'{JOOBLE_API_BASE_URL}/{JOOBLE_API_KEY}',
        payload={
            'keywords': filters.get('keyword') or '',
            'location': location,
            'page': 1,
        },
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    )

    items = []
    for record in _extract_api_records(payload):
        normalized = _normalize_api_record(record, 'jooble')
        if normalized and _is_tech_opportunity(normalized) and _matches_item_filters(normalized, filters):
            items.append(normalized)
    return items


def _fetch_adzuna(filters):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise RuntimeError('Adzuna API is not configured.')

    region = (filters.get('region') or 'all').strip().lower()
    countries = list(ADZUNA_COUNTRIES)
    if region == 'india':
        countries = ['in']
    elif region == 'abroad':
        countries = [country for country in countries if country != 'in'] or ['us', 'gb', 'au', 'ca']

    items = []
    for country_code in countries[:4]:
        payload = _fetch_json(
            f'{ADZUNA_API_BASE_URL}/{country_code}/search/1',
            params={
                'app_id': ADZUNA_APP_ID,
                'app_key': ADZUNA_APP_KEY,
                'results_per_page': 20,
                'what': filters.get('keyword') or '',
                'where': filters.get('location') or '',
            },
        )
        for record in _extract_api_records(payload):
            normalized = _normalize_adzuna_record(record)
            if normalized and _is_tech_opportunity(normalized) and _matches_item_filters(normalized, filters):
                items.append(normalized)
    return items


def _fetch_jsearch(filters):
    if not JSEARCH_API_KEY:
        raise RuntimeError('JSearch API is not configured.')

    headers = {'Accept': 'application/json', JSEARCH_API_AUTH_HEADER: JSEARCH_API_KEY}
    if JSEARCH_API_HOST:
        headers[JSEARCH_API_HOST_HEADER] = JSEARCH_API_HOST
    region = (filters.get('region') or 'all').strip().lower()
    query_parts = [filters.get('keyword') or 'software']
    if filters.get('location'):
        query_parts.append(f"in {filters.get('location')}")
    elif region == 'india':
        query_parts.append('in India')
    elif region == 'abroad':
        query_parts.append('outside India')

    payload = _fetch_json(
        JSEARCH_API_URL,
        params={
            'query': ' '.join(part for part in query_parts if part),
            'page': 1,
            'num_pages': 1,
        },
        headers=headers,
    )

    items = []
    for record in _extract_api_records(payload):
        normalized = _normalize_api_record(record, 'jsearch')
        if normalized and _is_tech_opportunity(normalized) and _matches_item_filters(normalized, filters):
            items.append(normalized)
    return items


def _safe_fetch(source_key, fetcher, filters, error_message):
    try:
        items = fetcher(filters)
        return {
            'source': source_key,
            'items': items,
            'count': len(items),
            'error': None,
            'note': None,
        }
    except requests.exceptions.ReadTimeout:
        return {
            'source': source_key,
            'items': [],
            'count': 0,
            'error': 'timeout',
            'note': f"{SOURCE_LABELS.get(source_key, source_key)} timed out while loading live results.",
        }
    except requests.exceptions.RequestException:
        return {
            'source': source_key,
            'items': [],
            'count': 0,
            'error': 'request_error',
            'note': f"{SOURCE_LABELS.get(source_key, source_key)} could not be reached right now.",
        }
    except Exception:
        return {
            'source': source_key,
            'items': [],
            'count': 0,
            'error': error_message,
            'note': error_message,
        }


def _dedupe_items(items):
    deduped = []
    seen = set()

    for item in items:
        title = _clean_text(item.get('title')).lower()
        company = _clean_text(item.get('company')).lower()
        location = _clean_text(item.get('location')).lower()
        key = (item.get('job_id') or '').strip().lower()
        if not key:
            key = generate_job_id(item)
            item['job_id'] = key
        if item.get('url'):
            url_key = f"url:{_clean_text(item.get('url')).lower()}"
            if url_key in seen:
                continue
        else:
            url_key = ''
        fuzzy_key = f'{title}|{company}|{location}'
        if not key or key in seen:
            continue
        seen.add(key)
        if fuzzy_key:
            seen.add(fuzzy_key)
        if url_key:
            seen.add(url_key)
        deduped.append(item)

    return deduped


def _ranking_score(item, filters):
    score = 0
    keyword = (filters.get('keyword') or '').strip().lower()
    haystack = ' '.join([
        item.get('title', ''),
        item.get('company', ''),
        item.get('summary', ''),
    ]).lower()
    compensation = (item.get('compensation') or '').lower()
    posted_at = (item.get('posted_at') or '').lower()
    source = (item.get('source') or '').lower()

    if keyword and keyword in haystack:
        score += 25
    if item.get('opportunity_type') == 'internship' and 'intern' in haystack:
        score += 12
    if any(token in compensation for token in ['$', '₹', '€', '£']) or re.search(r'\d', compensation):
        score += 18
    if any(token in posted_at for token in ['today', 'hour', 'just now']):
        score += 15
    if 'day' in posted_at:
        score += 8
    if source == 'jooble':
        score += 4
    return score


def fetch_live_opportunities(filters):
    source_notes = []
    provider_jobs = [
        ('jooble', _fetch_jooble, 'Jooble results need `JOOBLE_API_KEY` before live records can be loaded here.'),
        ('adzuna', _fetch_adzuna, 'Adzuna results need `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` before live records can be loaded here.'),
        ('jsearch', _fetch_jsearch, 'JSearch results need `JSEARCH_API_KEY` before live records can be loaded here.'),
    ]
    provider_results = []

    with ThreadPoolExecutor(max_workers=min(MAX_PROVIDER_WORKERS, len(provider_jobs))) as executor:
        future_map = {
            executor.submit(_safe_fetch, source_key, fetcher, filters, error_message): source_key
            for source_key, fetcher, error_message in provider_jobs
        }
        for future in as_completed(future_map):
            provider_results.append(future.result())

    items = []
    meta = {
        'jooble_count': 0,
        'adzuna_count': 0,
        'jsearch_count': 0,
        'failed_sources': [],
        'deduped_out': 0,
    }

    for provider in provider_results:
        meta[f"{provider['source']}_count"] = provider['count']
        items.extend(provider['items'])
        if provider['note']:
            source_notes.append(provider['note'])
            meta['failed_sources'].append(provider['source'])

    raw_count = len(items)
    items = _dedupe_items(items)
    meta['deduped_out'] = max(raw_count - len(items), 0)
    items.sort(key=lambda item: _ranking_score(item, filters), reverse=True)
    meta['final_count'] = len(items)
    return {
        'items': items,
        'source_notes': source_notes,
        'meta': meta,
        'fetched_at': datetime.utcnow().isoformat() + 'Z',
    }
