from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from utils.permissions import CustomIsAuthenticated
from .serializers import UserSerializer, LoginSerializer
from .models import User
from utils.utils import format_response  # Import the format_response function

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
        try:
            # Use the serializer to validate and handle errors
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                # If the serializer is valid, create the user
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="User created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            # If invalid, return the error messages directly from the serializer
            return format_response(
                errors=serializer.errors,
                message="User registration failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False  # Indicating failure
            )
        except Exception as e:
            # Log the exception if needed
            print(f"Error during user registration: {e}")
            return format_response(
                errors="An unexpected error occurred",
                message="User registration failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False  # Indicating failure
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
        try:
            serializer = LoginSerializer(data=request.data)
            print(request.data)
            print(request.method)
            if serializer.is_valid():
                user_data = serializer.validated_data  # This will contain email, access, refresh tokens
                return format_response(
                    data=user_data,
                    message="Login successful",
                    status_code=status.HTTP_200_OK,
                    success=True
                )
            
            return format_response(
                errors=serializer.errors,
                message="Login failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False  # Indicating failure
            )

        except Exception as e:
            # You could log the exception here
            print(e)
            return format_response(
                errors="Database error",
                message="Login failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False  # Indicating failure
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
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
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
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific user by ID. Requires authentication.",
        responses={
            200: UserSerializer(),
            401: "Unauthorized",
            404: "User not found",
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except:
            return format_response(
            errors={'detail': 'Client not found'},
            message="Client not found",
            status_code=status.HTTP_404_NOT_FOUND,
            success=False  # Indicating failure
        )
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="User details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )
       

    @swagger_auto_schema(
        operation_description="Update user details by ID. Requires authentication.",
        request_body=UserSerializer,
        responses={
            200: "User updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "User not found",
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
        except:
            return format_response(
            errors={'detail': 'Client not found'},
            message="Client not found",
            status_code=status.HTTP_404_NOT_FOUND,
            success=False  # Indicating failure
        )
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="User updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
      

    @swagger_auto_schema(
        operation_description="Delete a specific user by ID. Requires authentication.",
        responses={
            204: "User deleted successfully",
            401: "Unauthorized",
            404: "User not found",
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except:
            return format_response(
            errors={'detail': 'Client not found'},
            message="Client not found",
            status_code=status.HTTP_404_NOT_FOUND,
            success=False  # Indicating failure
        )
        if response.status_code == 204:
            return format_response(
                message="User deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT,
                success=True
            )