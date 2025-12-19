from django.db import transaction
from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from inventory.models.products import Product
from inventory.services.reservations import create_reservation
from inventory.services.audit import log_audit

class ReservationCreateAPIView(APIView):
    def post(self, request):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        try:
            with transaction.atomic():
                # Lock the product row for concurrency
                product = Product.objects.select_for_update().get(id=product_id)

                if product.available_stock < quantity:
                    return Response({'error': 'Insufficient stock'}, status=409)

                # Update stock
                product.available_stock -= quantity
                product.reserved_stock += quantity
                product.save()

                # Create reservation inside the same atomic block
                reservation = create_reservation(
                    product=product,  # Pass the locked product object
                    quantity=quantity,
                    user=request.user
                )

                # Audit log
                log_audit(
                    actor=request.user,
                    action='reservation_created',
                    obj=reservation,
                    new_value={
                        'quantity': reservation.quantity,
                        'expires_at': reservation.expires_at.isoformat()
                    }
                )

        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

        return Response({'reservation_id': reservation.id}, status=201)
