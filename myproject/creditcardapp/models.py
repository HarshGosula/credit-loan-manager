# app/models.py
from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)  # matches "Customer ID"
    first_name = models.CharField(max_length=100)    # First Name
    last_name = models.CharField(max_length=100)     # Last Name
    age = models.IntegerField()                      # Age
    phone_number = models.CharField(max_length=15, unique=True)  # Phone Number
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)  # Monthly Salary
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)  # Approved Limit

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)         # Loan ID
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="loans"
    )  # Customer ID (FK)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Loan Amount
    tenure = models.IntegerField(help_text="Tenure in months")          # Tenure
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2) # Interest Rate
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)  # Monthly Payment
    emis_paid_on_time = models.IntegerField()            # EMIs paid on Time
    date_of_approval = models.DateField()                # Date of Approval
    end_date = models.DateField()                        # End Date

    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer.customer_id}"
