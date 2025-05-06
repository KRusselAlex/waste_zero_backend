from django.urls import path
from .views import (
    AllDonationsListView,
    DonationListCreateView,
    DonationDetailView,
    DonationStatusUpdateView,
    UserDonationsMadeView,
    AvailableDonationsView,
    ReserveDonationView
)

urlpatterns = [
    # Public endpoints
    path('donations/all/', AllDonationsListView.as_view(), name='all-donations-list'),
    path('donations/available/', AvailableDonationsView.as_view(), name='available-donations'),
    
    # Donation management endpoints
    path('donations/', DonationListCreateView.as_view(), name='donation-list-create'),
    path('donations/<int:pk>/', DonationDetailView.as_view(), name='donation-detail'),
    path('donations/<int:pk>/status/', DonationStatusUpdateView.as_view(), name='donation-status-update'),
    path('donations/<int:pk>/reserve/', ReserveDonationView.as_view(), name='donation-reserve'),
    
    # User-specific endpoints
    path('users/<int:donor_id>/donations/', UserDonationsMadeView.as_view(), name='user-donations-made'),
]