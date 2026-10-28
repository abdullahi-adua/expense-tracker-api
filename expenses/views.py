from rest_framework import viewsets
from .serializer import CategorySerializer, TransactionSerializer
from .models import Category, Transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class= CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
            serializer.save(user=self.request.user)
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)