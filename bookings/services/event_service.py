from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import NotFound, ValidationError

from bookings.exceptions import BusinessLogicException
from bookings.models import Event


class EventService:
    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        title: str,
        description: str,
        capacity: int,
        event_date,
    ) -> Event:
        if event_date <= timezone.now():
            raise ValidationError({"event_date": "Event date must be in the future."})

        return Event.objects.create(
            title=title,
            description=description,
            capacity=capacity,
            event_date=event_date,
        )

    @classmethod
    @transaction.atomic
    def update(
        cls,
        *,
        event_id: int,
        **validated_data,
    ) -> Event:
        try:
            event = Event.objects.select_for_update().get(
                pk=event_id,
            )
        except Event.DoesNotExist:
            raise NotFound("Event not found.")

        event_date = validated_data.get("event_date")
        if event_date and event_date <= timezone.now():
            raise BusinessLogicException("Event date must be in the future.")
        for field, value in validated_data.items():
            setattr(event, field, value)

        event.save(update_fields=validated_data.keys())

        return event

    @staticmethod
    @transaction.atomic
    def delete(*, event_id: int) -> None:
        try:
            event = Event.objects.select_for_update().get(pk=event_id)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")

        if event.bookings.exists():
            raise BusinessLogicException(
                "Event with existing bookings cannot be deleted."
            )

        if event.event_date <= timezone.now():
            raise BusinessLogicException("Past events cannot be deleted.")

        event.delete()
