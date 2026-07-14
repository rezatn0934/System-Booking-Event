from bookings.selectors.event import EventSelector
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bookings.models import Event
from bookings.serializers import (
    EventCreateSerializer,
    EventDetailSerializer,
)
from bookings.services.event_service import EventService


class EventModelViewSet(ModelViewSet):
    queryset = Event.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        "title",
        "description",
    )

    filterset_fields = ("event_date",)

    ordering_fields = (
        "capacity",
        "event_date",
        "created_at",
    )

    ordering = ("event_date",)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return EventDetailSerializer
        return EventCreateSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self):
        if self.action == "retrieve":
            return EventSelector.detail(self.kwargs["pk"])

        return super().get_object()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = EventService.create(
            **serializer.validated_data,
        )

        return Response(
            EventDetailSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        event = EventService.update(
            event_id=instance.id,
            **serializer.validated_data,
        )

        return Response(EventDetailSerializer(event).data)

    def destroy(self, request, *args, **kwargs):
        EventService.delete(
            event_id=self.get_object().id,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
