from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from .serializers import ConsumerSerializer
from .models import Consumer
from utils.utils import format_response

class ConsumerCreateView(generics.ListCreateAPIView):
    """
    Register a new consumer.
    """
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Register a new consumer with delivery address and food preferences.",
        request_body=ConsumerSerializer,
        responses={
            201: "Consumer created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            multiple = isinstance(request.data, list)  # Check if the request contains a list
            serializer = ConsumerSerializer(data=request.data, many=multiple)

            if serializer.is_valid():
                # If the serializer is valid, create the consumer
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Consumer created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            # If invalid, return the error messages directly from the serializer
            return format_response(
                errors=serializer.errors,
                message="Consumer registration failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating consumer.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all consumers. Requires authentication.",
        responses={
            200: ConsumerSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            consumers = self.get_queryset()
            serializer = self.get_serializer(consumers, many=True)
            return format_response(
                data=serializer.data,
                message="Consumer list retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving consumers.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class ConsumerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific consumer.
    """
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific consumer by ID. Requires authentication.",
        responses={
            200: ConsumerSerializer(),
            401: "Unauthorized",
            404: "Consumer not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except Http404:
            return format_response(
                errors={'detail': 'Consumer not found'},
                message="Consumer not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Consumer details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Update consumer details by ID. Requires authentication.",
        request_body=ConsumerSerializer,
        responses={
            200: "Consumer updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Consumer not found",
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
                message="Consumer updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Delete a specific consumer by ID. Requires authentication.",
        responses={
            204: "Consumer deleted successfully",
            401: "Unauthorized",
            404: "Consumer not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            
            if response.status_code == 204:
                return format_response(
                    message="Consumer deleted successfully",
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


class ConsumerPreferencesView(generics.UpdateAPIView):
    """
    Update a consumer's food preferences.
    """
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a consumer's food preferences by ID. Requires authentication.",
        responses={
            200: "Consumer preferences updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Consumer not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            consumer = self.get_object()
            
            if 'food_preferences' not in request.data:
                return format_response(
                    errors={'food_preferences': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            consumer.food_preferences = request.data['food_preferences']
            consumer.save()
            
            serializer = self.get_serializer(consumer)
            return format_response(
                data=serializer.data,
                message="Consumer preferences updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Consumer not found'},
                message="Consumer not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating preferences",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class ConsumerAddressView(generics.UpdateAPIView):
    """
    Update a consumer's delivery address.
    """
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a consumer's delivery address by ID. Requires authentication.",
        responses={
            200: "Consumer address updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Consumer not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            consumer = self.get_object()
            
            if 'delivery_address' not in request.data:
                return format_response(
                    errors={'delivery_address': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            consumer.delivery_address = request.data['delivery_address']
            consumer.save()
            
            serializer = self.get_serializer(consumer)
            return format_response(
                data=serializer.data,
                message="Consumer address updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Consumer not found'},
                message="Consumer not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating address",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )