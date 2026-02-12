from django.contrib import admin
from .models import UserProfile, UserSkill, UserExperience

# Register your models here.


class UserSkillInline(admin.TabularInline):
    model = UserSkill
    extra = 1


class UserExperienceInline(admin.TabularInline):
    model = UserExperience
    extra = 1


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_status', 'location', 'updated_at')
    list_filter = ('current_status', 'updated_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    inlines = [UserSkillInline, UserExperienceInline]


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'profile', 'proficiency')
    list_filter = ('proficiency',)
    search_fields = ('skill_name',)


@admin.register(UserExperience)
class UserExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'profile', 'start_date', 'is_ongoing')
    list_filter = ('is_ongoing', 'start_date')
    search_fields = ('title', 'organization')
