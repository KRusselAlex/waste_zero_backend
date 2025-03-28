from django.db import models
from users.models import User
from points.models import Point

class Donation(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('collected', 'Collected'),
    ]
    
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations_made')  # L'utilisateur qui fait le don
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations_received')  # L'utilisateur qui reçoit le don
    title = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.FileField(upload_to='static/donation_photos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Attribuer des points au donateur lorsqu'il fait un don."""
        super().save(*args, **kwargs)
        if self.status == 'available':
            Point.objects.create(user=self.donor, points=10)  # Attribuer 10 points pour chaque don

