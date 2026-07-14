from django.urls import include, path
from rest_framework.routers import DefaultRouter

from bookings.views import (
    BookingModelViewSet,
    EventModelViewSet,
)

router = DefaultRouter()

router.register(
    r"events",
    EventModelViewSet,
    basename="event",
)

router.register(
    r"bookings",
    BookingModelViewSet,
    basename="booking",
)

urlpatterns = [
    path("", include(router.urls)),
]
