from django.db import models
from users.models import User

class Administrator(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('moderator', 'Moderator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    admin_role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permissions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
