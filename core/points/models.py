from django.db import models

from users.models import User

class Point(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def add_points(self, amount):
        self.balance += amount
        self.save()

