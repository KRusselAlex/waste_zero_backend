from django.urls import path
from .views import (
    ReviewListCreateView,
    ReviewDetailView,
    OrderReviewView
)

urlpatterns = [
    # Review CRUD endpoints
    path('reviews/', ReviewListCreateView.as_view(), name='review_list_create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
    
    # Order-specific review
    path('orders/<int:order_id>/review/', OrderReviewView.as_view(), name='order_review'),
]