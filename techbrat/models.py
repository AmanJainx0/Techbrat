from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    """Extended user profile with structured career guidance data"""
    
    EDUCATION_LEVEL_CHOICES = [
        ('school', 'School (K-12)'),
        ('intermediate', 'Intermediate (10+2)'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('doctorate', 'Doctorate'),
    ]
    
    DOMAIN_WORK_TYPE_CHOICES = [
        ('development', 'Development'),
        ('analytical', 'Analytical'),
        ('research', 'Research'),
        ('creative_ui', 'Creative UI'),
        ('security', 'Security'),
    ]
    
    CAREER_OBJECTIVE_CHOICES = [
        ('job', 'Job'),
        ('startup', 'Startup'),
        ('freelancing', 'Freelancing'),
        ('higher_studies', 'Higher Studies'),
    ]
    
    WORK_MODE_CHOICES = [
        ('remote', 'Remote'),
        ('on_site', 'On-site'),
        ('hybrid', 'Hybrid'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 1. Basic Academic Information
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, default='undergraduate')
    current_course = models.CharField(max_length=100, blank=True, help_text="e.g., B.Tech in Computer Science")
    year_of_study = models.CharField(max_length=50, blank=True, help_text="e.g., 3rd Year")
    
    # 2. Technical Skills (Handled by UserSkill model)
    # 3. Domain Interests
    tech_domains = models.TextField(blank=True, help_text="Comma-separated tech domains (AI/ML, Web Dev, etc.)")
    preferred_domain_work_type = models.CharField(max_length=20, choices=DOMAIN_WORK_TYPE_CHOICES, default='development')
    
    # 4. Career Goals
    career_objective = models.CharField(max_length=20, choices=CAREER_OBJECTIVE_CHOICES, default='job')
    target_timeline = models.CharField(max_length=100, blank=True, help_text="e.g., Within 6 months")
    preferred_work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default='remote')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
    
    class Meta:
        ordering = ['-updated_at']



class UserSkill(models.Model):
    """User skills with proficiency levels"""
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='intermediate')
    
    class Meta:
        unique_together = ('profile', 'skill_name')
        ordering = ['skill_name']
    
    def __str__(self):
        return f"{self.skill_name} - {self.proficiency}"


class Course(models.Model):
    """Platform-curated courses for users"""
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    LEARNING_TYPE_CHOICES = [
        ('video', 'Video Based'),
        ('text', 'Text Based'),
        ('interactive', 'Interactive Coding'),
        ('project', 'Project Based'),
    ]
    
    title = models.CharField(max_length=255)
    platform = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, help_text="e.g., AI/ML, Web Development")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    learning_type = models.CharField(max_length=20, choices=LEARNING_TYPE_CHOICES, default='video')
    duration = models.CharField(max_length=50, help_text="e.g., 10 hours, 4 weeks")
    is_free = models.BooleanField(default=True)
    is_ai_generated = models.BooleanField(default=False)
    is_external = models.BooleanField(default=False)
    link = models.URLField(max_length=500)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['domain']),
            models.Index(fields=['learning_type']),
            models.Index(fields=['is_free']),
        ]


class Book(models.Model):
    """Curated and AI-generated tech books"""

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    TYPE_CHOICES = [
        ('theory', 'Theory'),
        ('practical', 'Practical'),
        ('interview', 'Interview Prep'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    book_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='theory')
    description = models.TextField()
    link = models.URLField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['domain']),
            models.Index(fields=['book_type']),
            models.Index(fields=['is_ai_generated']),
        ]

    def __str__(self):
        return f"{self.title} - {self.author}"


class Tool(models.Model):
    """Tech tools and platforms for learning and development"""

    CATEGORY_CHOICES = [
        ('development', 'Development'),
        ('version_control', 'Version Control'),
        ('practice_platform', 'Practice Platform'),
        ('design', 'Design'),
        ('devops', 'DevOps'),
        ('ai_tools', 'AI Tools'),
        ('databases', 'Databases'),
        ('api_tools', 'API Tools'),
        ('cloud', 'Cloud Platform'),
        ('ci_cd', 'CI/CD'),
        ('collaboration', 'Collaboration'),
        ('other', 'Other'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all', 'All Levels'),
    ]

    USE_CASE_CHOICES = [
        ('learning', 'Learning'),
        ('practice', 'Practice'),
        ('production', 'Production'),
        ('all', 'All'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    use_case = models.CharField(max_length=50, choices=USE_CASE_CHOICES, default='all')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='all')
    link = models.URLField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['use_case']),
            models.Index(fields=['is_ai_generated']),
        ]

    def __str__(self):
        return self.name


class Tip(models.Model):
    """Daily motivation and actionable tips for tech learners"""

    CATEGORY_CHOICES = [
        ('productivity', 'Productivity'),
        ('learning_strategy', 'Learning Strategy'),
        ('coding_practice', 'Coding Practice'),
        ('career_growth', 'Career Growth'),
        ('consistency', 'Consistency'),
        ('mindset', 'Mindset'),
    ]

    title = models.CharField(max_length=200)
    explanation = models.TextField()
    action_step = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='productivity')
    icon = models.CharField(max_length=50, default='fa-lightbulb', help_text="Font Awesome icon class")
    is_ai_generated = models.BooleanField(default=False)
    daily_boost = models.BooleanField(default=False, help_text="Show in hero section as daily motivation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_ai_generated']),
            models.Index(fields=['daily_boost']),
        ]

    def __str__(self):
        return self.title

