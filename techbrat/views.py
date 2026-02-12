from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def index(request):
    # If user is not authenticated, show landing page
    if not request.user.is_authenticated:
        return render(request, 'landing.html')
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
    
    return render(request, 'landing.html')

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
            return render(request, 'landing.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'landing.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'landing.html')
        
        # Create new user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=fullname
            )
            user.save()
            
            # Auto-login after signup
            login(request, user)
            return redirect('techbrat:welcome')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'landing.html')

def welcome(request):
    if not request.user.is_authenticated:
        return redirect('techbrat:signin')
    return render(request, 'welcome.html')

def signout(request):
    logout(request)
    messages.success(request, 'You have been signed out successfully!')
    return redirect('techbrat:index')

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

def get_user_level(user):
    """
    Determines user experience level (beginner, intermediate, advanced)
    based on their profile and activity.
    """
    if not user.is_authenticated:
        return "beginner"
    
    from .models import UserProfile, UserSkill, UserExperience
    
    try:
        profile = user.profile
        
        # 1. Check current status
        if profile.current_status == 'working_professional':
            base_score = 2
        elif profile.current_status == 'college_student':
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
                
        # 3. Check experience
        experience_count = profile.experiences.count()
        if experience_count >= 3:
            base_score += 2
        elif experience_count >= 1:
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
        if not prompt:
            return JsonResponse(
                {"success": False, "error": "Prompt is required"},
                status=400
            )
            
        # -------------------------
# Tech-only validation (STRICT)
# -------------------------


# 1️⃣ Hard block obvious non-tech topics
        if is_obviously_non_tech(prompt):
            return JsonResponse(
            {
                "success": False,
                "error": "This platform supports only technology-related roadmaps."
            },
                status=400
            )

# 2️⃣ AI-based classification (flexible)
        if not ai_is_tech_related(prompt):
            return JsonResponse(
            {
               "success": False,
               "error": "Your input does not appear to be technology-related."
            },
            status=400
            )


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

        if not issue:
            return JsonResponse(
                {"error": "Issue text is required"},
                status=400
            )

        # ------------------------------------------------
        # TECH-ONLY VALIDATION (SAME AS ROADMAP)
        # ------------------------------------------------

        # 1️⃣ Hard block obvious non-tech issues
        if is_obviously_non_tech(issue):
            return JsonResponse(
                {
                    "error": "This feature supports only technology-related learning issues."
                },
                status=400
            )

        # 2️⃣ AI-based classification (flexible)
        if not ai_is_tech_related(issue):
            return JsonResponse(
                {
                    "error": "Your issue does not appear to be related to technology or programming."
                },
                status=400
            )

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

# 1️⃣ Hard block obvious non-tech
        if is_obviously_non_tech(combined_input):
            return JsonResponse(
            {
             "error": "This platform provides guidance only for technology-related careers."
            },
            status=400
            )

# 2️⃣ AI-based classification (flexible & future-proof)
        # if not ai_is_tech_related(combined_input):
        #     return JsonResponse(
        #     {
        #       "error": "Your career interests do not appear to be related to technology or IT."
        #     },
        #     status=400
        #     )


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
    from .models import UserProfile, UserSkill, UserExperience
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle profile updates
        action = request.POST.get('action')
        
        if action == 'update_profile':
            profile.location = request.POST.get('location', profile.location)
            profile.current_status = request.POST.get('current_status', profile.current_status)
            profile.bio = request.POST.get('bio', profile.bio)
            
            # Education
            profile.highest_qualification = request.POST.get('highest_qualification', profile.highest_qualification)
            profile.institution = request.POST.get('institution', profile.institution)
            profile.field_of_study = request.POST.get('field_of_study', profile.field_of_study)
            profile.current_year = request.POST.get('current_year', profile.current_year)
            
            cgpa = request.POST.get('cgpa')
            if cgpa:
                try:
                    profile.cgpa = float(cgpa)
                except ValueError:
                    pass
            
            # Interests
            profile.career_interests = request.POST.get('career_interests', profile.career_interests)
            profile.subject_interests = request.POST.get('subject_interests', profile.subject_interests)
            profile.preferred_work_type = request.POST.get('preferred_work_type', profile.preferred_work_type)
            
            # Career Preferences
            profile.preferred_locations = request.POST.get('preferred_locations', profile.preferred_locations)
            profile.salary_expectation = request.POST.get('salary_expectation', profile.salary_expectation)
            
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
        
        elif action == 'add_experience':
            title = request.POST.get('title')
            organization = request.POST.get('organization')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            is_ongoing = request.POST.get('is_ongoing') == 'on'
            
            if title and start_date:
                UserExperience.objects.create(
                    profile=profile,
                    title=title,
                    organization=organization,
                    description=description,
                    start_date=start_date,
                    end_date=end_date if end_date else None,
                    is_ongoing=is_ongoing
                )
                messages.success(request, 'Experience added successfully!')
            return redirect('techbrat:profile')
        
        elif action == 'delete_experience':
            exp_id = request.POST.get('exp_id')
            try:
                exp = UserExperience.objects.get(id=exp_id, profile=profile)
                exp.delete()
                messages.success(request, 'Experience removed successfully!')
            except UserExperience.DoesNotExist:
                pass
            return redirect('techbrat:profile')
    
    # Get all related data
    skills = profile.skills.all()
    experiences = profile.experiences.all()
    
    context = {
        'profile': profile,
        'user': request.user,
        'skills': skills,
        'experiences': experiences,
        'status_choices': UserProfile.STATUS_CHOICES,
        'skill_level_choices': UserProfile.SKILL_LEVEL_CHOICES,
        'work_type_choices': UserProfile.WORK_TYPE_CHOICES,
    }
    
    return render(request, 'profile.html', context)
