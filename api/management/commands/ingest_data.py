from django.core.management.base import BaseCommand
from api.models import Customer, Loan
import pandas as pd
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Ingest data from customer_data.xlsx and loan_data.xlsx"

    def handle(self, *args, **kwargs):
        # Load customer data
        customer_df = pd.read_excel("customer_data.xlsx")
        print(1000)
        for _, row in customer_df.iterrows():
            customer, created = Customer.objects.update_or_create(
                phone_number=row['Phone Number'],
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row['Age'],
                    'monthly_income': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                    'current_debt': 0,
                }
            )
            print(f"{'Created' if created else 'Updated'} customer {customer.customer_id}")

        # Load loan data
        loan_df = pd.read_excel("loan_data.xlsx")
        for _, row in loan_df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])
            except Customer.DoesNotExist:
                # print(f"Skipping loan with unknown customer_id {row['customer_id']}")
                continue

            # end_date = date.today() + timedelta(days=30 * int(row['tenure']))
            loan, created = Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    'customer': customer,
                    'loan_amount': row['Loan Amount'],
                    'interest_rate': row['Interest Rate'],
                    'tenure': row['Tenure'],
                    'monthly_installment': row['Monthly payment'],
                    'start_date': row['Date of Approval'],
                    'end_date': row['End Date'],
                    'emis_paid_on_time': row['EMIs paid on Time']
                }
            )
            print(f"{'Created' if created else 'Updated'} loan {loan.loan_id}")
