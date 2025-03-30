from django.urls import path
from .views import (
    ConsumerCreateView,
    ConsumerDetailView,
    ConsumerPreferencesView,
    ConsumerAddressView
)

urlpatterns = [
    # Consumer CRUD endpoints
    path('consumers/', ConsumerCreateView.as_view(), name='consumer_list_create'),
    path('consumers/<int:pk>/', ConsumerDetailView.as_view(), name='consumer_detail'),
    
    # Consumer specific updates
    path('consumers/<int:pk>/preferences/', ConsumerPreferencesView.as_view(), name='consumer_preferences'),
    path('consumers/<int:pk>/address/', ConsumerAddressView.as_view(), name='consumer_address'),
]