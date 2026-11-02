from rest_framework import viewsets
from .serializer import CategorySerializer, TransactionSerializer
from .models import Category, Transaction
from .pagination import StandardPagination
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import CategoryFilter, TransactionFilter
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class= CategorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = "name"
    ordering_fields = ["name","created_at"]
    ordering = ["name"]
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ["description"]
    ordering_fields = ["date", "amount","created_at"]
    ordering = ["-date", "-id"]

    def perform_create(self, serializer):
            serializer.save(user=self.request.user)
    
    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise ValidationError({"date_to": "Must be on or after date_from."})
        return qs