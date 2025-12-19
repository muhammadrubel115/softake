from django.utils.dateparse import parse_date
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inventory.models.orders import Order
from inventory.serializers.order_serializer import OrderSerializer


class OrderCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'   # newest first
    cursor_query_param = 'cursor'


class OrderViewSet(ReadOnlyModelViewSet):
    """
    GET /api/orders/

    Supports:
    - filter: date range, status, min/max total
    - sort: newest, highest value
    - cursor pagination
    """
    serializer_class = OrderSerializer
    pagination_class = OrderCursorPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]  # ✅ authentication

    def get_queryset(self):
        qs = Order.objects.select_related('user')  # fetch user in the same query

        # ---- Filters ----
        status = self.request.query_params.get('status')
        min_total = self.request.query_params.get('min_total')
        max_total = self.request.query_params.get('max_total')
        created_after = self.request.query_params.get('created_after')
        created_before = self.request.query_params.get('created_before')

        if status:
            qs = qs.filter(status=status)

        if min_total:
            qs = qs.filter(total_amount__gte=min_total)

        if max_total:
            qs = qs.filter(total_amount__lte=max_total)

        if created_after:
            qs = qs.filter(created_at__date__gte=parse_date(created_after))

        if created_before:
            qs = qs.filter(created_at__date__lte=parse_date(created_before))

        return qs

    def list(self, request, *args, **kwargs):
        """
        Override list to include request_id explicitly in response
        """
        response = super().list(request, *args, **kwargs)
        # request_id is automatically injected by middleware
        return response
