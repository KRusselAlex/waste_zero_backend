from django.urls import path
from .views import (
    OfferListCreateView,
    OfferDetailView,
    OfferStatusUpdateView,
    MerchantOffersView,
    ActiveOffersView
)

urlpatterns = [
    # Offer CRUD endpoints
    path('offers/', OfferListCreateView.as_view(), name='offer_list_create'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer_detail'),
    
    # Offer status management
    path('offers/<int:pk>/status/', OfferStatusUpdateView.as_view(), name='offer_status_update'),
    
    # Merchant-specific offers
    path('merchants/<int:merchant_id>/offers/', MerchantOffersView.as_view(), name='merchant_offers'),
    
    # Special offer listings
    path('offers/active/', ActiveOffersView.as_view(), name='active_offers'),
]