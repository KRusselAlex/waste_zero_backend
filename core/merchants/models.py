from django.db import models
from users.models import User

# merchants/models.py
class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=50)
    address = models.TextField()
    description = models.TextField()
    phone=models.TextField()
    pickup_hours = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)  # Ajout de la vérification
    max_price_limit = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # Prix max
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
