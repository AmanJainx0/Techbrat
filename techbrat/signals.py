from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_updated, pre_social_login
from django.contrib.auth.models import User
from techbrat.models import UserProfile


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """Create or update user profile when user is created or updated."""
    if created:
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        if not profile.education_level:
            profile.education_level = 'undergraduate'
            profile.save()


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """Link social account to existing local user if email matches."""
    if sociallogin.is_existing:
        return

    try:
        email = sociallogin.account.extra_data.get('email', '')
        if email:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
    except User.DoesNotExist:
        pass


@receiver(social_account_updated)
def on_social_account_updated(sender, request, sociallogin, **kwargs):
    """Handle social account updates and ensure profile exists."""
    user = sociallogin.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Update first name if not already set
    if not user.first_name and 'name' in sociallogin.account.extra_data:
        user.first_name = sociallogin.account.extra_data['name']
        user.save()
    
    # Ensure profile has basic setup
    if not profile.education_level:
        profile.education_level = 'undergraduate'
        profile.save()
