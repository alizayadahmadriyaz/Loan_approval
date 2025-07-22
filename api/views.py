from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import *
from datetime import date, timedelta
import math
from datetime import datetime

def calculate_emi(principal, rate, months):
    r = float(rate) / (12 * 100)
    return float((float(principal) * r * ((1 + r) ** months)) / (((1 + r) ** months) - 1))

@api_view(['POST'])
def register(request):
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    data = serializer.validated_data
    approved_limit = round(36 * data['monthly_income'] / 100000) * 100000
    customer = Customer.objects.create(**data, approved_limit=approved_limit)
    response = CustomerRegisterResponseSerializer(customer)
    return Response(response.data, status=201)
from django.db.models import Sum
@api_view(['POST'])
def check_eligibility(request):
    serializer = EligibilityRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data

    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=404)

    # Fetch all past loans
    loans = Loan.objects.filter(customer=customer)
    total_loans = loans.count()
    paid_on_time = sum(loan.emis_paid_on_time for loan in loans)

    current_year = datetime.now().year
    current_year_loans = loans.filter(start_date__year=current_year).count()

    total_approved_volume = loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0

    # Rule: if sum of current EMIs > approved limit, credit score = 0
    if customer.current_debt > customer.approved_limit:
        credit_score = 0
    else:
        # Basic weighted score example:
        credit_score = (
            (paid_on_time * 5) +
            (total_loans * 2) +
            (current_year_loans * 3) +
            (total_approved_volume / 100000)
        )
        credit_score = min(100, round(credit_score))  # Normalize to 100

    loan_amount = float(data['loan_amount'])
    interest_rate = float(data['interest_rate'])
    tenure = int(data['tenure'])
    emi = calculate_emi(loan_amount, interest_rate, tenure)
    total_future_emi = customer.current_debt + emi

    # Default
    approval = True
    corrected_interest_rate = interest_rate

    # Rule: total EMI burden
    if total_future_emi > (0.5 * customer.monthly_income):
        approval = False
        reason = "High EMI burden"

    # Rule: credit rating
    elif credit_score > 50:
        approval = True
    elif 30 < credit_score <= 50:
        if interest_rate < 12:
            corrected_interest_rate = 12
    elif 10 < credit_score <= 30:
        if interest_rate < 16:
            corrected_interest_rate = 16
    else:
        approval = False
        reason = "Low credit score"

    response_data = {
        "customer_id": customer.customer_id,
        "approval": approval,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_interest_rate,
        "tenure": tenure
        # "monthly_installment": calculate_emi(loan_amount, corrected_interest_rate, tenure),
        # "credit_score": credit_score,
    }

    # if not approval:
    #     response_data["reason"] = reason

    return Response(response_data, status=200)


@api_view(['POST'])
def create_loan(request):
    serializer = CreateLoanRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({"message": "Customer not found."}, status=404)

    emi = calculate_emi(data['loan_amount'], data['interest_rate'], data['tenure'])
    total_future_emi = customer.current_debt + emi
    max_emi_allowed = 0.5 * customer.monthly_income

    if total_future_emi > max_emi_allowed:
        return Response(CreateLoanResponseSerializer({
            "loan_id": None,
            "customer_id": customer.customer_id,
            "loan_approved": False,
            "message": "Loan not approved: High EMI burden.",
            "monthly_installment": emi
        }).data, status=200)

    # Create loan if eligible
    end_date = date.today() + timedelta(days=30 * data['tenure'])
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=data['loan_amount'],
        interest_rate=data['interest_rate'],
        tenure=data['tenure'],
        monthly_installment=emi,
        end_date=end_date
    )
    customer.current_debt += emi
    customer.save()

# class Loan(models.Model):
#     loan_id = models.AutoField(primary_key=True)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     loan_amount = models.FloatField()
#     interest_rate = models.FloatField()
#     tenure = models.IntegerField()
#     monthly_installment = models.FloatField()
#     start_date = models.DateField(auto_now_add=True)
#     end_date = models.DateField()
#     emis_paid_on_time = models.IntegerField()

    return Response(CreateLoanResponseSerializer({
        "loan_id": loan.loan_id,
        "customer_id": customer.customer_id,
        "loan_approved": True,
        "message": "Loan approved successfully.",
        "monthly_installment": emi
    }).data, status=201)




@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

    data = {
        "loan_id": loan_id,
        "customer": {
            "id": loan.customer.customer_id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure
    }
    serializer = ViewLoanResponseSerializer(data)
    return Response(serializer.data, status=200)




@api_view(['GET'])
def view_loans(request, customer_id):
    loans = Loan.objects.filter(customer__customer_id=customer_id)
    if not loans.exists():
        return Response({"error": "No loans found for the customer"}, status=status.HTTP_404_NOT_FOUND)

    # Calculate repayments_left for each loan
    loan_list = []
    for loan in loans:
        total_emis = loan.tenure
        emis_paid = loan.emis_paid_on_time
        repayments_left = max(total_emis - emis_paid, 0)

        loan_list.append({
            "loan_id": loan.loan_id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "repayments_left": repayments_left
        })

    serializer = LoanSummarySerializer(loan_list, many=True)
    return Response(serializer.data, status=200)



