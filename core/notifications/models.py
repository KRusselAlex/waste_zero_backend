from django.db import models
from users.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('reservation', 'Reservation'),
        ('order_ready', 'Order Ready'),
        ('new_offer', 'New Offer'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('read', 'Read'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notification_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
