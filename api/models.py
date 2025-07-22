from django.db import models

# customers/models.py

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    age = models.IntegerField()
    monthly_income = models.IntegerField(default=0)
    approved_limit = models.IntegerField()
    current_debt = models.FloatField(default=0.0)

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    interest_rate = models.FloatField()
    tenure = models.IntegerField()
    monthly_installment = models.FloatField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    emis_paid_on_time = models.IntegerField(default=0)
