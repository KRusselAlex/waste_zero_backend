from rest_framework import generics, status, filters
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from utils.utils import format_response

from .models import Donation
from .serializers import DonationSerializer


class DonationListCreateView(generics.ListCreateAPIView):
    """
    List all donations or create a new donation.
    """
    serializer_class = DonationSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'status', 'title']
    ordering = ['-created_at']  # Default ordering is newest first

    def get_queryset(self):
        return Donation.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new donation.",
        request_body=DonationSerializer,
        responses={
            201: "Donation created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            multiple = isinstance(request.data, list)  # Check if the request contains a list
            serializer = DonationSerializer(data=request.data, many=multiple)

            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Donation created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            return format_response(
                errors=serializer.errors,
                message="Donation creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating donation.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all donations with optional filtering.",
        responses={
            200: DonationSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            donor_id = request.query_params.get('donor', None)
            recipient_id = request.query_params.get('recipient', None)
            status_filter = request.query_params.get('status', None)
            
            # Apply filters if provided
            queryset = self.get_queryset()
            
            if donor_id:
                queryset = queryset.filter(donor_id=donor_id)
                
            if recipient_id:
                queryset = queryset.filter(recipient_id=recipient_id)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
                
            # Apply ordering from filter_backends
            queryset = self.filter_queryset(queryset)
            
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Donations retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving donations.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class DonationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a donation.
    """
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific donation by ID.",
        responses={
            200: DonationSerializer(),
            401: "Unauthorized",
            404: "Donation not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except Http404:
            return format_response(
                errors={'detail': 'Donation not found'},
                message="Donation not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Donation details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Update a donation by ID.",
        request_body=DonationSerializer,
        responses={
            200: "Donation updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Donation not found",
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
                message="Donation updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Delete a donation by ID.",
        responses={
            204: "Donation deleted successfully",
            401: "Unauthorized",
            404: "Donation not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            
            if response.status_code == 204:
                return format_response(
                    message="Donation deleted successfully",
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


class DonationStatusUpdateView(generics.UpdateAPIView):
    """
    Update a donation's status.
    """
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a donation's status by ID.",
        responses={
            200: "Donation status updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Donation not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            donation = self.get_object()
            
            if 'status' not in request.data:
                return format_response(
                    errors={'status': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Check if status is valid
            status_value = request.data['status']
            valid_statuses = [status for status, _ in Donation.STATUS_CHOICES]
            
            if status_value not in valid_statuses:
                return format_response(
                    errors={'status': f'Must be one of: {", ".join(valid_statuses)}'},
                    message="Invalid status value",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
                
            # If updating recipient
            if 'recipient' in request.data and request.data['recipient']:
                donation.recipient_id = request.data['recipient']
            
            # Update status
            donation.status = status_value
            donation.save()
            
            serializer = self.get_serializer(donation)
            return format_response(
                data=serializer.data,
                message="Donation status updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Donation not found'},
                message="Donation not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred updating donation status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class UserDonationsMadeView(generics.ListAPIView):
    """
    Retrieve all donations made by a specific user.
    """
    serializer_class = DonationSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'status', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        donor_id = self.kwargs.get('donor_id')
        return Donation.objects.filter(donor_id=donor_id)

    @swagger_auto_schema(
        operation_description="Retrieve all donations made by a specific user ID.",
        responses={
            200: DonationSerializer(many=True),
            401: "Unauthorized",
            404: "User not found or has no donations",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            if not queryset.exists():
                return format_response(
                    data=[],
                    message="No donations found for this user",
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
                message="User donations retrieved successfully",
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


class UserDonationsReceivedView(generics.ListAPIView):
    """
    Retrieve all donations received by a specific user.
    """
    serializer_class = DonationSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'status', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        recipient_id = self.kwargs.get('recipient_id')
        return Donation.objects.filter(recipient_id=recipient_id)

    @swagger_auto_schema(
        operation_description="Retrieve all donations received by a specific user ID.",
        responses={
            200: DonationSerializer(many=True),
            401: "Unauthorized",
            404: "User not found or has received no donations",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            if not queryset.exists():
                return format_response(
                    data=[],
                    message="No donations received by this user",
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
                message="User received donations retrieved successfully",
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


class AvailableDonationsView(generics.ListAPIView):
    """
    Retrieve all currently available donations.
    """
    serializer_class = DonationSerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Donation.objects.filter(status='available')

    @swagger_auto_schema(
        operation_description="Retrieve all currently available donations.",
        responses={
            200: DonationSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Apply donor filter if provided
            donor_id = request.query_params.get('donor', None)
            if donor_id:
                queryset = queryset.filter(donor_id=donor_id)
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
                
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Available donations retrieved successfully",
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


class ReserveDonationView(generics.UpdateAPIView):
    """
    Reserve a donation for a specific recipient.
    """
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Reserve a donation for a specific recipient.",
        responses={
            200: "Donation reserved successfully",
            400: "Invalid request or donation not available",
            401: "Unauthorized",
            404: "Donation not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            donation = self.get_object()
            
            if donation.status != 'available':
                return format_response(
                    errors={'status': 'This donation is not available for reservation'},
                    message="Donation not available",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            if 'recipient' not in request.data:
                return format_response(
                    errors={'recipient': 'This field is required'},
                    message="Missing required field",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Update donation with recipient and change status to reserved
            donation.recipient_id = request.data['recipient']
            donation.status = 'reserved'
            donation.save()
            
            serializer = self.get_serializer(donation)
            return format_response(
                data=serializer.data,
                message="Donation reserved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Donation not found'},
                message="Donation not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred reserving the donation",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )