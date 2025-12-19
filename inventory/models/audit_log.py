
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    actor = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    null=True,
    blank=True,
    on_delete=models.SET_NULL
    )


    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=64)


    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        indexes = [
        models.Index(fields=['object_type', 'object_id']),
        models.Index(fields=['created_at']),
        ]


    def __str__(self):
        return f"{self.action} on {self.object_type}({self.object_id})"