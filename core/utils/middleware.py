from rest_framework.exceptions import PermissionDenied

class CheckVerifiedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated and 
            not request.user.is_verified and
            request.path not in ['/auth/verify-email/', '/auth/login/', '/auth/register/']):
            raise PermissionDenied("Please verify your email address first")
        return self.get_response(request)