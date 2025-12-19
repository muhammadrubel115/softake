from rest_framework import serializers
from inventory.models.orders import Order


class OrderSerializer(serializers.ModelSerializer):
    # Use select_related('user') in the queryset to avoid N+1 queries
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    # Uncomment below if you have a related OrderItem model
    # items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user_id',
            'user_username',
            'user_email',
            'status',
            'total_amount',
            'created_at',
            # 'items',  # include if you have related OrderItem
        ]
        read_only_fields = ['id', 'user_id', 'user_username', 'user_email', 'created_at']
