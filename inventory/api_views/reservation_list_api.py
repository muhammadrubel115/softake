from rest_framework import generics
from inventory.models.reservations import Reservation
from inventory.serializers.reservation_serializer import ReservationSerializer
from rest_framework.permissions import IsAuthenticated

class ReservationListAPIView(generics.ListAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
