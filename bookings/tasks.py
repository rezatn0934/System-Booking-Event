from celery import shared_task
from django.utils import timezone

from bookings.models import Booking, BookingStatus
from bookings.services.booking_service import BookingService
from config.base_task import CeleryBaseTask


@shared_task(
    base=CeleryBaseTask,
    name="bookings.recover_expired_bookings",
    ignore_result=True,
)
def recover_expired_bookings():
    now = timezone.now()

    booking_ids = (
        Booking.objects.filter(
            status=BookingStatus.PENDING,
            expires_at__lte=now,
        )
        .values_list("id", flat=True)
        .iterator()
    )

    for booking_id in booking_ids:
        expire_booking.delay(booking_id=booking_id)


@shared_task(
    base=CeleryBaseTask,
    name="bookings.expire_booking",
    ignore_result=True,
)
def expire_booking(booking_id: int):
    BookingService.expire(booking_id=booking_id)
