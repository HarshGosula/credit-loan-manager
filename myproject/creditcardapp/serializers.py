from rest_framework import serializers
from .models import Customer
import math


class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["customer_id", "first_name", "last_name", "age", "phone_number", "monthly_salary", "approved_limit"]
        read_only_fields = ["customer_id", "approved_limit"]

    def create(self, validated_data):
        monthly_salary = validated_data["monthly_salary"]

        # approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        approved_limit = 36 * monthly_salary
        # round to nearest lakh (100000)
        approved_limit = round(approved_limit / 100000) * 100000  

        validated_data["approved_limit"] = approved_limit

        return Customer.objects.create(**validated_data)


class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

class LoanCreateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

