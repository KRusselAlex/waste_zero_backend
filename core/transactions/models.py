from django.db import models
from orders.models import Order

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]
    PAYMENT_CHOICES = [
        ('Stripe', 'Stripe'),
        ('PayPal', 'PayPal'),
        ('Apple Pay', 'Apple Pay'),
        ('Google Pay', 'Google Pay'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)