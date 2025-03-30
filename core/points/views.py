from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from utils.utils import format_response
from users.models import User
from .models import Point
from .serializers import PointSerializer


class PointDetailView(generics.RetrieveAPIView):
    """
    Retrieve a user's point balance.
    """
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [CustomIsAuthenticated]
    lookup_field = 'user_id'

    @swagger_auto_schema(
        operation_description="Retrieve a user's point balance by user ID.",
        responses={
            200: PointSerializer(),
            401: "Unauthorized",
            404: "User not found or has no point record",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            return format_response(
                data=response.data,
                message="Point balance retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Point record not found'},
                message="Point record not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )


class AddPointsView(generics.UpdateAPIView):
    """
    Add points to a user's balance.
    """
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [CustomIsAuthenticated]
    lookup_field = 'user_id'

    @swagger_auto_schema(
        operation_description="Add points to a user's balance.",
        request_body=PointSerializer,
        responses={
            200: "Points added successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "User not found",
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            point = self.get_object()
            
            if 'amount' not in request.data:
                return format_response(
                    errors={'amount': 'This field is required'},
                    message="Amount is required",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            try:
                amount = int(request.data['amount'])
                if amount <= 0:
                    raise ValueError
            except ValueError:
                return format_response(
                    errors={'amount': 'Must be a positive integer'},
                    message="Invalid amount",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            point.add_points(amount)
            serializer = self.get_serializer(point)
            
            return format_response(
                data=serializer.data,
                message=f"Successfully added {amount} points",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Http404:
            return format_response(
                errors={'detail': 'Point record not found'},
                message="Point record not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred while adding points",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class UserPointsTransferView(generics.GenericAPIView):
    """
    Transfer points between users.
    """
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Transfer points from one user to another.",
        request_body=PointSerializer,
        responses={
            200: "Points transferred successfully",
            400: "Invalid input or insufficient balance",
            401: "Unauthorized",
            404: "User(s) not found",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # Validate required fields
            required_fields = ['from_user_id', 'to_user_id', 'amount']
            if not all(field in request.data for field in required_fields):
                missing = [f for f in required_fields if f not in request.data]
                return format_response(
                    errors={field: 'This field is required' for field in missing},
                    message="Missing required fields",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            try:
                amount = int(request.data['amount'])
                if amount <= 0:
                    raise ValueError
            except ValueError:
                return format_response(
                    errors={'amount': 'Must be a positive integer'},
                    message="Invalid amount",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Get both user's point records
            try:
                from_point = Point.objects.get(user_id=request.data['from_user_id'])
                to_point = Point.objects.get(user_id=request.data['to_user_id'])
            except Point.DoesNotExist:
                return format_response(
                    errors={'detail': 'One or both users not found'},
                    message="User(s) not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=False
                )
            
            # Check sufficient balance
            if from_point.balance < amount:
                return format_response(
                    errors={'balance': 'Insufficient points'},
                    message="Insufficient points for transfer",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            # Perform transfer
            from_point.balance -= amount
            to_point.balance += amount
            
            from_point.save()
            to_point.save()
            
            return format_response(
                data={
                    'from_user_balance': from_point.balance,
                    'to_user_balance': to_point.balance
                },
                message=f"Successfully transferred {amount} points",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred during points transfer",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )


class PointLeaderboardView(generics.ListAPIView):
    """
    Retrieve leaderboard of users by point balance.
    """
    serializer_class = PointSerializer
    permission_classes = [CustomIsAuthenticated]
    queryset = Point.objects.all().order_by('-balance')

    @swagger_auto_schema(
        operation_description="Retrieve leaderboard of users sorted by point balance (highest first).",
        responses={
            200: PointSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            limit = int(request.query_params.get('limit', 10))
            if limit <= 0:
                limit = 10
            
            queryset = self.get_queryset()[:limit]
            serializer = self.get_serializer(queryset, many=True)
            
            return format_response(
                data=serializer.data,
                message="Leaderboard retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving leaderboard",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )