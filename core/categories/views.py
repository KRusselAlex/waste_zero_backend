from rest_framework import generics, status, filters
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from utils.permissions import CustomIsAuthenticated
from utils.utils import format_response

from .models import Category
from .serializers import CategorySerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    List all categories or create a new category.
    """
    serializer_class = CategorySerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'created_at']
    ordering = ['name']  # Default ordering is alphabetical

    def get_queryset(self):
        return Category.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new category.",
        request_body=CategorySerializer,
        responses={
            201: "Category created successfully",
            400: "Invalid input",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            multiple = isinstance(request.data, list)  # Check if the request contains a list
            serializer = CategorySerializer(data=request.data, many=multiple)

            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message="Category created successfully",
                    status_code=status.HTTP_201_CREATED,
                    success=True
                )
            return format_response(
                errors=serializer.errors,
                message="Category creation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        except Exception as e:
            return format_response(
                message="An error occurred while creating category.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of all categories with optional filtering.",
        responses={
            200: CategorySerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            parent_id = request.query_params.get('parent', None)
            top_level_only = request.query_params.get('top_level_only', None)
            
            # Apply filters if provided
            queryset = self.get_queryset()
            
            if parent_id:
                queryset = queryset.filter(parent_id=parent_id)
            elif top_level_only and top_level_only.lower() == 'true':
                queryset = queryset.filter(parent__isnull=True)
                
            # Apply ordering from filter_backends
            queryset = self.filter_queryset(queryset)
            
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Categories retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                message="An error occurred while retrieving categories.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                errors=str(e)
            )


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific category by ID.",
        responses={
            200: CategorySerializer(),
            401: "Unauthorized",
            404: "Category not found",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
        except Http404:
            return format_response(
                errors={'detail': 'Category not found'},
                message="Category not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
        
        if response.status_code == 200:
            return format_response(
                data=response.data,
                message="Category details retrieved",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Update a category by ID.",
        request_body=CategorySerializer,
        responses={
            200: "Category updated successfully",
            400: "Invalid input",
            401: "Unauthorized",
            404: "Category not found",
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
                message="Category updated successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )

    @swagger_auto_schema(
        operation_description="Delete a category by ID.",
        responses={
            204: "Category deleted successfully",
            401: "Unauthorized",
            404: "Category not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            
            if response.status_code == 204:
                return format_response(
                    message="Category deleted successfully",
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


class SubcategoriesView(generics.ListAPIView):
    """
    Retrieve all subcategories for a specific parent category.
    """
    serializer_class = CategorySerializer
    permission_classes = [CustomIsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        parent_id = self.kwargs.get('parent_id')
        return Category.objects.filter(parent_id=parent_id)

    @swagger_auto_schema(
        operation_description="Retrieve all subcategories for a specific parent category ID.",
        responses={
            200: CategorySerializer(many=True),
            401: "Unauthorized",
            404: "Parent category not found or has no subcategories",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # First check if parent exists
            parent_id = self.kwargs.get('parent_id')
            if not Category.objects.filter(id=parent_id).exists():
                return format_response(
                    errors={'detail': 'Parent category not found'},
                    message="Parent category not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=False
                )
            
            queryset = self.get_queryset()
            
            if not queryset.exists():
                return format_response(
                    data=[],
                    message="No subcategories found for this parent category",
                    status_code=status.HTTP_200_OK,
                    success=True
                )
                
            # Apply ordering
            queryset = self.filter_queryset(queryset)
                
            serializer = self.get_serializer(queryset, many=True)
            return format_response(
                data=serializer.data,
                message="Subcategories retrieved successfully",
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


class CategoryTreeView(generics.ListAPIView):
    """
    Retrieve a hierarchical tree of categories.
    """
    serializer_class = CategorySerializer
    permission_classes = [CustomIsAuthenticated]
    
    def get_queryset(self):
        # Return only top-level categories (those without a parent)
        return Category.objects.filter(parent__isnull=True)

    @swagger_auto_schema(
        operation_description="Retrieve a hierarchical tree of categories.",
        responses={
            200: "Category tree retrieved successfully",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Use a recursive serializer that includes subcategories
            serializer = self.get_serializer(queryset, many=True, context={'include_subcategories': True})
            
            return format_response(
                data=serializer.data,
                message="Category tree retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return format_response(
                errors=str(e),
                message="An error occurred retrieving category tree",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False
            )
