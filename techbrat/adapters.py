import logging

from django.conf import settings
from urllib.parse import urlsplit

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


logger = logging.getLogger(__name__)


class TechBratSocialAccountAdapter(DefaultSocialAccountAdapter):
    def on_authentication_error(
        self,
        request,
        provider,
        error=None,
        exception=None,
        extra_context=None,
    ):
        target_url = self._get_safe_redirect_target(request, extra_context)
        provider_name = getattr(provider, "name", "social provider")
        detail = self._get_error_detail(error, exception)

        logger.warning(
            "%s social sign-in failed%s",
            provider_name,
            f": {detail}" if detail else "",
            exc_info=exception if exception else None,
        )

        message = (
            f"{provider_name} sign-in could not be completed. Please try again from the sign-in page."
        )
        if settings.DEBUG and detail:
            message = f"{message} ({detail})"
        messages.error(request, message)
        raise ImmediateHttpResponse(redirect(target_url))

    def get_login_redirect_url(self, request):
        return reverse("techbrat:welcome")

    def _get_error_detail(self, error=None, exception=None):
        if exception:
            return exception.__class__.__name__
        if error:
            code = getattr(error, "value", error)
            return str(code)
        return ""

    def _get_safe_redirect_target(self, request, extra_context=None):
        state = (extra_context or {}).get("state") or {}
        candidates = [
            request.POST.get("next"),
            request.GET.get("next"),
            state.get("next"),
        ]

        allowed_hosts = {
            request.get_host(),
            request.get_host().split(":", 1)[0],
        }

        for candidate in candidates:
            if candidate and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts=allowed_hosts,
                require_https=request.is_secure(),
            ):
                return candidate

        return reverse("techbrat:signin")
