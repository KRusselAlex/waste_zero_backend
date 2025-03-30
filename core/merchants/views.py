from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from .serializers import MerchantSerializer
from .models import Merchant
from utils.utils import format_response

class MerchantCreateView(generics.ListCreateAPIView):
    """
    Register a new merchant.
    """
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Register a new merchant with business details.",
        request_body=MerchantSerializer,
        responses={
            201: "Merchant created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            multiple = isinstance(request.data, list)  # Check if the request contains a list
            serializer = MerchantSerializer(data=request.data, many=multiple)

            if serializer.is_valid():
                # If the serializer is valid, create the merchant
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Merchant created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            # If invalid, return the error messages directly from the serializer
            return format_response(
                errors=serializer.errors,
                message="Merchant registration failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating merchant.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all merchants. Requires authentication.",
        responses={
            200: MerchantSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            merchants = self.get_queryset()
            serializer = self.get_serializer(merchants, many=True)
            return format_response(
                data=serializer.data,
                message="Merchant list retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving merchants.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class MerchantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific merchant.
    """
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific merchant by ID. Requires authentication.",
        responses={
            200: MerchantSerializer(),
            401: "Unauthorized",
            404: "Merchant not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except Http404:
            return format_response(
                errors={'detail': 'Merchant not found'},
                message="Merchant not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Merchant details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Update merchant details by ID. Requires authentication.",
        request_body=MerchantSerializer,
        responses={
            200: "Merchant updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Merchant not found",
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
                message="Merchant updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Delete a specific merchant by ID. Requires authentication.",
        responses={
            204: "Merchant deleted successfully",
            401: "Unauthorized",
            404: "Merchant not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            
            if response.status_code == 204:
                return format_response(
                    message="Merchant deleted successfully",
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


class MerchantVerificationView(generics.UpdateAPIView):
    """
    Verify a merchant.
    """
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verify a merchant by ID. Requires authentication.",
        responses={
            200: "Merchant verified successfully",
            401: "Unauthorized",
            404: "Merchant not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            merchant = self.get_object()
            merchant.is_verified = True
            merchant.save()
            
            serializer = self.get_serializer(merchant)
            return format_response(
                data=serializer.data,
                message="Merchant verified successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Merchant not found'},
                message="Merchant not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred during verification",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class MerchantPriceLimitView(generics.UpdateAPIView):
    """
    Update a merchant's price limit.
    """
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a merchant's price limit by ID. Requires authentication.",
        responses={
            200: "Merchant price limit updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Merchant not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            merchant = self.get_object()
            
            if 'max_price_limit' not in request.data:
                return format_response(
                    errors={'max_price_limit': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            merchant.max_price_limit = request.data['max_price_limit']
            merchant.save()
            
            serializer = self.get_serializer(merchant)
            return format_response(
                data=serializer.data,
                message="Merchant price limit updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Merchant not found'},
                message="Merchant not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating price limit",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )