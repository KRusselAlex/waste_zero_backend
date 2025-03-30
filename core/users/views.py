from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from utils.permissions import CustomIsAuthenticated,IsSelfOrAdmin
from .serializers import UserSerializer, LoginSerializer,VerifyEmailSerializer
from .models import User
from utils.utils import format_response
from utils.utils import send_verification_email,is_token_expired
from django.conf import settings
from django.core.mail import send_mail


class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user with email, password, first name, and last name.",
        request_body=UserSerializer,
        responses={
            201: "User created successfully",
            400: "Invalid input",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            token = user.generate_verification_token()
            
            send_verification_email(user.email, token)
            return format_response(
                data=serializer.data,
                message="User created successfully",
                status_code=status.HTTP_201_CREATED,
                success=True
            )
        
        return format_response(
            errors=serializer.errors,
            message="User registration failed",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False
        )



class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Verify user email with the provided token",
        request_body=VerifyEmailSerializer,
        responses={
            200: "Email successfully verified",
            400: "Invalid or expired token",
        }
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return format_response(
                errors=serializer.errors,
                message="Invalid token format",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )

        token = serializer.validated_data['token']
        
        try:
            user = User.objects.get(verification_token=token)
            
            if is_token_expired(user.token_created_at):
                return format_response(
                    errors={'token': 'Token has expired'},
                    message="Verification token has expired. Please request a new one.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
                
            user.is_verified = True
            user.verification_token = None
            user.token_created_at = None
            user.save()
            
            return format_response(
                message="Email successfully verified",
                status_code=status.HTTP_200_OK,
                success=True
            )
            
        except User.DoesNotExist:
            return format_response(
                errors={'token': 'Invalid token'},
                message="Invalid verification token",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )


class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Resend verification email",
        responses={
            200: "Verification email resent",
            400: "User already verified",
        }
    )
    def post(self, request):
        if request.user.is_verified:
            return format_response(
                errors={'email': 'Already verified'},
                message="Email is already verified",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
            
        token = request.user.generate_verification_token()
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        send_mail(
            "Verify your email",
            f"Please click the following link to verify your email: {verification_url}",
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        
        return format_response(
            message="Verification email resent successfully",
            status_code=status.HTTP_200_OK,
            success=True
        )
            
class LoginView(APIView):
    """
    Authenticate a user and return access and refresh tokens.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Authenticate a user using email and password.",
        request_body=LoginSerializer,
        responses={
            200: "Login successful",
            400: "Invalid credentials",
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return format_response(
                data=serializer.validated_data,
                message="Login successful",
                status_code=status.HTTP_200_OK,
                success=True
            )
        
        return format_response(
            errors=serializer.errors,
            message="Login failed",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False
        )


class UserListView(generics.ListAPIView):
    """
    Retrieve a list of all users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all users. Requires authentication.",
        responses={
            200: UserSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return format_response(
            data=serializer.data,
            message="User list retrieved successfully",
            status_code=status.HTTP_200_OK,
            success=True
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrAdmin] # Use our custom permission

    def get_object(self):
        try:
            return super().get_object()
        except User.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return format_response(
                errors={'detail': 'User not found'},
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
            
        serializer = self.get_serializer(instance)
        return format_response(
            data=serializer.data,
            message="User details retrieved",
            status_code=status.HTTP_200_OK,
            success=True
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return format_response(
                errors={'detail': 'User not found'},
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )

        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return format_response(
            data=serializer.data,
            message="User updated successfully",
            status_code=status.HTTP_200_OK,
            success=True
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return format_response(
                errors={'detail': 'User not found'},
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )

        self.perform_destroy(instance)
        return format_response(
            message="User deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
            success=True
        )