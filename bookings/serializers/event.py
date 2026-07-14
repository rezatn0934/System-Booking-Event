from rest_framework import serializers

from bookings.models import Event


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "title",
            "description",
            "capacity",
            "event_date",
        )


class EventDetailSerializer(serializers.ModelSerializer):
    active_booking_count = serializers.IntegerField(read_only=True)
    confirmed_booking_count = serializers.IntegerField(read_only=True)
    remaining_capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "capacity",
            "event_date",
            "active_booking_count",
            "confirmed_booking_count",
            "remaining_capacity",
        )
