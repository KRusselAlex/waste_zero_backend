from rest_framework import permissions, exceptions

class CustomIsAuthenticated(permissions.BasePermission):
    """
    Custom permission to return a custom response if the user is not authenticated.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise exceptions.PermissionDenied({
                "error": "Authentication required. Please log in.",
                "success": False,
                "data": None
            })
        return True