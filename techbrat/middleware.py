from django.conf import settings
from django.http import HttpResponseRedirect


class CanonicalLocalhostMiddleware:
    LOCAL_ALIASES = {"127.0.0.1", "localhost"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        redirect_response = self._build_redirect_response(request)
        if redirect_response is not None:
            return redirect_response
        return self.get_response(request)

    def _build_redirect_response(self, request):
        site_domain = (getattr(settings, "SITE_DOMAIN", "") or "").strip()
        if not site_domain or site_domain.lower() == "example.com":
            return None
        if request.path.startswith('/accounts/'):
            return None
        current_host = request.get_host()
        current_name, _, current_port = current_host.partition(":")
        target_name, _, target_port = site_domain.partition(":")

        current_name = current_name.lower()
        target_name = target_name.lower()

        if (
            current_name not in self.LOCAL_ALIASES
            or target_name not in self.LOCAL_ALIASES
            or current_name == target_name
        ):
            return None

        target_host = target_name
        resolved_port = target_port or current_port
        if resolved_port:
            target_host = f"{target_host}:{resolved_port}"

        return HttpResponseRedirect(
            f"{request.scheme}://{target_host}{request.get_full_path()}"
        )
