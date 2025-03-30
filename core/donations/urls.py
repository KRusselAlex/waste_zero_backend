from django.urls import path
from .views import (
    DonationListCreateView,
    DonationDetailView,
    DonationStatusUpdateView,
    UserDonationsMadeView,
    UserDonationsReceivedView,
    AvailableDonationsView,
    ReserveDonationView
)

urlpatterns = [
    # Donation CRUD endpoints
    path('donations/', DonationListCreateView.as_view(), name='donation_list_create'),
    path('donations/<int:pk>/', DonationDetailView.as_view(), name='donation_detail'),
    
    # Donation status management
    path('donations/<int:pk>/status/', DonationStatusUpdateView.as_view(), name='donation_status_update'),
    path('donations/<int:pk>/reserve/', ReserveDonationView.as_view(), name='donation_reserve'),
    
    # User-specific donation endpoints
    path('users/<int:donor_id>/donations/', UserDonationsMadeView.as_view(), name='user_donations_made'),
    path('users/<int:recipient_id>/received-donations/', UserDonationsReceivedView.as_view(), name='user_donations_received'),
    
    # Special donation listings
    path('donations/available/', AvailableDonationsView.as_view(), name='available_donations'),
]