# inventory/service/audit.py
import threading
from inventory.models.audit_log import AuditLog

def _create_audit(actor, action, object_type, object_id, old_value=None, new_value=None):
    """Synchronous DB save"""
    AuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        old_value=old_value,
        new_value=new_value,
    )

def log_audit(actor, action, object_type, object_id, old_value=None, new_value=None):
    """
    Fire-and-forget audit logger using a background thread.
    """
    thread = threading.Thread(
        target=_create_audit,
        args=(actor, action, object_type, object_id, old_value, new_value),
        daemon=True  # thread won't block Django shutdown
    )
    thread.start()
    thread.join()  # Ensure the audit log is created before proceeding