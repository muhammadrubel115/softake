from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone

from inventory.models.audit_log import AuditLog
from inventory.models.orders import Order
from inventory.models.products import Product
from inventory.models.reservations import Reservation

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "action",
        "object_type",
        "object_id",
        "actor",
        "created_at",
    )

    list_filter = (
        "action",
        "object_type",
        "created_at",
    )

    search_fields = (
        "object_id",
        "object_type",
        "action",
        "actor__username",
        "actor__email",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "actor",
        "action",
        "object_type",
        "object_id",
        "old_value",
        "new_value",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class OrderAdminForm(ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def clean_status(self):
        new_status = self.cleaned_data.get("status")

        if self.instance.pk:
            old_status = self.instance.status
            if new_status != old_status:
                if new_status not in Order.TRANSITION_MAP.get(old_status, []):
                    raise ValidationError(
                        f"Invalid transition: {old_status} → {new_status}"
                    )

        return new_status


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm

    list_display = (
        "id",
        "user",
        "status",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "user__username",
        "user__email",
    )

    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    list_select_related = ("user",)

class ProductAdminForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        available = cleaned_data.get("available_stock")
        reserved = cleaned_data.get("reserved_stock")
        total = cleaned_data.get("total_stock")

        if (
            available is not None
            and reserved is not None
            and total is not None
            and available + reserved != total
        ):
            raise ValidationError(
                "available_stock + reserved_stock must equal total_stock"
            )

        return cleaned_data


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    list_display = (
        "id",
        "name",
        "total_stock",
        "available_stock",
        "reserved_stock",
    )

    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "quantity",
        "is_active",
        "expires_at",
        "is_expired",
    )

    list_filter = (
        "is_active",
        "expires_at",
    )

    search_fields = ("product__name",)
    ordering = ("-expires_at",)
    list_select_related = ("product",)
    readonly_fields = ("expires_at",)

    def is_expired(self, obj):
        return obj.expires_at <= timezone.now()

    is_expired.boolean = True
