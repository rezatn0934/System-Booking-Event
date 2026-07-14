from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="Phone number must start with '09' and contain exactly 11 digits.",
)