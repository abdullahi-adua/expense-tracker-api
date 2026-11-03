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
from decimal import Decimal
from django.db.models import Sum, Count
from rest_framework.response import Response
from rest_framework import status



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
        qs = Transaction.objects.filter(user=self.request.user).select_related("category")
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise ValidationError({"date_to": "Must be on or after date_from."})
        return qs


    @action(detail=False, methods=['get'])
    def summary(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        qs = self.get_queryset()
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        
        income = (qs.filter(category__type='income').aggregate(total=Sum('amount'))['total']
                or Decimal('0.00'))
        expense = (qs.filter(category__type='expense').aggregate(total=Sum('amount'))['total']
                or Decimal('0.00'))
        net = income - expense
        count = qs.count()
        
        return Response({
            'date_from': date_from,
            'date_to': date_to,
            'total_income': str(income),
            'total_expense': str(expense),
            'net': str(net),
            'transaction_count': count,
        })
    
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if not year or not month:
            return Response(
                {'detail': "Query parameters 'year' and 'month' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            year_int = int(year)
            month_int = int(month)
        except (TypeError, ValueError):
            return Response(
                {'detail': "Year and month must be valid integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not (1 <= month_int <= 12):
            return Response(
                {'month': ["Must be between 1 and 12."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        qs = self.get_queryset().filter(date__year=year_int, date__month=month_int)
        
        breakdown = (
            qs.values('category__name', 'category__type')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('category__type', 'category__name')
        )
        
        by_category = [
            {
                'category': row['category__name'],
                'type': row['category__type'],
                'total': str(row['total']),
                'count': row['count'],
            }
            for row in breakdown
        ]
        
        return Response({
            'year': year_int,
            'month': month_int,
            'by_category': by_category,
        })