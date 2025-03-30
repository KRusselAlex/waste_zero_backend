from rest_framework import generics, status, filters
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from .serializers import TransactionSerializer
from .models import Transaction
from utils.utils import format_response

class TransactionCreateView(generics.ListCreateAPIView):
    """
    Create a new transaction and list all transactions.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['transaction_date', 'amount', 'status']
    ordering = ['-transaction_date']  # Default ordering

    @swagger_auto_schema(
        operation_description="Create a new transaction record for an order.",
        request_body=TransactionSerializer,
        responses={
            201: "Transaction created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            multiple = isinstance(request.data, list)  # Check if the request contains a list
            serializer = TransactionSerializer(data=request.data, many=multiple)

            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Transaction created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            return format_response(
                errors=serializer.errors,
                message="Transaction creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating transaction.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all transactions. Supports filtering and ordering.",
        responses={
            200: TransactionSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            status_filter = request.query_params.get('status', None)
            payment_method = request.query_params.get('payment_method', None)
            
            # Apply filters if provided
            queryset = self.get_queryset()
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if payment_method:
                queryset = queryset.filter(payment_method=payment_method)
                
            # Apply ordering from filter_backends
            queryset = self.filter_queryset(queryset)
            
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Transactions retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving transactions.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class TransactionDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a specific transaction.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific transaction by ID.",
        responses={
            200: TransactionSerializer(),
            401: "Unauthorized",
            404: "Transaction not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except Http404:
            return format_response(
                errors={'detail': 'Transaction not found'},
                message="Transaction not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Transaction details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Update transaction details by ID.",
        request_body=TransactionSerializer,
        responses={
            200: "Transaction updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Transaction not found",
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
        except Exception as error:
            return format_response(
                errors={'detail': str(error)},
                message="There is an error",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Transaction updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )


class TransactionStatusUpdateView(generics.UpdateAPIView):
    """
    Update a transaction's status.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a transaction's status by ID.",
        responses={
            200: "Transaction status updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Transaction not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            transaction = self.get_object()
            
            if 'status' not in request.data:
                return format_response(
                    errors={'status': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Check if status is valid
            status_value = request.data['status']
            valid_statuses = [status for status, _ in Transaction.STATUS_CHOICES]
            
            if status_value not in valid_statuses:
                return format_response(
                    errors={'status': f'Must be one of: {", ".join(valid_statuses)}'},
                    message="Invalid status value",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            transaction.status = status_value
            transaction.save()
            
            serializer = self.get_serializer(transaction)
            return format_response(
                data=serializer.data,
                message="Transaction status updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Transaction not found'},
                message="Transaction not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating transaction status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class TransactionByOrderView(generics.RetrieveAPIView):
    """
    Retrieve transaction details for a specific order.
    """
    serializer_class = TransactionSerializer
    permission_classes = [CustomIsAuthenticated]
    
    def get_object(self):
        order_id = self.kwargs.get('order_id')
        try:
            return Transaction.objects.get(order_id=order_id)
        except Transaction.DoesNotExist:
            raise Http404("No transaction found for this order")

    @swagger_auto_schema(
        operation_description="Retrieve transaction details for a specific order ID.",
        responses={
            200: TransactionSerializer(),
            401: "Unauthorized",
            404: "Transaction not found for this order",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            transaction = self.get_object()
            serializer = self.get_serializer(transaction)
            return format_response(
                data=serializer.data,
                message="Transaction details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'No transaction found for this order'},
                message="Transaction not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )