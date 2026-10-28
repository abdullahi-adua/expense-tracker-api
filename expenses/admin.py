from django.contrib import admin
from .models import Category, Transaction

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display= ["id","name","type","user", "created_at"]
    list_filter= ["type", "created_at"]
    search_fields = ["name", "user__username"]
    raw_id_fields= ["user"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display= ["id","user","category","amount", "date"]
    list_filter = ["date", "category__type", "category"]
    search_fields = ["description", "user__username"]
    raw_id_fields = ["user", "category"]
    date_hierarchy = "date"