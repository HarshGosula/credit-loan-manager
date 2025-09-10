from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerRegisterSerializer, LoanEligibilitySerializer, LoanCreateSerializer
from datetime import date
from .models import Customer, Loan
from datetime import date, timedelta


@api_view(["POST"])
def register_customer(request):
    serializer = CustomerRegisterSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        response_data = {
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "age": customer.age,
            "phone_number": customer.phone_number,
            "monthly_salary": float(customer.monthly_salary),
            "approved_limit": float(customer.approved_limit),
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def calculate_emi(principal, annual_rate, tenure_months):
    """
    Calculate EMI using compound interest formula
    """
    r = (annual_rate / 100) / 12
    n = tenure_months
    if r == 0:
        return principal / n
    emi = (principal * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
    return emi


@api_view(["POST"])
def check_eligibility(request):
    serializer = LoanEligibilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    customer_id = serializer.validated_data["customer_id"]
    loan_amount = float(serializer.validated_data["loan_amount"])
    interest_rate = float(serializer.validated_data["interest_rate"])
    tenure = serializer.validated_data["tenure"]

    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    # ----- Step 1: Gather past loan info -----
    loans = Loan.objects.filter(customer=customer)
    current_year = date.today().year

    total_approved_volume = sum([float(l.loan_amount) for l in loans])
    total_current_loans = sum([float(l.loan_amount) for l in loans if l.end_date >= date.today()])
    total_emis = sum([float(l.monthly_payment) for l in loans if l.end_date >= date.today()])
    loans_this_year = loans.filter(date_of_approval__year=current_year).count()

    # Base credit score = 100
    credit_score = 100

    # Past loans paid on time (reward punctuality)
    on_time_ratio = 0
    if loans.count() > 0:
        on_time_ratio = sum([l.emis_paid_on_time for l in loans]) / (loans.count() * tenure)
        credit_score -= (1 - on_time_ratio) * 30  # penalize missed EMIs

    # Number of loans taken (more loans reduce credit score)
    credit_score -= min(loans.count() * 2, 20)

    # Loan activity in current year (too many loans → risky)
    credit_score -= min(loans_this_year * 5, 15)

    # Loan approved volume compared to approved limit
    if total_approved_volume > float(customer.approved_limit):
        credit_score = 0

    credit_score = max(0, min(100, credit_score))  # clamp to 0–100

    # ----- Step 2: Loan approval rules -----
    approval = True
    corrected_interest_rate = interest_rate

    if credit_score > 50:
        pass
    elif 30 < credit_score <= 50:
        if interest_rate < 12:
            corrected_interest_rate = 12
        if corrected_interest_rate < 12:
            approval = False
    elif 10 < credit_score <= 30:
        if interest_rate < 16:
            corrected_interest_rate = 16
        if corrected_interest_rate < 16:
            approval = False
    else:  # credit_score <= 10
        approval = False

    # Rule: if current EMIs > 50% of monthly salary → reject
    if total_emis > (0.5 * float(customer.monthly_salary)):
        approval = False

    # ----- Step 3: EMI calculation -----
    monthly_installment = calculate_emi(loan_amount, corrected_interest_rate, tenure)

    response_data = {
        "customer_id": customer.customer_id,
        "approval": approval,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_interest_rate,
        "tenure": tenure,
        "monthly_installment": round(monthly_installment, 2),
    }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(["POST"])
def create_loan(request):
    serializer = LoanCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    customer_id = serializer.validated_data["customer_id"]
    loan_amount = float(serializer.validated_data["loan_amount"])
    interest_rate = float(serializer.validated_data["interest_rate"])
    tenure = serializer.validated_data["tenure"]

    # Step 1: Check if customer exists
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    # Step 2: Reuse eligibility logic
    eligibility_request = {
        "customer_id": customer_id,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "tenure": tenure,
    }
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    fake_request = factory.post("/check-eligibility", eligibility_request, format="json")
    eligibility_response = check_eligibility(fake_request)

    eligibility_data = eligibility_response.data

    # Step 3: If not approved, return failure response
    if not eligibility_data["approval"]:
        return Response({
            "loan_id": None,
            "customer_id": customer_id,
            "loan_approved": False,
            "message": "Loan not approved based on eligibility criteria.",
            "monthly_installment": None,
        }, status=status.HTTP_200_OK)

    # Step 4: If approved, create loan entry in DB
    monthly_installment = eligibility_data["monthly_installment"]

    new_loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=eligibility_data["corrected_interest_rate"],
        monthly_payment=monthly_installment,
        emis_paid_on_time=0,  # starting fresh loan
        date_of_approval=date.today(),
        end_date=date.today() + timedelta(days=30*tenure)  # approx months
    )

    return Response({
        "loan_id": new_loan.loan_id,
        "customer_id": customer_id,
        "loan_approved": True,
        "message": "Loan successfully approved.",
        "monthly_installment": monthly_installment,
    }, status=status.HTTP_201_CREATED)

@api_view(["GET"])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.select_related("customer").get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

    response_data = {
        "loan_id": loan.loan_id,
        "customer": {
            "id": loan.customer.customer_id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age,
        },
        "loan_amount": float(loan.loan_amount),
        "interest_rate": float(loan.interest_rate),
        "monthly_installment": float(loan.monthly_payment),
        "tenure": loan.tenure,
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_loans(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    loans = Loan.objects.filter(customer=customer)

    loan_list = []
    today = date.today()

    for loan in loans:
        # calculate repayments left
        repayments_done = loan.emis_paid_on_time
        repayments_left = loan.tenure - repayments_done
        if repayments_left < 0:
            repayments_left = 0

        loan_list.append({
            "loan_id": loan.loan_id,
            "loan_amount": float(loan.loan_amount),
            "interest_rate": float(loan.interest_rate),
            "monthly_installment": float(loan.monthly_payment),
            "repayments_left": repayments_left,
        })

    return Response(loan_list, status=status.HTTP_200_OK)

