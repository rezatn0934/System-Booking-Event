from django.db.models import Count, F, IntegerField, Q
from django.db.models.expressions import ExpressionWrapper
from rest_framework.exceptions import NotFound

from bookings.models import BookingStatus, Event


class EventSelector:
    @classmethod
    def base_queryset(cls):
        return Event.objects.annotate(
            active_booking_count=Count(
                "bookings",
                filter=Q(
                    bookings__status__in=[
                        BookingStatus.PENDING,
                        BookingStatus.CONFIRMED,
                    ]
                ),
            ),
            confirmed_booking_count=Count(
                "bookings",
                filter=Q(bookings__status=BookingStatus.CONFIRMED),
            ),
        ).annotate(
            remaining_capacity=ExpressionWrapper(
                F("capacity") - F("active_booking_count"),
                output_field=IntegerField(),
            )
        )

    @classmethod
    def detail(cls, event_id: int) -> Event:
        try:
            return cls.base_queryset().get(pk=event_id)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")

    @classmethod
    def list(cls):

        return cls.base_queryset().order_by(
            "event_date"
        )