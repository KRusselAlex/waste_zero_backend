from django.urls import path
from .views import (
    AdministratorListCreateView,
    AdministratorDetailView,
    AdministratorRoleListView,
    CurrentAdministratorView
)

urlpatterns = [
    # Administrator management endpoints (Super Admin only)
    path('administrators/', AdministratorListCreateView.as_view(), name='administrator_list_create'),
    path('administrators/<int:user_id>/', AdministratorDetailView.as_view(), name='administrator_detail'),
    
    # Administrator role and current user endpoints
    path('administrators/roles/', AdministratorRoleListView.as_view(), name='administrator_roles'),
    path('administrators/me/', CurrentAdministratorView.as_view(), name='current_administrator'),
]