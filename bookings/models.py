from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BookingStatus(models.TextChoices):
    PENDING = "PE", _("Pending")
    CONFIRMED = "CO", _("Confirmed")
    CANCELED = "CA", _("Canceled")
    EXPIRED = "EX", _("Expired")


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    event_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("event_date",)

    def __str__(self):
        return self.title


class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="bookings")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )

    status = models.CharField(
        max_length=2,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        db_index=True,
    )

    expires_at = models.DateTimeField(
        default=lambda: timezone.now() + timedelta(minutes=10),
        db_index=True,
    )

    confirmed_at = models.DateTimeField(null=True, blank=True)

    canceled_at = models.DateTimeField(null=True, blank=True)

    expired_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("event", "user"),
                condition=Q(
                    status__in=[
                        BookingStatus.PENDING,
                        BookingStatus.CONFIRMED,
                    ]
                ),
                name="unique_active_booking_per_user",
            ),
        ]
        indexes = [
            models.Index(
                fields=("event", "status"),
            ),
            models.Index(
                fields=("status", "expires_at"),
            ),
        ]

    def __str__(self):
        return f"{self.user.id} - {self.event.id}"
