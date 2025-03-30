from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated, IsSuperAdmin
from utils.utils import format_response
from .models import Administrator
from .serializers import AdministratorSerializer


class AdministratorListCreateView(generics.ListCreateAPIView):
    """
    List all administrators or create a new administrator.
    Only accessible by super admins.
    """
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = [CustomIsAuthenticated, IsSuperAdmin]

    @swagger_auto_schema(
        operation_description="List all administrators (Super Admin only)",
        responses={
            200: AdministratorSerializer(many=True),
            401: "Unauthorized",
            403: "Forbidden - Super Admin access required",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Administrators retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving administrators",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Create a new administrator (Super Admin only)",
        request_body=AdministratorSerializer,
        responses={
            201: "Administrator created successfully",
            400: "Invalid input",
            401: "Unauthorized",
            403: "Forbidden - Super Admin access required",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Administrator created successfully",
                status_code=status.HTTP_201_CREATED,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="Administrator creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )


class AdministratorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an administrator.
    Only accessible by super admins.
    """
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = [CustomIsAuthenticated, IsSuperAdmin]
    lookup_field = 'user_id'

    @swagger_auto_schema(
        operation_description="Retrieve administrator details (Super Admin only)",
        responses={
            200: AdministratorSerializer(),
            401: "Unauthorized",
            403: "Forbidden - Super Admin access required",
            404: "Administrator not found",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Administrator details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Administrator not found'},
                message="Administrator not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Update administrator details (Super Admin only)",
        request_body=AdministratorSerializer,
        responses={
            200: "Administrator updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            403: "Forbidden - Super Admin access required",
            404: "Administrator not found",
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Administrator updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Administrator not found'},
                message="Administrator not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="Administrator update failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Partially update administrator details (Super Admin only)",
        request_body=AdministratorSerializer,
        responses={
            200: "Administrator updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            403: "Forbidden - Super Admin access required",
            404: "Administrator not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            response = super().partial_update(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Administrator updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Administrator not found'},
                message="Administrator not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="Administrator update failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Delete an administrator (Super Admin only)",
        responses={
            204: "Administrator deleted successfully",
            401: "Unauthorized",
            403: "Forbidden - Super Admin access required",
            404: "Administrator not found",
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
            return format_response(
                message="Administrator deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Administrator not found'},
                message="Administrator not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )


class AdministratorRoleListView(generics.GenericAPIView):
    """
    List all available administrator roles.
    Accessible by any administrator.
    """
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all available administrator roles",
        responses={
            200: "List of role choices",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            roles = [{'value': choice[0], 'display': choice[1]} 
                    for choice in Administrator.ROLE_CHOICES]
            return format_response(
                data=roles,
                message="Roles retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving roles",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class CurrentAdministratorView(generics.RetrieveAPIView):
    """
    Retrieve current logged-in administrator's details.
    """
    serializer_class = AdministratorSerializer
    permission_classes = [CustomIsAuthenticated]

    def get_object(self):
        return self.request.user.administrator

    @swagger_auto_schema(
        operation_description="Retrieve current administrator's details",
        responses={
            200: AdministratorSerializer(),
            401: "Unauthorized",
            404: "Administrator not found",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            if not hasattr(request.user, 'administrator'):
                return format_response(
                    errors={'detail': 'User is not an administrator'},
                    message="User is not an administrator",
                    status_code=status.HTTP_403_FORBIDDEN,
                    success=False
                )
                
            response = super().get(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Administrator details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving administrator details",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )