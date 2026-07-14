from django.db import IntegrityError, transaction
from django.utils import timezone

from rest_framework.exceptions import NotFound

from bookings.models import Booking, BookingStatus, Event
from bookings.states.booking_context import BookingContext
from bookings.tasks import expire_booking
from bookings.exceptions import (
    BusinessLogicException,
    ResourceExpiredException,
)


class BookingService:
    @staticmethod
    @transaction.atomic
    def create(*, user, event_id: int) -> Booking:
        try:
            event = Event.objects.select_for_update().get(pk=event_id)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")

        if event.event_date <= timezone.now():
            raise BusinessLogicException("Booking for this event is closed.")

        # Idempotency
        booking = Booking.objects.filter(
            event=event,
            user=user,
            status__in=[
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
            ],
        ).first()

        if booking is not None:
            return booking

        active_booking_count = Booking.objects.filter(
            event=event,
            status__in=[
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
            ],
        ).count()

        if active_booking_count >= event.capacity:
            raise BusinessLogicException("Event capacity is full.")

        try:
            booking = Booking.objects.create(
                event=event,
                user=user,
            )
            transaction.on_commit(
                lambda: expire_booking.apply_async(
                    kwargs={"booking_id": booking.pk},
                    eta=booking.expires_at,
                )
            )

            return booking
        except IntegrityError:
            return Booking.objects.get(
                event=event,
                user=user,
                status__in=[
                    BookingStatus.PENDING,
                    BookingStatus.CONFIRMED,
                ],
            )

    @staticmethod
    @transaction.atomic
    def confirm(*, user, booking_id: int) -> Booking:
        try:
            booking = Booking.objects.select_for_update().get(
                pk=booking_id,
                user=user,
            )
        except Booking.DoesNotExist:
            raise NotFound("Booking not found.")

        if (
            booking.status == BookingStatus.PENDING
            and booking.expires_at <= timezone.now()
        ):
            BookingContext(booking).state.expire()
            raise ResourceExpiredException("Booking has expired.")

        _validate_event_not_started(event=booking.event)
        return BookingContext(booking).state.confirm()

    @staticmethod
    @transaction.atomic
    def cancel(*, user, booking_id: int) -> Booking:
        try:
            booking = (
                Booking.objects.select_for_update()
                .select_related("event")
                .get(
                    pk=booking_id,
                    user=user,
                )
            )
        except Booking.DoesNotExist:
            raise NotFound("Booking not found.")

        _validate_event_not_started(event=booking.event)

        return BookingContext(booking).state.cancel()

    @staticmethod
    @transaction.atomic
    def expire(*, booking_id: int) -> Booking | None:
        try:
            booking = Booking.objects.select_for_update().get(pk=booking_id)
        except Booking.DoesNotExist:
            return None

        if booking.status != BookingStatus.PENDING:
            return booking

        if booking.expires_at > timezone.now():
            return booking

        _validate_event_not_started(event=booking.event)
        return BookingContext(booking).state.expire()


def _validate_event_not_started(event):
    if event.event_date <= timezone.now():
        raise BusinessLogicException("This event has already started.")
