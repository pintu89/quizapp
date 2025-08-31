# home/middleware.py
from django.shortcuts import redirect

class RestrictAccessMiddleware:
    """
    Only specified paths are public.
    All other views require Django admin login or player session.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_paths = ['/', '/login/', '/favicon.ico', '/static/']

        if any(request.path.startswith(p) for p in public_paths):
            return self.get_response(request)

        # Admin access
        if request.user.is_authenticated and request.user.is_superuser:
            print("User Login as Admin")
            return self.get_response(request)

        # Player access
        if request.session.get("player_id"):
            print("User Login as Player")
            return self.get_response(request)

        # Redirect unauthenticated users
        print(" ❌ Unauthenticated access attempt")
        return redirect("login")
