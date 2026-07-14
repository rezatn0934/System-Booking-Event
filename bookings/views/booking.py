from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bookings.models import Booking
from bookings.serializers import (
    BookingCreateSerializer,
    BookingSerializer,
)
from bookings.services.booking_service import BookingService


class BookingModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = BookingCreateSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Booking.objects.select_related(
        "event",
        "user",
    )
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = ("event__title",)
    filterset_fields = (
        "status",
        "event",
        "user",
    )
    ordering_fields = (
        "created_at",
        "confirmed_at",
        "expires_at",
        "status",
        "event__event_date",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        qs = self.queryset

        if self.request.user.is_staff:
            return qs

        return qs.filter(
            user=self.request.user,
        )

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        booking = BookingService.confirm(
            user=request.user,
            booking_id=self.kwargs["pk"],
        )

        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = BookingService.cancel(
            user=request.user,
            booking_id=self.kwargs["pk"],
        )

        return Response(self.get_serializer(booking).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = BookingService.create(
            user=request.user,
            event_id=serializer.validated_data["event_id"],
        )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )
