from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inventory.models.reservations import Reservation
from inventory.serializers.reservation_serializer import ReservationSerializer

class ReservationCreateAPIView(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Override create to provide custom response including request_id
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        # Return the response with request_id already added by middleware
        return Response(
            {
                "reservation": serializer.data,
                # 'request_id' will also be injected by RequestIDMiddleware
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
