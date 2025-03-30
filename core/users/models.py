from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.utils import generate_verification_token
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('merchant', 'Merchant'),
        ('consumer', 'Consumer'),
        ('administrator', 'Administrator'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='consumer')
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.FileField(upload_to='static/profiles/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    token_created_at = models.DateTimeField(null=True, blank=True)


    def generate_verification_token(self):
        self.verification_token = generate_verification_token()
        self.token_created_at = timezone.now()
        self.save()
        return self.verification_token
