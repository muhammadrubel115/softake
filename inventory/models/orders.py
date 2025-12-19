from django.db import models
from django.conf import settings
from inventory.order_states import validate_transition


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        db_index=True,          # important for filtering by user
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True           # filter by status
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True           # range queries + sorting
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True           # date range filter + newest sorting
    )

    TRANSITION_MAP = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['shipped'],
        'shipped': ['delivered'],
        'delivered': [],
        'cancelled': [],
    }

    class Meta:
        ordering = ['-created_at']  # default: newest first
        indexes = [
            # Common filter: status + date range
            models.Index(fields=['status', 'created_at']),

            # Sorting by newest
            models.Index(fields=['-created_at']),

            # Sorting + filtering by order value
            models.Index(fields=['-total_amount']),

            # Cursor pagination optimization
            models.Index(fields=['created_at', 'id']),
        ]

    def __str__(self):
        return f"Order #{self.id} ({self.status})"

    def transition_to(self, new_status: str):
        """
        State transition only.
        No side effects, no audit, no permissions.
        """
        validate_transition(self.status, new_status)
        self.status = new_status
        self.save(update_fields=['status'])
