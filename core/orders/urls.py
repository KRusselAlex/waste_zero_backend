from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderStatusUpdateView,
    ConsumerOrdersView,
    OrderStatusChoicesView,
    OrderPaymentChoicesView
)

urlpatterns = [
    # Order management endpoints
    path('orders/', OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    
    # Consumer-specific orders
    path('consumers/<int:consumer_id>/orders/', ConsumerOrdersView.as_view(), name='consumer_orders'),
    
    # Choices endpoints (for dropdowns)
    path('orders/status-choices/', OrderStatusChoicesView.as_view(), name='order_status_choices'),
    path('orders/payment-choices/', OrderPaymentChoicesView.as_view(), name='order_payment_choices'),
]