# accounts/urls.py
from django.urls import path
from .views import RegisterView, LoginView, UserDetailView,UserListView,VerifyEmailView,ResendVerificationEmailView
from rest_framework_simplejwt.views import TokenRefreshView




urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('users/', UserListView.as_view(), name='all-users'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]