from celery import shared_task
import pandas as pd
from .models import Customer, Loan


@shared_task
def load_customers(file_path="data/customer_data.xlsx"):
    if Customer.objects.exists():
        return "Customers already loaded" 
    df = pd.read_excel(file_path)

    objs = [
        Customer(
            customer_id=row["Customer ID"],
            first_name=row["First Name"],
            last_name=row["Last Name"],
            age=row["Age"],
            phone_number=row["Phone Number"],
            monthly_salary=row["Monthly Salary"],
            approved_limit=row["Approved Limit"],
        )
        for _, row in df.iterrows()
    ]

    Customer.objects.bulk_create(objs, ignore_conflicts=True)
    return f"Inserted {len(objs)} customers"


@shared_task
def load_loans(file_path="data/loan_data.xlsx"):
    if Loan.objects.exists():
        return "Loans already loaded" 
    df = pd.read_excel(file_path)

    objs = [
        Loan(
            loan_id=row["Loan ID"],
            customer_id=row["Customer ID"],  # FK reference
            loan_amount=row["Loan Amount"],
            tenure=row["Tenure"],
            interest_rate=row["Interest Rate"],
            monthly_payment=row["Monthly payment"],
            emis_paid_on_time=row["EMIs paid on Time"],
            date_of_approval=row["Date of Approval"],
            end_date=row["End Date"],
        )
        for _, row in df.iterrows()
    ]

    Loan.objects.bulk_create(objs, ignore_conflicts=True)
    return f"Inserted {len(objs)} loans"
