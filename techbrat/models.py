from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    """Extended user profile with career and education information"""
    
    STATUS_CHOICES = [
        ('student', 'Student'),
        ('college_student', 'College Student'),
        ('working_professional', 'Working Professional'),
    ]
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    WORK_TYPE_CHOICES = [
        ('office', 'Office'),
        ('remote', 'Remote'),
        ('field', 'Field'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile Overview
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='student')
    bio = models.TextField(blank=True, max_length=500)
    
    # Education
    highest_qualification = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=150, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    current_year = models.CharField(max_length=50, blank=True)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Interests
    career_interests = models.TextField(blank=True, help_text="Comma-separated career interests")
    subject_interests = models.TextField(blank=True, help_text="Comma-separated subject interests")
    preferred_work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default='office', blank=True)
    
    # Career Preferences
    preferred_locations = models.TextField(blank=True, help_text="Comma-separated preferred locations")
    salary_expectation = models.CharField(max_length=100, blank=True)
    
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


class UserExperience(models.Model):
    """User internships and projects"""
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=150)
    organization = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_ongoing = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} at {self.organization}"
