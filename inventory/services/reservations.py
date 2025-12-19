from django.db import transaction
from django.core.exceptions import ValidationError

from inventory.models.products import Product
from inventory.models.reservations import Reservation
from inventory.services.audit import log_audit


def create_reservation(*, product_id: int, quantity: int, user):
    with transaction.atomic():
        product = (
            Product.objects
            .select_for_update()
            .get(id=product_id)
        )

        if product.available_stock < quantity:
            raise ValidationError("Insufficient stock")

        # Capture OLD state (before mutation)
        old_value = {
            "available_stock": product.available_stock,
            "reserved_stock": product.reserved_stock,
        }

        # Mutate state
        product.available_stock -= quantity
        product.reserved_stock += quantity
        product.save(update_fields=["available_stock", "reserved_stock"])

        reservation = Reservation.objects.create(
            product=product,
            quantity=quantity,
            user=user
        )

        # Capture NEW state (after mutation)
        new_value = {
            "available_stock": product.available_stock,
            "reserved_stock": product.reserved_stock,
            "quantity_reserved": quantity,
        }

        # Audit AFTER successful commit
        transaction.on_commit(lambda: log_audit(
            actor=user,
            action="reservation_created",
            object_type="Reservation",
            object_id=reservation.id,
            old_value=old_value,
            new_value=new_value,
        ))

        return reservation
