from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

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

    @property
    def display_name(self):
        return self.title

    def get_absolute_url(self):
        return reverse('techbrat:course_detail', args=[self.pk])
    
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

    @property
    def display_name(self):
        return self.title

    def get_absolute_url(self):
        return reverse('techbrat:book_detail', args=[self.pk])


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

    @property
    def display_name(self):
        return self.name

    def get_absolute_url(self):
        return reverse('techbrat:tool_detail', args=[self.pk])


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

    @property
    def display_name(self):
        return self.title

    def get_absolute_url(self):
        return reverse('techbrat:tip_detail', args=[self.pk])


class SavedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'content_type', 'object_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} saved {self.content_type.app_label}.{self.content_type.model}:{self.object_id}'

    @property
    def item_title(self):
        obj = self.content_object
        if obj is None:
            return 'Unavailable item'
        return getattr(obj, 'title', None) or getattr(obj, 'name', None) or str(obj)


class CareerPathSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_path_snapshots')
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    fingerprint = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'fingerprint')

    def __str__(self):
        return self.title

    @property
    def display_name(self):
        return self.title

    def get_absolute_url(self):
        return reverse('techbrat:career_path_detail', args=[self.pk])


class RoadmapSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmap_snapshots')
    title = models.CharField(max_length=255)
    prompt = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    fingerprint = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'fingerprint')

    def __str__(self):
        return self.title

    @property
    def display_name(self):
        return self.title

    def get_absolute_url(self):
        return reverse('techbrat:roadmap_snapshot_detail', args=[self.pk])

    @property
    def step_count(self):
        roadmap = self.payload.get('roadmap', {})
        steps = roadmap.get('steps', [])
        return len(steps) if isinstance(steps, list) else 0

    @property
    def completed_steps_count(self):
        return self.step_progress.count()

    @property
    def completion_percentage(self):
        if not self.step_count:
            return 0
        return round((self.completed_steps_count / self.step_count) * 100)


class RoadmapStepProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmap_step_progress')
    snapshot = models.ForeignKey(RoadmapSnapshot, on_delete=models.CASCADE, related_name='step_progress')
    step_index = models.PositiveIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_index']
        unique_together = ('user', 'snapshot', 'step_index')
        indexes = [
            models.Index(fields=['user', 'snapshot']),
            models.Index(fields=['completed_at']),
        ]

    def __str__(self):
        return f'{self.user.username} completed step {self.step_index} for {self.snapshot.title}'


class LearningActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('roadmap_step_completed', 'Roadmap Step Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    activity_date = models.DateField(default=timezone.localdate)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-activity_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_date']),
            models.Index(fields=['activity_type']),
        ]

    def __str__(self):
        return f'{self.user.username} {self.activity_type} on {self.activity_date}'


class WeeklyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_goals')
    week_start = models.DateField()
    target_steps = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-week_start']
        unique_together = ('user', 'week_start')
        indexes = [
            models.Index(fields=['user', 'week_start']),
        ]

    def __str__(self):
        return f'{self.user.username} weekly goal for {self.week_start}'


class IssueAssistanceSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issue_assistance_snapshots')
    title = models.CharField(max_length=255)
    issue = models.TextField()
    summary = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    fingerprint = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'fingerprint')

    def __str__(self):
        return self.title

    @property
    def display_name(self):
        return self.title

    def get_absolute_url(self):
        return reverse('techbrat:issue_snapshot_detail', args=[self.pk])


class CompanyPrepSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_prep_snapshots')
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    fingerprint = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'fingerprint')

    def __str__(self):
        return self.title

    @property
    def display_name(self):
        return self.title

    def get_absolute_url(self):
        return reverse('techbrat:company_prep_detail', args=[self.pk])

