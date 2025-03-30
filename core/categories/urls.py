from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    SubcategoriesView,
    CategoryTreeView
)

urlpatterns = [
    # Category management endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # Category hierarchy endpoints
    path('categories/<int:parent_id>/subcategories/', SubcategoriesView.as_view(), name='subcategories_list'),
    path('categories/tree/', CategoryTreeView.as_view(), name='category_tree'),
]