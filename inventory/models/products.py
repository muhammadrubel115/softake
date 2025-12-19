from django.db import models
from django.core.exceptions import ValidationError


class Product(models.Model):
    name = models.CharField(max_length=255)

    total_stock = models.PositiveIntegerField()
    available_stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)

    def clean(self):
        """
        Domain invariant validation.
        Called by admin, forms, and full_clean().
        """
        if (
            self.available_stock is not None
            and self.reserved_stock is not None
            and self.total_stock is not None
        ):
            if self.available_stock + self.reserved_stock != self.total_stock:
                raise ValidationError({
                    'available_stock': 'available + reserved must equal total stock',
                    'reserved_stock': 'available + reserved must equal total stock',
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # ensures clean() runs everywhere
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
 