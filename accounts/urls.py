from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    ChangePasswordView,
    LogoutView,
    PasswordLoginView,
    ProfileView,
    SendOTPView,
    VerifyOTPView,
    SetPasswordView,
)

app_name = "accounts"

urlpatterns = [
    path(
        "login/password/",
        PasswordLoginView.as_view(),
        name="login-password",
    ),
    path(
        "login/otp/send/",
        SendOTPView.as_view(),
        name="login-otp-send",
    ),
    path(
        "login/otp/verify/",
        VerifyOTPView.as_view(),
        name="login-otp-verify",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "me/",
        ProfileView.as_view(),
        name="me",
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "set-password/",
        SetPasswordView.as_view(),
        name="set-password",
    ),
]
