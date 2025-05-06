from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework import status
from .utils import format_response
from rest_framework import permissions, exceptions



class CustomIsAuthenticated(permissions.BasePermission):
    """
    Custom permission to check if user is authenticated.
    Returns formatted response if not authenticated.
    """
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            raise exceptions.NotAuthenticated({  # Changed from PermissionDenied
                "error": "Authentication required",
                "success": False,
                "data": None
            })

        # Add this if you want to require verification for all authenticated access
        # if not request.user.is_verified:
        #     return format_response(
        #         message="Email verification required",
        #         errors={"auth": "Please verify your email address"},
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         success=False
        #     )
        return True


class IsAdminUser(CustomIsAuthenticated):
    """
    Permission that checks if the authenticated user is an administrator.
    """
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if request.user.role != 'administrator':
            response_data = format_response(
                message="Permission denied",
                errors={"permission": "Administrator access required"},
                status_code=status.HTTP_403_FORBIDDEN,
                success=False
            )
            raise PermissionDenied(detail=response_data)
        return True


class IsSelfOrAdmin(CustomIsAuthenticated):
    """
    Permission that checks if the authenticated user is accessing their own data or is an admin.
    """
    def has_object_permission(self, request, view, obj):
        super().has_permission(request, view)
        
        # Allow access if user is admin or accessing their own profile
        if request.user.role == 'administrator' or obj == request.user:
            return True
            
        response_data = format_response(
            message="Permission denied",
            errors={"permission": "You can only access your own data"},
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )
        raise PermissionDenied(detail=response_data)


class IsSuperAdmin(CustomIsAuthenticated):
    """
    Permission that checks if the authenticated user is a super admin.
    Returns formatted response if check fails.
    """
    def has_permission(self, request, view):
        super().has_permission(request, view)
        
        if not request.user.is_superuser:
            response_data = format_response(
                message="Permission denied",
                errors={"permission": "Super admin access required"},
                status_code=status.HTTP_403_FORBIDDEN,
                success=False
            )
            raise PermissionDenied(detail=response_data)
        return True


class IsAdminOrReadOnly(CustomIsAuthenticated):
    """
    Allows read access to any request but write access only to admin users.
    Returns formatted response if check fails.
    """
    def has_permission(self, request, view):
        super().has_permission(request, view)
        
        if request.method in permissions.SAFE_METHODS:
            return True
            
        if not request.user.is_staff:
            response_data = format_response(
                message="Permission denied",
                errors={"permission": "Admin access required for write operations"},
                status_code=status.HTTP_403_FORBIDDEN,
                success=False
            )
            raise PermissionDenied(detail=response_data)
        return True


class IsOwnerOrAdmin(CustomIsAuthenticated):
    """
    Only allows owners of an object or admins to edit it.
    Returns formatted response if check fails.
    """
    def has_object_permission(self, request, view, obj):
        super().has_permission(request, view)
        
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        if not hasattr(obj, 'user') or obj.user != request.user:
            response_data = format_response(
                message="Permission denied",
                errors={"permission": "You must be the owner or admin to perform this action"},
                status_code=status.HTTP_403_FORBIDDEN,
                success=False
            )
            raise PermissionDenied(detail=response_data)
        return True


class IsMerchantOwnerOrAdmin(CustomIsAuthenticated):
    """
    Permission that checks if the user is an admin or the merchant who created the offer.
    """
    def has_object_permission(self, request, view, obj):
        super().has_permission(request, view)
        
        # Admin can access any offer
        if request.user.role == 'administrator' or request.user.is_staff:
            return True
            
        # Merchant can only access their own offers
        if hasattr(obj, 'merchant') and obj.merchant == request.user:
            return True
            
        response_data = format_response(
            message="Permission denied",
            errors={"permission": "You can only access your own offers"},
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )
        raise PermissionDenied(detail=response_data)




class IsDonationOwnerOrAdmin(CustomIsAuthenticated):
    """
    Permission that checks if the user is an admin or involved in the donation
    (either as donor or recipient).
    """
    def has_object_permission(self, request, view, obj):
        super().has_permission(request, view)
        
        # Admin can access any donation
        if request.user.role == 'administrator' or request.user.is_staff:
            return True
            
        # User can access if they're the donor or recipient
        if obj.donor == request.user or (obj.recipient and obj.recipient == request.user):
            return True
            
        response_data = format_response(
            message="Permission denied",
            errors={"permission": "You can only access your own donations"},
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )
        raise PermissionDenied(detail=response_data)