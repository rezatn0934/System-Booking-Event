from bookings.models import Booking, BookingStatus
from bookings.states.booking_states import (
    BaseBookingState,
    PendingState,
    ConfirmedState,
    CanceledState,
    ExpiredState,
)


class BookingContext:
    def __init__(self, booking: Booking):
        self.booking = booking

    @property
    def state(self):
        match self.booking.status:
            case BookingStatus.PENDING:
                return PendingState(self.booking)

            case BookingStatus.CONFIRMED:
                return ConfirmedState(self.booking)

            case BookingStatus.CANCELED:
                return CanceledState(self.booking)

            case BookingStatus.EXPIRED:
                return ExpiredState(self.booking)

            case _:
                return BaseBookingState(self.booking)
