from rest_framework import generics, status, filters
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from utils.utils import format_response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateView(generics.ListCreateAPIView):
    """
    List all notifications or create a new notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['notification_date', 'created_at', 'type', 'status']
    ordering = ['-notification_date']  # Default ordering is newest first

    def get_queryset(self):
        return Notification.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new notification.",
        request_body=NotificationSerializer,
        responses={
            201: "Notification created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            multiple = isinstance(request.data, list)  # Check if the request contains a list
            serializer = NotificationSerializer(data=request.data, many=multiple)

            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Notification created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            return format_response(
                errors=serializer.errors,
                message="Notification creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating notification.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all notifications with optional filtering.",
        responses={
            200: NotificationSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            user_id = request.query_params.get('user', None)
            type_filter = request.query_params.get('type', None)
            status_filter = request.query_params.get('status', None)
            
            # Apply filters if provided
            queryset = self.get_queryset()
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            if type_filter:
                queryset = queryset.filter(type=type_filter)
                
            if status_filter:
                queryset = queryset.filter(status=status_filter)
                
            # Apply ordering from filter_backends
            queryset = self.filter_queryset(queryset)
            
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Notifications retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving notifications.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a notification.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific notification by ID.",
        responses={
            200: NotificationSerializer(),
            401: "Unauthorized",
            404: "Notification not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except Http404:
            return format_response(
                errors={'detail': 'Notification not found'},
                message="Notification not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Notification details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Update a notification by ID.",
        request_body=NotificationSerializer,
        responses={
            200: "Notification updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Notification not found",
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
        except Exception as error:
            return format_response(
                errors={'detail': str(error)},
                message="There is an error",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Notification updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Delete a notification by ID.",
        responses={
            204: "Notification deleted successfully",
            401: "Unauthorized",
            404: "Notification not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            
            if response.status_code == 204:
                return format_response(
                    message="Notification deleted successfully",
                    status_code=status.HTTP_204_NO_CONTENT,
                    success=True
                )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="Database error",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )


class UserNotificationsView(generics.ListAPIView):
    """
    Retrieve all notifications for a specific user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['notification_date', 'created_at', 'type', 'status']
    ordering = ['-notification_date']
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Notification.objects.filter(user_id=user_id)

    @swagger_auto_schema(
        operation_description="Retrieve all notifications for a specific user ID.",
        responses={
            200: NotificationSerializer(many=True),
            401: "Unauthorized",
            404: "User not found or has no notifications",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            if not queryset.exists():
                return format_response(
                    data=[],
                    message="No notifications found for this user",
                    status_code=status.HTTP_200_OK,
                    success=True
                )
                
            # Apply optional type filter if provided
            type_filter = request.query_params.get('type', None)
            if type_filter:
                queryset = queryset.filter(type=type_filter)
                
            # Apply optional status filter if provided
            status_filter = request.query_params.get('status', None)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
                
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="User notifications retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class NotificationStatusUpdateView(generics.UpdateAPIView):
    """
    Update a notification's status (e.g., mark as read).
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a notification's status by ID.",
        responses={
            200: "Notification status updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Notification not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            notification = self.get_object()
            
            if 'status' not in request.data:
                return format_response(
                    errors={'status': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Check if status is valid
            status_value = request.data['status']
            valid_statuses = [status for status, _ in Notification.STATUS_CHOICES]
            
            if status_value not in valid_statuses:
                return format_response(
                    errors={'status': f'Must be one of: {", ".join(valid_statuses)}'},
                    message="Invalid status value",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            notification.status = status_value
            notification.save()
            
            serializer = self.get_serializer(notification)
            return format_response(
                data=serializer.data,
                message="Notification status updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Notification not found'},
                message="Notification not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating notification status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class MarkAllUserNotificationsReadView(generics.GenericAPIView):
    """
    Mark all notifications for a user as read.
    """
    permission_classes = [CustomIsAuthenticated]
    serializer_class = NotificationSerializer
    
    @swagger_auto_schema(
        operation_description="Mark all notifications for a specific user as read.",
        responses={
            200: "All notifications marked as read",
            401: "Unauthorized",
            404: "User not found",
        }
    )
    def post(self, request, user_id):
        try:
            # Find all unread notifications for the user
            unread_notifications = Notification.objects.filter(
                user_id=user_id,
                status='sent'
            )
            
            if not unread_notifications.exists():
                return format_response(
                    message="No unread notifications found for this user",
                    status_code=status.HTTP_200_OK,
                    success=True
                )
                
            # Update all to read status
            count = unread_notifications.count()
            unread_notifications.update(status='read')
            
            return format_response(
                data={'count': count},
                message=f"{count} notifications marked as read",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )