from rest_framework import generics, status, filters
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from utils.utils import format_response
from .models import Order
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """
    List all orders or create a new order.
    """
    serializer_class = OrderSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order_date', 'pickup_date', 'total_price']
    ordering = ['-order_date']  # Default ordering is newest first

    def get_queryset(self):
        return Order.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new order.",
        request_body=OrderSerializer,
        responses={
            201: "Order created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Order created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            return format_response(
                errors=serializer.errors,
                message="Order creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating order.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all orders with optional filtering.",
        responses={
            200: OrderSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            consumer_id = request.query_params.get('consumer', None)
            offer_id = request.query_params.get('offer', None)
            status_filter = request.query_params.get('status', None)
            payment_method = request.query_params.get('payment_method', None)
            
            # Apply filters if provided
            queryset = self.get_queryset()
            
            if consumer_id:
                queryset = queryset.filter(consumer_id=consumer_id)
                
            if offer_id:
                queryset = queryset.filter(offer_id=offer_id)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
                
            if payment_method:
                queryset = queryset.filter(payment_method=payment_method)
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
            
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Orders retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving orders.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific order by ID.",
        responses={
            200: OrderSerializer(),
            401: "Unauthorized",
            404: "Order not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Order details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Order not found'},
                message="Order not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Update an order by ID.",
        request_body=OrderSerializer,
        responses={
            200: "Order updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Order not found",
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Order updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Order not found'},
                message="Order not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="Order update failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Delete an order by ID.",
        responses={
            204: "Order deleted successfully",
            401: "Unauthorized",
            404: "Order not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
            return format_response(
                message="Order deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Order not found'},
                message="Order not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    Update an order's status.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update an order's status by ID.",
        responses={
            200: "Order status updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Order not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            
            if 'status' not in request.data:
                return format_response(
                    errors={'status': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Check if status is valid
            status_value = request.data['status']
            valid_statuses = [status[0] for status in Order.STATUS_CHOICES]
            
            if status_value not in valid_statuses:
                return format_response(
                    errors={'status': f'Must be one of: {", ".join(valid_statuses)}'},
                    message="Invalid status value",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
                
            # Update status
            order.status = status_value
            order.save()
            
            serializer = self.get_serializer(order)
            return format_response(
                data=serializer.data,
                message="Order status updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Order not found'},
                message="Order not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating order status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class ConsumerOrdersView(generics.ListAPIView):
    """
    Retrieve all orders for a specific consumer.
    """
    serializer_class = OrderSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order_date', 'pickup_date', 'total_price']
    ordering = ['-order_date']
    
    def get_queryset(self):
        consumer_id = self.kwargs.get('consumer_id')
        return Order.objects.filter(consumer_id=consumer_id)

    @swagger_auto_schema(
        operation_description="Retrieve all orders for a specific consumer ID.",
        responses={
            200: OrderSerializer(many=True),
            401: "Unauthorized",
            404: "Consumer not found or has no orders",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Apply status filter if provided
            status_filter = request.query_params.get('status', None)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
            
            if not queryset.exists():
                return format_response(
                    data=[],
                    message="No orders found for this consumer",
                    status_code=status.HTTP_200_OK,
                    success=True
                )
                
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Consumer orders retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving consumer orders",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class OrderStatusChoicesView(generics.GenericAPIView):
    """
    List all available order status choices.
    """
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all available order status choices",
        responses={
            200: "List of status choices",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            status_choices = [{'value': choice[0], 'display': choice[1]} 
                            for choice in Order.STATUS_CHOICES]
            return format_response(
                data=status_choices,
                message="Status choices retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving status choices",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class OrderPaymentChoicesView(generics.GenericAPIView):
    """
    List all available payment method choices.
    """
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all available payment method choices",
        responses={
            200: "List of payment method choices",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            payment_choices = [{'value': choice[0], 'display': choice[1]} 
                             for choice in Order.PAYMENT_CHOICES]
            return format_response(
                data=payment_choices,
                message="Payment method choices retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving payment method choices",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )