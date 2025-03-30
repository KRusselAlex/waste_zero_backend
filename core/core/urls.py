"""
core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="0Waste Api",
      default_version='v1',
      description="API 0Waste management",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@myapi.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.deployment_status, name='deployment_status'),
    
    # API v1 endpoints
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('merchants.urls')),
    path('api/v1/', include('consumers.urls')),
    path('api/v1/', include('donations.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('offers.urls')),
    path('api/v1/', include('points.urls')),
    path('api/v1/', include('reviews.urls')),
    path('api/v1/', include('transactions.urls')),
    path('api/v1/', include('administrators.urls')),
    path('api/v1/', include('categories.urls')),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-docs'),
]