from rest_framework import generics, status, filters
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from django.utils import timezone
from utils.permissions import CustomIsAuthenticated
from .serializers import OfferSerializer
from .models import Offer
from utils.utils import format_response

class OfferListCreateView(generics.ListCreateAPIView):
    """
    List all offers or create a new offer.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'price', 'start_date', 'end_date']
    ordering = ['-created_at']  # Default ordering is newest first

    @swagger_auto_schema(
        operation_description="Create a new offer for a merchant.",
        request_body=OfferSerializer,
        responses={
            201: "Offer created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            multiple = isinstance(request.data, list)  # Check if the request contains a list
            serializer = OfferSerializer(data=request.data, many=multiple)

            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Offer created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            return format_response(
                errors=serializer.errors,
                message="Offer creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating offer.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all offers with optional filtering.",
        responses={
            200: OfferSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            merchant_id = request.query_params.get('merchant', None)
            status_filter = request.query_params.get('status', None)
            min_price = request.query_params.get('min_price', None)
            max_price = request.query_params.get('max_price', None)
            available_now = request.query_params.get('available_now', None)
            
            # Apply filters if provided
            queryset = self.get_queryset()
            
            if merchant_id:
                queryset = queryset.filter(merchant_id=merchant_id)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if min_price:
                queryset = queryset.filter(price__gte=min_price)
                
            if max_price:
                queryset = queryset.filter(price__lte=max_price)
                
            if available_now and available_now.lower() == 'true':
                today = timezone.now().date()
                queryset = queryset.filter(
                    start_date__lte=today,
                    end_date__gte=today,
                    status='available'
                )
                
            # Apply ordering from filter_backends
            queryset = self.filter_queryset(queryset)
            
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Offers retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving offers.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an offer.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific offer by ID.",
        responses={
            200: OfferSerializer(),
            401: "Unauthorized",
            404: "Offer not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except Http404:
            return format_response(
                errors={'detail': 'Offer not found'},
                message="Offer not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Offer details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Update an offer by ID.",
        request_body=OfferSerializer,
        responses={
            200: "Offer updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Offer not found",
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
                message="Offer updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Delete an offer by ID.",
        responses={
            204: "Offer deleted successfully",
            401: "Unauthorized",
            404: "Offer not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            
            if response.status_code == 204:
                return format_response(
                    message="Offer deleted successfully",
                    status_code=status.HTTP_204_NO_CONTENT,
                    success=True
                )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="Database error",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )


class OfferStatusUpdateView(generics.UpdateAPIView):
    """
    Update an offer's status.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update an offer's status by ID.",
        responses={
            200: "Offer status updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Offer not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            offer = self.get_object()
            
            if 'status' not in request.data:
                return format_response(
                    errors={'status': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Check if status is valid
            status_value = request.data['status']
            valid_statuses = [status for status, _ in Offer.STATUS_CHOICES]
            
            if status_value not in valid_statuses:
                return format_response(
                    errors={'status': f'Must be one of: {", ".join(valid_statuses)}'},
                    message="Invalid status value",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            offer.status = status_value
            offer.save()
            
            serializer = self.get_serializer(offer)
            return format_response(
                data=serializer.data,
                message="Offer status updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Offer not found'},
                message="Offer not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating offer status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class MerchantOffersView(generics.ListAPIView):
    """
    Retrieve all offers for a specific merchant.
    """
    serializer_class = OfferSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'price', 'start_date', 'end_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        merchant_id = self.kwargs.get('merchant_id')
        return Offer.objects.filter(merchant_id=merchant_id)

    @swagger_auto_schema(
        operation_description="Retrieve all offers for a specific merchant ID.",
        responses={
            200: OfferSerializer(many=True),
            401: "Unauthorized",
            404: "Merchant not found or has no offers",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            if not queryset.exists():
                return format_response(
                    data=[],
                    message="No offers found for this merchant",
                    status_code=status.HTTP_200_OK,
                    success=True
                )
                
            # Apply optional status filter if provided
            status_filter = request.query_params.get('status', None)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
                
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Merchant offers retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class ActiveOffersView(generics.ListAPIView):
    """
    Retrieve all currently active offers.
    """
    serializer_class = OfferSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'price']
    ordering = ['price']  # Default ordering by price (lowest first)
    
    def get_queryset(self):
        today = timezone.now().date()
        return Offer.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='available'
        )

    @swagger_auto_schema(
        operation_description="Retrieve all currently active offers (available and within date range).",
        responses={
            200: OfferSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Apply merchant filter if provided
            merchant_id = request.query_params.get('merchant', None)
            if merchant_id:
                queryset = queryset.filter(merchant_id=merchant_id)
                
            # Apply price range filters if provided
            min_price = request.query_params.get('min_price', None)
            max_price = request.query_params.get('max_price', None)
            
            if min_price:
                queryset = queryset.filter(price__gte=min_price)
                
            if max_price:
                queryset = queryset.filter(price__lte=max_price)
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
                
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Active offers retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )