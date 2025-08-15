from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """
    Force login for all views except those explicitly excluded.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            settings.LOGIN_URL.lstrip('/'),
            'admin/',
            'static/',  # Allow static files
        ]

    def __call__(self, request):
        if not request.user.is_authenticated and not any(request.path.startswith('/' + url) for url in self.exempt_urls):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
