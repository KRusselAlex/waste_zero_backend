from django.urls import path
from .views import (
    TransactionCreateView,
    TransactionDetailView,
    TransactionStatusUpdateView,
    TransactionByOrderView
)

urlpatterns = [
    # Transaction CRUD endpoints
    path('transactions/', TransactionCreateView.as_view(), name='transaction_list_create'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    
    # Transaction status management
    path('transactions/<int:pk>/status/', TransactionStatusUpdateView.as_view(), name='transaction_status_update'),
    
    # Order-specific transaction
    path('orders/<int:order_id>/transaction/', TransactionByOrderView.as_view(), name='order_transaction'),
]