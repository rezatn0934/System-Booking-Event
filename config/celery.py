import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "expire-pending-bookings_runner": {
        "task": "bookings.recover_expired_bookings",
        "schedule": timedelta(minutes=30),
    },
}
app.autodiscover_tasks()
