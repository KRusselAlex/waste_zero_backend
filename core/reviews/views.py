from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated,IsSelfOrAdmin
from utils.utils import format_response
from .models import Review
from rest_framework import filters
from .serializers import ReviewSerializer

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    List all reviews or create a new review.
    """
    serializer_class = ReviewSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['review_date', 'rating']
    ordering = ['-review_date']  # Default ordering is newest first

    def get_queryset(self):
        return Review.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new review.",
        request_body=ReviewSerializer,
        responses={
            201: "Review created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Review created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            return format_response(
                errors=serializer.errors,
                message="Review creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating review.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all reviews with optional filtering.",
        responses={
            200: ReviewSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            order_id = request.query_params.get('order', None)
            min_rating = request.query_params.get('min_rating', None)
            
            # Apply filters if provided
            queryset = self.get_queryset()
            
            if order_id:
                queryset = queryset.filter(order_id=order_id)
            
            if min_rating:
                queryset = queryset.filter(rating__gte=min_rating)
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
            
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Reviews retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving reviews.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific review by ID.",
        responses={
            200: ReviewSerializer(),
            401: "Unauthorized",
            404: "Review not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Review details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Review not found'},
                message="Review not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Update a review by ID.",
        request_body=ReviewSerializer,
        responses={
            200: "Review updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Review not found",
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Review updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Review not found'},
                message="Review not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="Review update failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )

    @swagger_auto_schema(
        operation_description="Delete a review by ID.",
        responses={
            204: "Review deleted successfully",
            401: "Unauthorized",
            404: "Review not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
            return format_response(
                message="Review deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Review not found'},
                message="Review not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )

class OrderReviewView(generics.RetrieveAPIView):
    """
    Retrieve review for a specific order.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsSelfOrAdmin]
    lookup_field = 'order_id'

    @swagger_auto_schema(
        operation_description="Retrieve review for a specific order ID.",
        responses={
            200: ReviewSerializer(),
            401: "Unauthorized",
            404: "Review not found for this order",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Order review retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                data=None,
                message="No review found for this order",
                status_code=status.HTTP_200_OK,
                success=True
            )