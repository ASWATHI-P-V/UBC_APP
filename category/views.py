# category/views.py
from rest_framework import generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category
from .serializers import CategorySerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import NotFound
from accounts.utils import api_response
 

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['id', 'type', 'category_name']
    search_fields = ['category_name', 'type']
    ordering_fields = ['id', 'category_name', 'type']
    ordering = ['id']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Category list retrieved successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            success=True,
            message="Category created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

class CategoryDetailView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return api_response(
                success=True,
                message="Category retrieved successfully.",
                data=serializer.data
            )
        except Category.DoesNotExist:
            return api_response(
                success=False,
                message=f"Category with ID {kwargs['pk']} does not exist.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )

