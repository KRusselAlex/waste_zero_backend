from django.urls import path
from .views import (
    NotificationListCreateView,
    NotificationDetailView,
    UserNotificationsView,
    NotificationStatusUpdateView,
    MarkAllUserNotificationsReadView
)

urlpatterns = [
    # Notification CRUD endpoints
    path('notifications/', NotificationListCreateView.as_view(), name='notification_list_create'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
    
    # Notification status management
    path('notifications/<int:pk>/status/', NotificationStatusUpdateView.as_view(), name='notification_status_update'),
    
    # User-specific notification endpoints
    path('users/<int:user_id>/notifications/', UserNotificationsView.as_view(), name='user_notifications'),
    path('users/<int:user_id>/notifications/mark-read/', MarkAllUserNotificationsReadView.as_view(), name='mark_all_notifications_read'),
]