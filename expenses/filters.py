import django_filters
from .models import Transaction, Category




class CategoryFilter(django_filters.FilterSet):
    
    name = django_filters.CharFilter(field_name="name",lookup_expr="icontains")
    type = django_filters.ChoiceFilter(
        field_name="type",
        choices=[("income", "Income"), ("expense", "Expense")],
    )
    class Meta:
        model = Category
        fields = []   

class TransactionFilter(django_filters.FilterSet):
    
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category__id")
    type = django_filters.ChoiceFilter(
            field_name="category__type",
            choices=[("income", "Income"), ("expense", "Expense")],
        )
    class Meta:
        model = Transaction
        fields = []   
