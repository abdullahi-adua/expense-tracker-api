from rest_framework import serializers
from .models import Category, Transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name", "type", "created_at"]
        read_only_fields = ["id","created_at"]


    



class TransactionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="category.type", read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    class Meta:
        model = Transaction
        fields = ["id", "category","category_id", "amount","type", "date", "description",
                  "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


    def validate_category_id(self, value):
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("You can only use your own categories.")
        return value