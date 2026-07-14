from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.authenticators import PhoneBackend
from accounts.models import User
from accounts.validators import phone_number_validator


class PasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=11,
        validators=[phone_number_validator],
    )
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = PhoneBackend().authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError("username or password is incorrect.")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive.")

        attrs["user"] = user
        return attrs


class SendOTPSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=11,
        validators=[phone_number_validator],
    )


class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=11,
        validators=[phone_number_validator],
    )
    otp = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
        )


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")

        return value

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.has_usable_password():
            raise serializers.ValidationError("Password has not been set yet.")

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        validate_password(attrs["new_password"], user)

        return attrs


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        if user.has_usable_password():
            raise serializers.ValidationError("Password has already been set.")

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        validate_password(attrs["new_password"], user)

        return attrs
