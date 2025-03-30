from django.urls import path
from .views import (
    MerchantCreateView,
    MerchantDetailView,
    MerchantVerificationView,
    MerchantPriceLimitView
)

urlpatterns = [
    # Merchant CRUD endpoints
    path('merchants/', MerchantCreateView.as_view(), name='merchant_list_create'),
    path('merchants/<int:pk>/', MerchantDetailView.as_view(), name='merchant_detail'),
    
    # Merchant management endpoints
    path('merchants/<int:pk>/verify/', MerchantVerificationView.as_view(), name='merchant_verify'),
    path('merchants/<int:pk>/price-limit/', MerchantPriceLimitView.as_view(), name='merchant_price_limit'),
]