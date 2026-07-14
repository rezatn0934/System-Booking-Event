from rest_framework import status
from rest_framework.exceptions import APIException


class OTPException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "otp_error"
    default_detail = "OTP error."


class OTPBlockedException(OTPException):
    default_code = "otp_blocked"
    default_detail = "OTP is temporarily blocked. Please try again later."


class OTPAlreadySentException(OTPException):
    default_code = "otp_already_sent"
    default_detail = (
        "OTP has already been sent. Please wait before requesting another code."
    )


class OTPRequestLimitExceededException(OTPException):
    default_code = "otp_request_limit_exceeded"
    default_detail = "OTP request limit exceeded. Please try again later."


class OTPExpiredException(OTPException):
    default_code = "otp_expired"
    default_detail = "OTP has expired. Please request a new one."


class OTPInvalidException(OTPException):
    default_code = "otp_invalid"
    default_detail = "The OTP you entered is invalid."


class OTPInvalidatedException(OTPException):
    default_code = "otp_invalidated"
    default_detail = "OTP has been invalidated due to too many failed attempts."
