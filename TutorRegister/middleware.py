from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        LOGIN_EXEMPT_URLS = ("auth/", "admin/", "verification/")
        if not request.user.is_authenticated:
            path = request.path_info.lstrip("/")
            if not any(path.startswith(allowed) for allowed in LOGIN_EXEMPT_URLS):
                return redirect("TutorRegister:login")
        return self.get_response(request)
