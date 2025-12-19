from django.db import transaction
from inventory.services.audit import log_audit

def create_order(*, actor, order):
    old_value = None
    new_value = {
        "user_id": order.user_id,
        "total_amount": str(order.total_amount),
        "status": order.status,
    }

    with transaction.atomic():
        order.save()

        transaction.on_commit(lambda: log_audit(
            actor=actor,
            action="order_created",
            object_type="Order",
            object_id=order.id,
            old_value=old_value,
            new_value=new_value,
        ))
