from django.contrib import admin
from .models import UserProfile, UserSkill, Course

# Register your models here.


class UserSkillInline(admin.TabularInline):
    model = UserSkill
    extra = 1


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'education_level', 'career_objective', 'updated_at')
    list_filter = ('education_level', 'career_objective', 'updated_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'current_course')
    inlines = [UserSkillInline]


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'profile', 'proficiency')
    list_filter = ('proficiency',)
    search_fields = ('skill_name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'domain', 'level', 'is_free', 'created_at')
    list_filter = ('domain', 'level', 'is_free', 'platform')
    search_fields = ('title', 'domain', 'platform', 'description')

