from django.db import models
from django.utils import timezone
from datetime import timedelta
from inventory.models.products import Product


class Reservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)


@staticmethod
def expiry_time():

    return timezone.now() + timedelta(minutes=10)