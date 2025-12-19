from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventory.api_views.order_set import OrderViewSet
from inventory.api_views.reservation_create_api import ReservationCreateAPIView
from inventory.api_views.reservation_list_api import ReservationListAPIView
from django.urls import path
from inventory.api_views.sample_api import TestAPIView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    # Orders API (optimized, cursor pagination)
    path('', include(router.urls)),

    # Reservation APIs
    path('reservations/', ReservationCreateAPIView.as_view(), name='reservation-create'),
    path('reservations/list/', ReservationListAPIView.as_view(), name='reservation-list'),

    path('test/', TestAPIView.as_view(), name='test-api'),

]
