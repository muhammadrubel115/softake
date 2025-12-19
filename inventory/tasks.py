from celery import shared_task
from django.db import transaction
from django.utils import timezone
from inventory.models.reservations import Reservation
from inventory.models.products import Product
from inventory.services.audit import log_audit  # optional

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def release_expired_reservations(self, *args, **kwargs):
    """
    Releases expired reservations safely:
    - Marks reservation as inactive
    - Returns quantity to available_stock
    - Deducts from reserved_stock without going negative
    """
    now = timezone.now()
    expired_reservations = Reservation.objects.filter(is_active=True, expires_at__lte=now)

    released_count = 0

    for reservation in expired_reservations:
        with transaction.atomic():
            # Lock product row for safe concurrency
            product = Product.objects.select_for_update().get(id=reservation.product_id)

            # Calculate safe quantity to release
            release_qty = min(reservation.quantity, product.reserved_stock)

            # Release stock safely
            product.reserved_stock -= release_qty
            product.available_stock += release_qty

            # Ensure invariant: available + reserved == total
            product.available_stock = max(product.available_stock, 0)
            product.reserved_stock = max(product.reserved_stock, 0)
            product.save()

            # Mark reservation inactive
            reservation.is_active = False
            reservation.save()

            # Optional audit log
            
            released_count += 1

    return f"Released {released_count} expired reservations"
