from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    PasswordLoginSerializer,
    VerifyOTPSerializer,
    SendOTPSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    SetPasswordSerializer,
)
from accounts.services.auth import JWTService
from accounts.services.otp_service import OTPService
from drf_spectacular.utils import OpenApiResponse, extend_schema

User = get_user_model()


@extend_schema(
    tags=["Authentication"],
    summary="Login with username and password",
    request=PasswordLoginSerializer,
    responses={
        200: OpenApiResponse(description="Login successful"),
        400: OpenApiResponse(description="Validation error"),
    },
)
class PasswordLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = JWTService.create_tokens(serializer.validated_data["user"])

        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Authentication"],
    summary="Verify OTP",
    request=VerifyOTPSerializer,
    responses={
        200: OpenApiResponse(description="OTP verified successfully"),
        400: OpenApiResponse(description="Invalid OTP"),
    },
)
class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        otp = serializer.validated_data["otp"]

        OTPService.verify_otp(username, otp)

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "is_active": True,
            },
        )

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        tokens = JWTService.create_tokens(user)

        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Authentication"],
    summary="Send OTP",
    request=SendOTPSerializer,
    responses={
        200: OpenApiResponse(description="OTP sent successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
)
class SendOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        OTPService.send_otp(
            serializer.validated_data["username"],
        )

        return Response(
            {
                "detail": "OTP sent successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Profile"],
        summary="Get current user profile",
        responses=UserSerializer,
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=["Profile"],
        summary="Update current user profile",
        request=UpdateProfileSerializer,
        responses=UserSerializer,
    )
    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Logout",
        request=LogoutSerializer,
        responses={
            204: OpenApiResponse(description="Logged out successfully"),
        },
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        RefreshToken(serializer.validated_data["refresh"]).blacklist()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Change password",
        request=ChangePasswordSerializer,
        responses={
            204: OpenApiResponse(description="Password changed successfully"),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Set password",
        request=SetPasswordSerializer,
        responses={
            204: OpenApiResponse(description="Password set successfully"),
        },
    )
    def post(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])

        return Response(status=status.HTTP_204_NO_CONTENT)
