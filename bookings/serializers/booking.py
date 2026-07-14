from rest_framework import serializers

from accounts.serializers import UserSerializer
from bookings.models import Booking
from bookings.serializers import EventCreateSerializer


class BookingCreateSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(min_value=1)


class BookingSerializer(serializers.ModelSerializer):
    event = EventCreateSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "event",
            "user",
            "status",
            "expires_at",
            "confirmed_at",
            "created_at",
        )
