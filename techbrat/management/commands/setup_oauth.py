from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Setup Google and GitHub OAuth apps'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        site.domain = settings.SITE_DOMAIN
        site.name = settings.SITE_NAME
        site.save(update_fields=['domain', 'name'])

        self.stdout.write(self.style.SUCCESS(f'Site configured as {site.domain}'))

        self.sync_provider(
            provider='google',
            name='Google',
            client_id=settings.GOOGLE_CLIENT_ID,
            secret=settings.GOOGLE_CLIENT_SECRET,
            site=site,
        )
        self.sync_provider(
            provider='github',
            name='GitHub',
            client_id=settings.GITHUB_CLIENT_ID,
            secret=settings.GITHUB_CLIENT_SECRET,
            site=site,
        )

        self.stdout.write(self.style.SUCCESS('\nOAuth setup complete'))

    def sync_provider(self, provider, name, client_id, secret, site):
        if not client_id or not secret:
            self.stdout.write(self.style.WARNING(f'{name} credentials not configured'))
            return

        app, created = SocialApp.objects.get_or_create(
            provider=provider,
            defaults={
                'name': name,
                'client_id': client_id,
                'secret': secret,
            },
        )

        updated_fields = []
        if app.name != name:
            app.name = name
            updated_fields.append('name')
        if app.client_id != client_id:
            app.client_id = client_id
            updated_fields.append('client_id')
        if app.secret != secret:
            app.secret = secret
            updated_fields.append('secret')
        if updated_fields:
            app.save(update_fields=updated_fields)

        if not app.sites.filter(id=site.id).exists():
            app.sites.add(site)

        status = 'created' if created else 'synced'
        self.stdout.write(self.style.SUCCESS(f'{name} OAuth app {status}'))
