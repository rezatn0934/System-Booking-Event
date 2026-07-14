from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create a default admin user'

    def handle(self, *args, **options):
        admin = get_user_model().objects.filter(username=settings.SUPERUSER,)
        if admin.count() <= 0:
            admin = get_user_model().objects.create_superuser(username=settings.SUPERUSER,
                                                              password=settings.SUPERPASS)
            admin.is_active = True
            print("default superuser created")
