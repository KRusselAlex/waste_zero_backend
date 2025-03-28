from django.db import models
from users.models import User

class Consumer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    delivery_address = models.TextField()
    food_preferences = models.TextField()
    purchase_history = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
