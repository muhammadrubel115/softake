from django.db import transaction
from inventory.services.audit import log_audit

def change_status(*, actor, obj, new_status):
    old_value = {"status": obj.status}
    obj.status = new_status

    with transaction.atomic():
        obj.save(update_fields=["status"])

        transaction.on_commit(lambda: log_audit(
            actor=actor,
            action="status_changed",
            object_type=obj.__class__.__name__,
            object_id=obj.id,
            old_value=old_value,
            new_value={"status": new_status},
        ))
