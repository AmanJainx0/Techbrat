from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup Google and GitHub OAuth apps'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        
        # Setup Google OAuth
        if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'secret': settings.GOOGLE_CLIENT_SECRET,
                }
            )
            if not google_app.sites.filter(id=site.id).exists():
                google_app.sites.add(site)
            
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Google OAuth app created'))
            else:
                self.stdout.write(self.style.SUCCESS('✓ Google OAuth app already exists'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Google credentials not configured'))

        # Setup GitHub OAuth
        if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
            github_app, created = SocialApp.objects.get_or_create(
                provider='github',
                defaults={
                    'name': 'GitHub',
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'secret': settings.GITHUB_CLIENT_SECRET,
                }
            )
            if not github_app.sites.filter(id=site.id).exists():
                github_app.sites.add(site)
            
            if created:
                self.stdout.write(self.style.SUCCESS('✓ GitHub OAuth app created'))
            else:
                self.stdout.write(self.style.SUCCESS('✓ GitHub OAuth app already exists'))
        else:
            self.stdout.write(self.style.WARNING('⚠ GitHub credentials not configured'))

        self.stdout.write(self.style.SUCCESS('\n✓ OAuth setup complete!'))
