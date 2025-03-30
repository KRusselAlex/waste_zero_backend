from django.urls import path
from .views import (
    PointDetailView,
    AddPointsView,
    UserPointsTransferView,
    PointLeaderboardView
)

urlpatterns = [
    # Points management endpoints
    path('points/<int:user_id>/', PointDetailView.as_view(), name='point_balance'),
    path('points/<int:user_id>/add/', AddPointsView.as_view(), name='add_points'),
    
    # Points transfer endpoint
    path('points/transfer/', UserPointsTransferView.as_view(), name='transfer_points'),
    
    # Leaderboard endpoint
    path('points/leaderboard/', PointLeaderboardView.as_view(), name='points_leaderboard'),
]