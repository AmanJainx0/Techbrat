from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.sites.models import Site

from techbrat.models import Course, UserProfile, UserSkill, Book


def get_landing_context(auth_mode='signup'):
    try:
        from allauth.socialaccount.models import SocialApp

        site = Site.objects.get_current()
        google_enabled = SocialApp.objects.filter(provider='google', sites=site).exists()
        github_enabled = SocialApp.objects.filter(provider='github', sites=site).exists()
    except Exception:
        google_enabled = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)
        github_enabled = bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)

    return {
        'google_login_enabled': google_enabled,
        'github_login_enabled': github_enabled,
        'auth_mode': auth_mode,
    }

def index(request):
    # If user is not authenticated, show landing page
    if not request.user.is_authenticated:
        return render(request, 'landing_auth.html', get_landing_context())
    return render(request, 'index.html')

@login_required(login_url='techbrat:signin')
def issue(request):
    return render(request, 'issue.html')

@login_required(login_url='techbrat:signin')
def que(request):
    return render(request, 'que.html')

def roadmap(request):
    return render(request, 'roadmap.html')

def signin(request):
    if request.user.is_authenticated:
        return redirect('techbrat:welcome')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if user exists
        try:
            user_exists = User.objects.get(email=email)
            # User exists, authenticate
            user = authenticate(request, username=user_exists.username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('techbrat:welcome')
            else:
                # User exists but password is wrong
                messages.error(request, 'Incorrect password. Please try again.')
        except User.DoesNotExist:
            # User doesn't exist
            messages.error(request, 'Email not found. Please create an account to continue.')
    
    return render(request, 'landing_auth.html', get_landing_context('signin'))

def signup(request):
    if request.user.is_authenticated:
        return redirect('techbrat:welcome')
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'landing_auth.html', get_landing_context('signup'))
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'landing_auth.html', get_landing_context('signup'))
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'landing_auth.html', get_landing_context('signup'))
        
        # Create new user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=fullname
            )
            user.save()

            # Ensure profile exists immediately for downstream views/templates
            get_or_create_profile(user)

            # Auto-login after signup
            login(request, user)
            return redirect('techbrat:welcome')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'landing_auth.html', get_landing_context('signup'))

def welcome(request):
    if not request.user.is_authenticated:
        return redirect('techbrat:signin')
    return render(request, 'welcome.html')

def signout(request):
    logout(request)
    messages.success(request, 'You have been signed out successfully!')
    return redirect('techbrat:index')


def get_or_create_profile(user):
    """Centralized helper to safely fetch or create a profile with sane defaults."""
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if not profile.education_level:
        profile.education_level = 'undergraduate'
        profile.save(update_fields=['education_level'])

    return profile


def get_user_domains(profile):
    """Return tech domains as a trimmed list for template-friendly rendering."""
    if not profile.tech_domains:
        return []
    return [d.strip() for d in profile.tech_domains.split(',') if d.strip()]


def get_profile_completion(profile):
    """Calculate profile completion in 20% steps based on key fields and skills."""
    fields = [
        profile.current_course,
        profile.year_of_study,
        profile.tech_domains,
        profile.target_timeline,
    ]

    completion = sum(1 for field in fields if field) * 20

    if profile.skills.exists():
        completion += 20

    return min(completion, 100)

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from utils.ai_validator import is_tech_query, normalize_tech_query, get_alternative_suggestions

def get_user_level(user):
    """
    Determines user experience level (beginner, intermediate, advanced)
    based on their profile and activity.
    """
    if not user.is_authenticated:
        return "beginner"
    
    from .models import UserProfile, UserSkill
    
    try:
        profile = user.profile
        
        # 1. Check education level
        if profile.education_level in ['postgraduate', 'doctorate']:
            base_score = 2
        elif profile.education_level == 'undergraduate':
            base_score = 1
        else:
            base_score = 0
            
        # 2. Check skill levels
        skills = profile.skills.all()
        if skills.exists():
            advanced_skills = skills.filter(proficiency='advanced').count()
            intermediate_skills = skills.filter(proficiency='intermediate').count()
            
            if advanced_skills >= 2:
                base_score += 2
            elif intermediate_skills >= 3 or advanced_skills >= 1:
                base_score += 1
                
        
            
        # Final Determination
        if base_score >= 4:
            return "advanced"
        elif base_score >= 2:
            return "intermediate"
        else:
            return "beginner"
            
    except Exception:
        return "beginner"


# --------------------------- STATIC ROADMAP API ---------------------------


@csrf_exempt
def get_roadmap(request):
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "roadmap", "backend_roadmap.json")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return JsonResponse(data, safe=False)

    except FileNotFoundError:
        return JsonResponse({"error": "Roadmap JSON file not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------
# Tech-domain validation helpers
# ---------------------------

NON_TECH_DOMAINS = [
    "dance", "dancing", "choreography",
    "singing", "music", "guitar", "piano",
    "cooking", "recipe", "chef",
    "painting", "sketching", "art",
    "sports", "football", "cricket", "tennis",
    "gym", "fitness", "yoga",
    "acting", "drama",
    "fashion", "makeup",
    "astrology", "horoscope",
    "politics", "religion"
]

def is_obviously_non_tech(text: str) -> bool:
    if not text:
        return False
    text = text.lower()
    return any(word in text for word in NON_TECH_DOMAINS)



def ai_is_tech_related(prompt: str) -> bool:
    """
    AI-based classifier.
    NEVER raises exception.
    Returns False if unsure.
    """
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
                            "You are a strict classifier.\n"
                            "Answer ONLY with YES or NO.\n"
                            "Is the following query related to technology, "
                            "software development, computer science, or IT?"
                        )
                    },
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=8
        )

        data = response.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
            .upper()
        )

        return content == "YES"

    except Exception as e:
        # 🔒 SAFETY NET
        print("AI classifier failed:", str(e))
        return False

# --------------------------- AI ROADMAP GENERATOR ---------------------------

@csrf_exempt
def generate_roadmap(request):
    """
    Generates a technical roadmap using AI.
    Guarantees JSON-only response to frontend.
    """

    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Only POST requests are allowed"},
            status=405
        )

    try:
        # -------------------------
        # Parse Request Body
        # -------------------------
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse(
                {"success": False, "error": "Invalid JSON in request body"},
                status=400
            )

        prompt = body.get("prompt", "").strip()
        prompt = normalize_tech_query(prompt)
        if not prompt:
            return JsonResponse(
                {"success": False, "error": "Prompt is required"},
                status=400
            )
            
        # -------------------------
# Tech-only validation (STRICT)
# -------------------------

        if not is_tech_query(prompt):
            alt_msg = get_alternative_suggestions()
            return JsonResponse({
                "success": False,
                "error": f"Only technology-related content is supported. {alt_msg}."
            }, status=400)

        # -------------------------
        # Determine User Level
        # -------------------------
        user_level = get_user_level(request.user)

        # -------------------------
        # AI Request
        # -------------------------
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "TechBrat Roadmap Generator",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "temperature": 0.4,
                "messages": [
                    {
                        "role": "system",
                        "content": f"""
You are an expert technical architect and educator.
Role: Generate a PRECISE and BROAD technical roadmap for a {user_level} learner.

CRITICAL RULES:
1. Content must be BROAD and EXPLAINED in great detail.
2. Formatting: Use PLAIN TEXT ONLY. Avoid any markdown symbols like **, ###, or triple backticks.
3. Structure: Present descriptions as a list of bullet points (one point per line starting with •).
4. Tailor the complexity and resources to a {user_level} level.
5. Return roadmap in valid JSON only.

STRICT JSON STRUCTURE (NO EXTRA TEXT):
{{
  "roadmap_title": "Comprehensive [Topic] Roadmap for {user_level}s",
  "steps": [
    {{
      "title": "Step Title",
      "description": "• Point 1: Broad detail.\\n• Point 2: Deep insight.\\n• Point 3: Practical application.",
      "resources": [
        {{
          "title": "Resource Name",
          "link": "Direct link to tutorial/documentation"
        }}
      ]
    }}
  ]
}}
"""
                    },
                    {"role": "user", "content": prompt}
                ],
            },
            timeout=25
        )

        # -------------------------
        # Parse AI Response
        # -------------------------
        try:
            raw = response.json()
        except Exception:
            return JsonResponse(
                {
                    "success": False,
                    "error": "AI returned non-JSON response",
                    "raw": response.text[:300],
                },
                status=500
            )

        if "choices" not in raw or not raw["choices"]:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid AI response structure",
                    "raw": raw,
                },
                status=500
            )

        try:
            content = raw["choices"][0]["message"]["content"]
            if not content:
                raise ValueError("Empty AI content")
            content = content.strip()
        except Exception:
            return JsonResponse(
                {
                    "success": False,
                    "error": "AI returned empty or malformed content",
                    "raw": raw,
                },
                status=500
            )

        # -------------------------
        # Clean AI Output
        # -------------------------
        content = content.replace("```json", "").replace("```", "").strip()

        # Ensure JSON starts properly
        json_start = content.find("{")
        if json_start != -1:
            content = content[json_start:]

        # -------------------------
        # Final JSON Parse Guard
        # -------------------------
        try:
            roadmap = json.loads(content, strict=False)
        except Exception:
            return JsonResponse(
                {
                    "success": False,
                    "error": "AI produced invalid JSON",
                    "raw_output": content[:400],
                },
                status=500
            )

        # -------------------------
        # Validate JSON Structure
        # -------------------------
        if (
            not isinstance(roadmap, dict)
            or "roadmap_title" not in roadmap
            or "steps" not in roadmap
            or not isinstance(roadmap["steps"], list)
        ):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid roadmap format",
                    "roadmap": roadmap,
                },
                status=500
            )

        # -------------------------
        # SUCCESS RESPONSE
        # -------------------------
        return JsonResponse(
            {
                "success": True,
                "data": roadmap
            },
            status=200
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "error": "Internal server error",
                "details": str(e),
            },
            status=500
        )


@csrf_exempt
def issue_assistance(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST only"},
            status=405
        )

    try:
        body = json.loads(request.body.decode("utf-8"))
        issue = body.get("issue", "").strip()
        issue = normalize_tech_query(issue)

        if not issue:
            return JsonResponse(
                {"error": "Issue text is required"},
                status=400
            )

        # ------------------------------------------------
        # TECH-ONLY VALIDATION (SAME AS ROADMAP)
        # ------------------------------------------------

        if not is_tech_query(issue):
            alt_msg = get_alternative_suggestions()
            return JsonResponse({
                "success": False,
                "error": f"Only technology-related content is supported. {alt_msg}."
            }, status=400)

        # ------------------------------------------------
        # CONTINUE WITH AI ASSISTANCE
        # ------------------------------------------------

        user_name = (
            request.user.first_name
            if request.user.is_authenticated
            else "Student"
        )
        user_level = get_user_level(request.user)

        system_prompt = f"""
You are a senior tech mentor.
Role: Provide deep, broad, and beginner-friendly assistance for technical issues.
Target Level: {user_level}

CRITICAL RULES:
1. Provide VERY EXPLAINED and BROAD content.
2. Formatting: Use PLAIN TEXT ONLY. Avoid any markdown symbols.
3. Structure: Use bullet points (•), one point per line.
4. Focus strictly on TECHNOLOGY / PROGRAMMING issues.

Return ONLY valid JSON in this exact format:
{{
  "issue_detected": "Brief technical issue name",
  "simple_explanation": "• Point 1 explaining why it happens.\n• Point 2 explaining the concept.",
  "alternative_learning": "• Alternative approach 1.\n• Alternative approach 2.",
  "practice_or_example": "• Practice tip 1.\n• Example idea.",
  "motivation_boost": "Encouraging advice for a {user_level} learner."
}}
"""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "temperature": 0.5,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Student Name: {user_name}\nIssue: {issue}",
                    },
                ],
            },
            timeout=25,
        )

        raw = response.json()

        if "choices" not in raw or not raw["choices"]:
            return JsonResponse(
                {"error": "AI response failed", "details": raw},
                status=500
            )

        content = raw["choices"][0]["message"]["content"]
        content = content.replace("```json", "").replace("```", "").strip()

        return JsonResponse(
            json.loads(content, strict=False),
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON from AI"},
            status=500
        )

    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)},
            status=500
        )


@csrf_exempt
def career_guidance(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        # prompt = body.get("prompt") # No longer receiving full prompt from frontend
        
        user_name = request.user.first_name if request.user.is_authenticated else "Student"
        user_level = get_user_level(request.user)
        education_level = body.get("education_level", "N/A")
        interests = body.get("interests", "N/A")
        skills = body.get("skills", "N/A")
        learning_style = body.get("learning_style", "N/A")
        career_goal = body.get("career_goal", "N/A")
        # -------------------------
# TECH-ONLY VALIDATION
# -------------------------

        combined_input = f"{interests} {skills} {career_goal}".strip()
        combined_input = normalize_tech_query(combined_input)

        if not is_tech_query(combined_input):
            alt_msg = get_alternative_suggestions()
            return JsonResponse({
                "success": False,
                "error": f"Only technology-related content is supported. {alt_msg}."
            }, status=400)

        system_prompt = f"""
You are an expert tech career advisor.
Role: Provide BROAD and DEEP career guidance for a {user_level} learner.

CRITICAL RULES:
1. ONLY analyze tech-related profiles. If interests, skills, or goals are non-technical, return: {{"error": "Our platform only provides guidance for tech-related careers."}}.

2. Content must be VERY EXPLAINED. Each recommendation should be a mini-essay but structured in points.
3. Formatting: Use PLAIN TEXT ONLY. Avoid any markdown symbols like **, ###, etc.
4. Structure: Use bullet points (•) for all long descriptions and roadmaps.
5. Tailor the advice precisely for a {user_level} level.

Return ONLY valid JSON in this exact format:
{{
  "recommended_careers": [
    {{
      "career_name": "Career Title",
      "simple_explanation": "• Deep industry role point 1.\n• Broad context point 2.",
      "why_suitable": "• Profile match point 1.\n• Skill alignment point 2.",
      "future_scope": "• Trend point 1.\n• Demand point 2.",
      "beginner_roadmap": ["• Detailed Step 1", "• Detailed Step 2", "• Detailed Step 3"],
      "beginner_resources": [
        {{ "title": "Resource Name", "type": "Course/Book/Documentation", "link": "URL" }}
      ]
    }}
  ]
}}
"""

        prompt = f"""
Student Profile:
Name: {user_name}
Assessed Level: {user_level}
Education Level: {education_level}
Interests: {interests}
Skills: {skills}
Learning Style: {learning_style}
Career Goal: {career_goal}
"""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "temperature": 0.5,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            },
        )

        raw = response.json()

        if "choices" not in raw:
            return JsonResponse({"error": "AI response failed", "details": raw}, status=500)

        content = raw["choices"][0]["message"]["content"]
        content = content.replace("```json", "").replace("```", "").strip()

        return JsonResponse(json.loads(content, strict=False))


    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON from AI"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required(login_url='techbrat:signin')
def profile(request):
    """Display and manage user profile"""
    profile = get_or_create_profile(request.user)
    
    if request.method == 'POST':
        # Handle profile updates
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # 1. Basic Academic Information
            profile.education_level = request.POST.get('education_level', profile.education_level)
            profile.current_course = request.POST.get('current_course', profile.current_course)
            profile.year_of_study = request.POST.get('year_of_study', profile.year_of_study)
            
            # 3. Domain Interests
            profile.tech_domains = request.POST.get('tech_domains', profile.tech_domains)
            profile.preferred_domain_work_type = request.POST.get('preferred_domain_work_type', profile.preferred_domain_work_type)
            
            # 4. Career Goals
            profile.career_objective = request.POST.get('career_objective', profile.career_objective)
            profile.target_timeline = request.POST.get('target_timeline', profile.target_timeline)
            profile.preferred_work_mode = request.POST.get('preferred_work_mode', profile.preferred_work_mode)
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('techbrat:profile')
        
        elif action == 'add_skill':
            skill_name = request.POST.get('skill_name')
            proficiency = request.POST.get('proficiency', 'intermediate')
            
            if skill_name:
                UserSkill.objects.get_or_create(
                    profile=profile,
                    skill_name=skill_name,
                    defaults={'proficiency': proficiency}
                )
                messages.success(request, 'Skill added successfully!')
            return redirect('techbrat:profile')
        
        elif action == 'delete_skill':
            skill_id = request.POST.get('skill_id')
            try:
                skill = UserSkill.objects.get(id=skill_id, profile=profile)
                skill.delete()
                messages.success(request, 'Skill removed successfully!')
            except UserSkill.DoesNotExist:
                pass
            return redirect('techbrat:profile')
        
    # Get related data and calculate completion percentage
    skills = profile.skills.all()
    completion = get_profile_completion(profile)
    
    context = {
        'profile': profile,
        'user': request.user,
        'skills': skills,
        'domains_list': get_user_domains(profile),
        'completion_percentage': completion,
        'education_level_choices': UserProfile.EDUCATION_LEVEL_CHOICES,
        'domain_work_type_choices': UserProfile.DOMAIN_WORK_TYPE_CHOICES,
        'career_objective_choices': UserProfile.CAREER_OBJECTIVE_CHOICES,
        'work_mode_choices': UserProfile.WORK_MODE_CHOICES,
        'skill_level_choices': UserSkill.SKILL_LEVEL_CHOICES,
    }
    
    return render(request, 'profile.html', context)


@login_required(login_url='techbrat:signin')
def courses(request):
    """
    Displays personalized course recommendations based on user profile and filters.
    """
    # Get user level and domains
    user_level = get_user_level(request.user)
    profile = get_or_create_profile(request.user)
    user_domains = get_user_domains(profile)
    
    # Base Queryset
    queryset = Course.objects.all()
    
    # Apply Personalization (Default behavior if no filters provided)
    level_filter = request.GET.get('level')
    domain_filter = request.GET.get('domain')
    free_filter = request.GET.get('free')
    
    is_filtered = any([level_filter, domain_filter, free_filter])
    
    if not is_filtered:
        # Default: Filter by user level
        queryset = queryset.filter(level=user_level)
        # If user has domains, try to match them
        if user_domains:
            # Simple intersection: show courses matching at least one domain
            from django.db.models import Q
            domain_query = Q()
            for domain in user_domains:
                domain_query |= Q(domain__icontains=domain)
            queryset = queryset.filter(domain_query)
    else:
        # Apply manual filters
        if level_filter:
            queryset = queryset.filter(level=level_filter)
        if domain_filter:
            queryset = queryset.filter(domain__icontains=domain_filter)
        if free_filter:
            is_free = free_filter.lower() == 'true'
            queryset = queryset.filter(is_free=is_free)
            
    # Get all unique domains for the filter dropdown
    all_domains = Course.objects.values_list('domain', flat=True).distinct()
    
    context = {
        'courses': queryset,
        'user_level': user_level,
        'domains': profile.tech_domains,
        'all_domains': all_domains,
        'selected_level': level_filter or (user_level if not is_filtered else ""),
        'selected_domain': domain_filter,
        'selected_free': free_filter,
        'is_personalized': not is_filtered
    }
    
    return render(request, 'courses.html', context)


@login_required(login_url='techbrat:signin')
def books(request):
    profile = get_or_create_profile(request.user)
    user_level = get_user_level(request.user)
    domains_list = get_user_domains(profile)
    goal = profile.get_career_objective_display()

    context = {
        'user_level': user_level,
        'domains_list': domains_list,
        'goal': goal,
        'level_choices': Book.LEVEL_CHOICES,
        'type_choices': Book.TYPE_CHOICES,
    }
    return render(request, 'books.html', context)


def _dedupe_books(books):
    seen = set()
    unique = []
    for b in books:
        key = (b['title'].strip().lower(), b['author'].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(b)
    return unique


def _ai_books(level, domains, goal):
    from django.conf import settings
    prompt = f"""
You are a tech learning advisor.

Recommend 5 high-quality REAL books based on:

User Level: {level}
Domains: {domains}
Career Goal: {goal}

IMPORTANT:
- ONLY tech-related books
- NO non-technical topics
- If domain is niche, return related tech books

Each book must include:
- title
- author
- level
- type (theory/practical/interview)
- reason (why recommended)
- link

Return ONLY JSON array.
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "temperature": 0.4,
                "messages": [
                    {"role": "system", "content": "Return only JSON array of books."},
                    {"role": "user", "content": prompt}
                ],
            },
            timeout=20,
        )
        raw = response.json()
        content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content, strict=False)
        books = []
        for item in data:
            books.append({
                "title": item.get("title", "").strip(),
                "author": item.get("author", "").strip(),
                "domain": domains if isinstance(domains, str) else ", ".join(domains),
                "level": item.get("level", "beginner"),
                "book_type": item.get("type", "theory"),
                "description": item.get("reason", ""),
                "link": item.get("link", ""),
                "is_ai_generated": True,
            })
        return _dedupe_books([b for b in books if b["title"] and b["author"]])
    except Exception:
        return []


@csrf_exempt
def book_recommendations(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST only"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    level = body.get("level", "beginner")
    domains = body.get("domains", [])
    goal = body.get("goal", "")

    domain_text = ", ".join(domains) if isinstance(domains, list) else str(domains)
    if not is_tech_query(domain_text):
        return JsonResponse({"success": False, "error": "🚫 Only technology-related books are supported. Try topics like AI, Web Development, or Databases."}, status=400)

    ai_books = _ai_books(level, domain_text, goal)
    return JsonResponse({"success": True, "data": ai_books}, status=200)


@csrf_exempt
def filter_books(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "GET only"}, status=405)

    level = request.GET.get("level")
    domain = request.GET.get("domain", "").strip()
    book_type = request.GET.get("type")

    if domain and not is_tech_query(domain):
        return JsonResponse({"success": False, "error": "🚫 Only technology-related books are supported. Try topics like AI, Web Development, or Databases."}, status=400)

    queryset = Book.objects.all()
    if level:
        queryset = queryset.filter(level=level)
    if domain:
        queryset = queryset.filter(domain__icontains=domain)
    if book_type:
        queryset = queryset.filter(book_type=book_type)

    db_books = list(queryset.values(
        "title", "author", "domain", "level", "book_type", "description", "link", "is_ai_generated"
    ))

    combined = db_books
    if len(db_books) < 4:
        ai_books = _ai_books(level or "beginner", domain or "technology", "")
        combined = _dedupe_books(db_books + ai_books)

    return JsonResponse({"success": True, "data": combined}, status=200)
@login_required(login_url='techbrat:signin')
def filter_courses(request):
    from .models import Course
    from .course_fetcher import fetch_external_courses, deduplicate_courses
    from django.db.models import Q
    from django.core.cache import cache
    import json
    import requests
    from django.conf import settings

    level = request.GET.get('level', 'beginner')
    domain = request.GET.get('domain', '')
    domain = normalize_tech_query(domain)
    learning_type = request.GET.get('learning_type', 'video')
    free = request.GET.get('free', 'true')

    is_free_bool = (free.lower() == 'true')

    if not is_tech_query(domain):
        alt_msg = get_alternative_suggestions()
        return JsonResponse({
            "success": False,
            "error": f"🚫 Only technology-related courses are supported. {alt_msg}."
        }, status=400)

    # ─── Cache Check ───────────────────────────────────
    cache_key = f"courses_{level}_{domain}_{learning_type}_{free}"
    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse({'success': True, 'courses': cached})

    # ─── Helper: serialize a DB queryset to list[dict] ──
    def serialize_queryset(qs, limit=15):
        result = []
        for course in qs[:limit]:
            result.append({
                'title': course.title,
                'platform': course.platform,
                'level': course.level,
                'level_display': course.get_level_display(),
                'domain': course.domain,
                'is_free': course.is_free,
                'learning_type': course.learning_type,
                'learning_type_display': course.get_learning_type_display(),
                'duration': course.duration,
                'link': course.link,
                'description': course.description,
                'is_ai': course.is_ai_generated,
                'is_external': course.is_external,
            })
        return result

    # ─── Helper: flexible domain filter (supports multi-word) ──
    domain_list = []
    if domain:
        domain_list = [d.strip() for d in domain.split(',') if d.strip()]

    def apply_domain_filter(qs):
        if domain_list:
            dq = Q()
            for d in domain_list:
                dq |= Q(domain__icontains=d)
                # Also search within title for broader matching
                dq |= Q(title__icontains=d)
            return qs.filter(dq)
        return qs

    # ─── STEP 1: Database Query (existing) ─────────────
    queryset = Course.objects.filter(
        level=level,
        learning_type=learning_type,
        is_free=is_free_bool
    )
    queryset = apply_domain_filter(queryset)
    db_courses = serialize_queryset(queryset, limit=15)

    # ─── STEP 2: External Fetch ────────────────────────
    # Trigger when DB returned < 6 results OR no results at all
    external_courses_raw = []
    if len(db_courses) < 6 or not queryset.exists():
        try:
            external_courses_raw = fetch_external_courses(
                level=level,
                domain=domain or 'technology',
                learning_type=learning_type,
                is_free=is_free_bool
            )

            # Save external courses to DB for future queries
            for course_data in external_courses_raw:
                if not Course.objects.filter(
                    title=course_data['title'],
                    platform=course_data['platform']
                ).exists():
                    try:
                        Course.objects.create(
                            title=course_data['title'],
                            platform=course_data['platform'],
                            domain=course_data.get('domain', ''),
                            level=course_data.get('level', level),
                            learning_type=course_data.get('learning_type', learning_type),
                            duration=course_data.get('duration', ''),
                            is_free=course_data.get('is_free', is_free_bool),
                            is_ai_generated=False,
                            is_external=True,
                            link=course_data.get('link', ''),
                            description=course_data.get('description', '')
                        )
                    except Exception:
                        continue

        except Exception as e:
            print(f"External course fetch failed: {e}")

    # ─── STEP 3: AI Fallback (enhanced) ────────────────
    # Re-query DB to include any newly saved external courses
    queryset = Course.objects.filter(
        level=level,
        learning_type=learning_type,
        is_free=is_free_bool
    )
    queryset = apply_domain_filter(queryset)

    # Track AI-generated courses for fallback guarantee
    ai_courses_raw = []

    if queryset.count() < 6 or not queryset.exists():

        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        model = getattr(settings, 'OPENROUTER_MODEL', 'google/gemini-2.0-flash-001')

        if api_key:

            free_or_paid = "Free" if is_free_bool else "Paid"
            domain_text = domain if domain else "general technology"

            prompt = f"""
You are a real-world tech course recommendation engine.

Your job is to find HIGH-QUALITY, REAL courses available on the internet.

User Requirements:
- Skill Level: {level}
- Domain: {domain_text}
- Learning Type: {learning_type}
- Pricing: {free_or_paid}

IMPORTANT RULES:
1. Return at least 6 courses ALWAYS. Never return an empty array.
2. Courses MUST be REAL and available online.
3. Prefer platforms:
   - Coursera
   - Udemy
   - FreeCodeCamp
   - edX
   - YouTube (for free courses)
   - Official documentation/tutorials
4. Links MUST be valid and usable.
5. DO NOT generate fake courses.
6. If exact domain courses are limited, return CLOSELY RELATED courses.
   Examples:
   - Redis → caching, backend optimization, databases
   - Kafka → streaming, distributed systems, event-driven architecture
   - Docker → containerization, DevOps, cloud deployment
   - GraphQL → API design, web services, backend development
7. You MUST always return data. An empty response is UNACCEPTABLE.

Return ONLY JSON ARRAY (no markdown):

[
  {{
    "title": "",
    "platform": "",
    "level": "{level}",
    "domain": "{domain_text}",
    "learning_type": "{learning_type}",
    "is_free": {str(is_free_bool).lower()},
    "duration": "",
    "description": "2-3 line explanation",
    "link": ""
  }}
]
"""

            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=15
                )

                if response.status_code == 200:

                    ai_content = response.json()['choices'][0]['message']['content']
                    ai_content = ai_content.replace("```json", "").replace("```", "").strip()

                    # Find JSON array start
                    arr_start = ai_content.find("[")
                    if arr_start != -1:
                        ai_content = ai_content[arr_start:]

                    ai_data = json.loads(ai_content)

                    if isinstance(ai_data, list):
                        ai_courses_raw = ai_data
                    else:
                        ai_courses_raw = []

                    for course_data in ai_courses_raw:
                        if not isinstance(course_data, dict):
                            continue
                        if not course_data.get('title') or not course_data.get('platform'):
                            continue
                        if not Course.objects.filter(
                            title=course_data['title'],
                            platform=course_data['platform']
                        ).exists():
                            try:
                                Course.objects.create(
                                    title=course_data['title'],
                                    platform=course_data['platform'],
                                    domain=course_data.get('domain', domain_text),
                                    level=course_data.get('level', level),
                                    learning_type=course_data.get('learning_type', learning_type),
                                    duration=course_data.get('duration', ''),
                                    is_free=course_data.get('is_free', is_free_bool),
                                    is_ai_generated=True,
                                    is_external=False,
                                    link=course_data.get('link', ''),
                                    description=course_data.get('description', '')
                                )
                            except Exception:
                                continue

                    # Re-run query AFTER saving
                    queryset = Course.objects.filter(
                        level=level,
                        learning_type=learning_type,
                        is_free=is_free_bool
                    )
                    queryset = apply_domain_filter(queryset)

                    # 🔥 FIX 2: Relax domain filter if it yields 0 results
                    if queryset.count() == 0:
                        queryset = Course.objects.filter(
                            level=level,
                            learning_type=learning_type,
                            is_free=is_free_bool
                        )

            except Exception as e:
                print("AI fallback failed:", str(e))

                # ─── Retry with simpler prompt ─────────────
                try:
                    simple_prompt = f"Generate 6 {free_or_paid.lower()} beginner courses for {domain_text}. Return ONLY JSON array with fields: title, platform, level, domain, learning_type, is_free, duration, description, link. No markdown."
                    retry_resp = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": simple_prompt}]
                        },
                        timeout=15
                    )
                    if retry_resp.status_code == 200:
                        retry_content = retry_resp.json()['choices'][0]['message']['content']
                        retry_content = retry_content.replace("```json", "").replace("```", "").strip()
                        arr_start = retry_content.find("[")
                        if arr_start != -1:
                            retry_content = retry_content[arr_start:]
                        retry_data = json.loads(retry_content)
                        if isinstance(retry_data, list):
                            ai_courses_raw = retry_data
                except Exception as retry_err:
                    print("AI retry also failed:", str(retry_err))

    # ─── STEP 4: Merge & Deduplicate ───────────────────
    all_courses = serialize_queryset(queryset, limit=20)

    # Add any external courses that didn't get saved
    for ext in external_courses_raw:
        all_courses.append({
            'title': ext.get('title', ''),
            'platform': ext.get('platform', ''),
            'level': ext.get('level', level),
            'level_display': level.capitalize(),
            'domain': ext.get('domain', ''),
            'is_free': ext.get('is_free', is_free_bool),
            'learning_type': ext.get('learning_type', learning_type),
            'learning_type_display': learning_type.replace('_', ' ').title(),
            'duration': ext.get('duration', ''),
            'link': ext.get('link', ''),
            'description': ext.get('description', ''),
            'is_ai': False,
            'is_external': True,
        })

    # ─── Fallback guarantee: if DB is STILL empty, return AI raw ──
    if len(all_courses) == 0 and ai_courses_raw:
        for c in ai_courses_raw:
            if isinstance(c, dict) and c.get('title'):
                all_courses.append({
                    'title': c.get('title', ''),
                    'platform': c.get('platform', ''),
                    'level': c.get('level', level),
                    'level_display': level.capitalize(),
                    'domain': c.get('domain', domain if domain else 'Technology'),
                    'is_free': c.get('is_free', is_free_bool),
                    'learning_type': c.get('learning_type', learning_type),
                    'learning_type_display': learning_type.replace('_', ' ').title(),
                    'duration': c.get('duration', ''),
                    'link': c.get('link', ''),
                    'description': c.get('description', ''),
                    'is_ai': True,
                    'is_external': False,
                })

    # Deduplicate and limit
    final_courses = deduplicate_courses(all_courses)[:15]

    # 🔥 FIX 3: FINAL SAFETY NET — user NEVER sees empty results
    if len(final_courses) == 0:
        final_courses = [
            {
                "title": f"Introduction to {domain or 'Technology'}",
                "platform": "YouTube / Web",
                "level": level,
                "level_display": level.capitalize(),
                "domain": domain or "Technology",
                "is_free": True,
                "learning_type": learning_type,
                "learning_type_display": learning_type.replace('_', ' ').title(),
                "duration": "Varies",
                "link": "https://www.youtube.com/results?search_query=" + (domain or "technology").replace(" ", "+"),
                "description": "Basic learning resources for the selected domain.",
                "is_ai": True,
                "is_external": False,
            }
        ]

    # 🔥 FIX 5: Debug logging for traceability
    print(f"[filter_courses] DB: {len(db_courses)} | External: {len(external_courses_raw)} | AI: {len(ai_courses_raw)} | Final: {len(final_courses)}")

    # ─── STEP 5: Cache & Return ────────────────────────
    # Only cache if we have results (avoid caching empty)
    if final_courses:
        cache.set(cache_key, final_courses, 600)  # 10 min TTL

    return JsonResponse({
        'success': True,
        'courses': final_courses
    })


# ═════════════ TOOLS & PLATFORMS PAGE ═════════════

def tools(request):
    """Display tools and platforms page."""
    from techbrat.models import Tool
    
    # Get category choices for filter
    categories = [choice[0] for choice in Tool.CATEGORY_CHOICES]
    difficulties = [choice[0] for choice in Tool.DIFFICULTY_CHOICES]
    use_cases = [choice[0] for choice in Tool.USE_CASE_CHOICES]
    
    return render(request, 'tools.html', {
        'categories': categories,
        'difficulties': difficulties,
        'use_cases': use_cases,
    })


@csrf_exempt
def filter_tools(request):
    """API endpoint for filtering and searching tools with AI fallback."""
    from techbrat.models import Tool
    from techbrat.tool_fetcher import is_query_tech_related, get_tools_hybrid
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    search_query = data.get('search', '').strip()
    category = data.get('category', 'all')
    difficulty = data.get('difficulty', 'all')
    use_case = data.get('use_case', 'all')
    
    # ── TECH VALIDATION ────────────────────────────
    if search_query:
        is_tech, error_msg = is_query_tech_related(search_query)
        if not is_tech:
            return JsonResponse({
                'success': False,
                'message': error_msg or 'This platform supports only technology-related tools and platforms.'
            })
    
    # ── FETCH TOOLS (HYBRID) ───────────────────────
    try:
        tools_data = get_tools_hybrid(
            category=category if category != 'all' else None,
            difficulty=difficulty if difficulty != 'all' else None,
            use_case=use_case if use_case != 'all' else None,
            search_query=search_query if search_query else None
        )
        
        return JsonResponse({
            'success': True,
            'tools': tools_data,
            'count': len(tools_data)
        })
    
    except Exception as e:
        print(f"Tools API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def tools_recommendations(request):
    """Get AI-generated tool recommendations."""
    from techbrat.tool_fetcher import generate_tools_via_ai
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    category = data.get('category')
    difficulty = data.get('difficulty')
    use_case = data.get('use_case')
    
    try:
        tools = generate_tools_via_ai(
            category=category,
            difficulty=difficulty,
            use_case=use_case,
            count=6
        )
        
        return JsonResponse({
            'success': True,
            'tools': tools,
            'generated': True
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═════════════ MOTIVATION & TIPS PAGE ═════════════

def motivation(request):
    """Display motivation and tips page."""
    from techbrat.models import Tip
    from techbrat.tip_fetcher import get_daily_tip, get_consistency_streak
    
    # Get category choices for filter
    categories = [choice[0] for choice in Tip.CATEGORY_CHOICES]
    
    # Get daily tip
    daily_tip = get_daily_tip()
    
    # Get consistency streak (for logged-in users)
    streak = 0
    if request.user.is_authenticated:
        streak, _ = get_consistency_streak(request.user)
    
    return render(request, 'motivation.html', {
        'categories': categories,
        'daily_tip': daily_tip,
        'streak': streak,
    })


@csrf_exempt
def filter_tips(request):
    """API endpoint for filtering and fetching tips."""
    from techbrat.models import Tip
    from techbrat.tip_fetcher import is_tip_tech_related, get_tips_hybrid
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    category = data.get('category', 'all')
    limit = min(int(data.get('limit', 5)), 10)  # Max 10 tips
    
    try:
        tips = get_tips_hybrid(
            category=category if category != 'all' else None,
            limit=limit
        )
        
        return JsonResponse({
            'success': True,
            'tips': tips,
            'count': len(tips)
        })
    
    except Exception as e:
        print(f"Tips API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def tips_recommendations(request):
    """Get AI-generated motivation tips."""
    from techbrat.tip_fetcher import generate_tips_via_ai
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    category = data.get('category')
    limit = min(int(data.get('limit', 5)), 10)
    
    try:
        tips = generate_tips_via_ai(
            category=category,
            count=limit
        )
        
        return JsonResponse({
            'success': True,
            'tips': tips,
            'generated': True,
            'count': len(tips)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


