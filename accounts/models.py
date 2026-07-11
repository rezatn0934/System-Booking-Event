from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

phone_number_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message=_("Phone number must be in the format 09XXXXXXXXX."),
)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(
        _("Phone Number"),
        max_length=11,
        unique=True,
        validators=[phone_number_validator],
    )

    first_name = models.CharField(
        _("First Name"), max_length=50, blank=True, default=""
    )

    last_name = models.CharField(_("Last Name"), max_length=100, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ("-date_joined",)
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.phone

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
