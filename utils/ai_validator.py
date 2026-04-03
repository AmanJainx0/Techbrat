import requests
from django.conf import settings
from django.core.cache import cache
import random

TECH_NORMALIZATION_MAP = {
    "redi": "Redis",
    "ai": "AI/ML",
    "ml": "AI/ML",
    "machine learning": "AI/ML",
    "artificial intelligence": "AI/ML",
    "js": "JavaScript",
    "reactjs": "React",
    "node": "Node.js",
    "py": "Python",
    "k8s": "Kubernetes",
    "aws": "AWS",
}

TECH_ALTERNATIVES = [
    "Web Development, AI/ML, or Databases",
    "Cloud Computing, Mobile Development, or Data Science",
    "Backend Architecture, Frontend Development, or DevOps"
]

# Only obvious non-tech words (NOT exhaustive)
NON_TECH_KEYWORDS = [
    "dance", "music", "cooking", "recipe", "sports",
    "gym", "yoga", "fashion", "makeup", "astrology",
    "politics", "religion", "acting", "singing"
]

def is_obviously_non_tech(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in NON_TECH_KEYWORDS)

def normalize_tech_query(query: str) -> str:
    """Auto-corrects and normalizes common tech queries."""
    if not query:
        return query
    
    lowered = query.strip().lower()
    return TECH_NORMALIZATION_MAP.get(lowered, query.strip())

def get_alternative_suggestions() -> str:
    """Returns a random suggestion string for blocked queries."""
    return random.choice(TECH_ALTERNATIVES)


def ai_is_tech_related(query: str) -> bool:
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "temperature": 0,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a strict but intelligent classifier.\n"
                            "Answer ONLY YES or NO.\n\n"
                            "Return YES if query is related to:\n"
                            "- programming\n"
                            "- software development\n"
                            "- computer science\n"
                            "- IT\n"
                            "- databases (Redis, MySQL, MongoDB)\n"
                            "- cloud (AWS, Azure)\n"
                            "- DevOps tools (Docker, Kubernetes)\n"
                            "- AI/ML, data science\n"
                            "- backend, frontend, system design\n\n"
                            "Return NO for non-tech topics like:\n"
                            "- cooking, dance, fitness, sports, fashion, music"
                        )
                    },
                    {"role": "user", "content": query}
                ]
            },
            timeout=6
        )

        content = (
            response.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
            .upper()
        )

        return content == "YES"

    except Exception:
        return False


def is_tech_query(query: str) -> bool:
    if not query:
        return True

    query = query.strip().lower()

    cache_key = f"tech_check_{query}"
    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    # Fast rejection
    if is_obviously_non_tech(query):
        cache.set(cache_key, False, 3600)
        return False

    # AI validation
    result = ai_is_tech_related(query)
    cache.set(cache_key, result, 3600)

    return result
