from django.utils import timezone

from bookings.exceptions import BusinessLogicException, ResourceExpiredException
from bookings.models import Booking, BookingStatus


class BaseBookingState:
    def __init__(self, booking: Booking):
        self.booking = booking

    def confirm(self):
        raise BusinessLogicException("Operation not allowed.")

    def cancel(self):
        raise BusinessLogicException("Operation not allowed.")

    def expire(self):
        raise BusinessLogicException("Operation not allowed.")


class PendingState(BaseBookingState):
    def confirm(self):
        self.booking.status = BookingStatus.CONFIRMED
        self.booking.confirmed_at = timezone.now()

        self.booking.save(
            update_fields=[
                "status",
                "confirmed_at",
                "updated_at",
            ]
        )

        return self.booking

    def cancel(self):
        self.booking.status = BookingStatus.CANCELED
        self.booking.canceled_at = timezone.now()

        self.booking.save(
            update_fields=[
                "status",
                "canceled_at",
                "updated_at",
            ]
        )

        return self.booking

    def expire(self):
        self.booking.status = BookingStatus.EXPIRED
        self.booking.expired_at = timezone.now()

        self.booking.save(
            update_fields=[
                "status",
                "expired_at",
                "updated_at",
            ]
        )

        return self.booking


class ConfirmedState(BaseBookingState):
    def confirm(self):
        raise BusinessLogicException("Booking already confirmed.")

    def cancel(self):
        self.booking.status = BookingStatus.CANCELED
        self.booking.canceled_at = timezone.now()

        self.booking.save(
            update_fields=[
                "status",
                "canceled_at",
                "updated_at",
            ]
        )

        return self.booking

    def expire(self):
        raise BusinessLogicException("Confirmed booking cannot be expired.")


class CanceledState(BaseBookingState):
    def confirm(self):
        raise BusinessLogicException("Canceled booking cannot be confirmed.")

    def cancel(self):
        raise BusinessLogicException("Booking already canceled.")

    def expire(self):
        raise BusinessLogicException("Canceled booking cannot be expired.")


class ExpiredState(BaseBookingState):
    def confirm(self):
        raise ResourceExpiredException("Booking has expired.")

    def cancel(self):
        raise ResourceExpiredException("Booking has expired.")

    def expire(self):
        raise BusinessLogicException("Booking already expired.")
