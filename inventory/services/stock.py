from django.db import transaction
from inventory.services.audit import log_audit

def adjust_stock(*, actor, product, delta, reason):
    old_value = {
        "available_stock": product.available_stock,
        "reserved_stock": product.reserved_stock,
    }

    product.available_stock += delta

    with transaction.atomic():
        product.save(update_fields=["available_stock"])

        transaction.on_commit(lambda: log_audit(
            actor=actor,
            action="stock_adjusted",
            object_type="Product",
            object_id=product.id,
            old_value=old_value,
            new_value={
                "available_stock": product.available_stock,
                "reason": reason,
                "delta": delta,
            },
        ))
