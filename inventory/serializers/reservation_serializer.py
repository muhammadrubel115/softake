from rest_framework import serializers
from django.db import transaction
from inventory.models.reservations import Reservation
from inventory.models.products import Product
from django.utils import timezone

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'product', 'quantity', 'expires_at', 'is_active']
        read_only_fields = ['expires_at', 'is_active']

    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity']

        with transaction.atomic():
            # Lock the product row to ensure concurrency safety
            product = Product.objects.select_for_update().get(id=product.id)

            if product.available_stock < quantity:
                raise serializers.ValidationError("Not enough stock available.")

            # Deduct available stock, add reserved stock
            product.available_stock -= quantity
            product.reserved_stock += quantity
            product.save()

            # Set expiration time
            validated_data['expires_at'] = timezone.now() + timezone.timedelta(minutes=10)
            reservation = Reservation.objects.create(**validated_data)

        return reservation
