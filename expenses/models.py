from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

TYPE_CHOICES = [
    ("income", "Income"),
    ("expense", "Expense")
    ]

class Category(models.Model):

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "user"],
                                               name= "unique_category_per_user" )]
        ordering= ["name"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="transactions") 
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions")
    amount = models.DecimalField(max_digits=12,decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    date = models.DateField()
    description = models.CharField(max_length=255, blank= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
                    models.Index(fields=["user", "date"])
        ]

        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.date}"