from django.conf import settings
from django.core.cache import caches

from accounts.exceptions import OTPExpiredException, OTPBlockedException, OTPAlreadySentException, \
    OTPRequestLimitExceededException, OTPInvalidatedException, OTPInvalidException
from accounts.tasks import send_otp_task
from accounts.utils import generate_otp

cache = caches["auth"]


class OTPService:
    @staticmethod
    def _otp_key(phone: str) -> str:
        return f"otp:{phone}"

    @staticmethod
    def _attempt_key(phone: str) -> str:
        return f"otp:attempt:{phone}"

    @staticmethod
    def _request_key(phone: str) -> str:
        return f"otp:req:{phone}"

    @staticmethod
    def _block_key(phone: str) -> str:
        return f"otp:block:{phone}"

    @classmethod
    def send_otp(cls, phone: str) -> None:
        if cache.get(cls._block_key(phone)):
            raise OTPBlockedException()

        if cache.get(cls._otp_key(phone)):
            raise OTPAlreadySentException()

        request_key = cls._request_key(phone)

        req_count = cache.get(request_key)

        if req_count is None:
            cache.set(
                request_key,
                1,
                timeout=settings.OTP_REQUEST_WINDOW_SECONDS,
            )
            req_count = 1
        else:
            req_count = cache.incr(request_key)

        if req_count > settings.OTP_REQUEST_LIMIT:
            cache.set(
                cls._block_key(phone),
                1,
                timeout=settings.OTP_BLOCK_SECONDS,
            )

            cache.delete_many(
                [
                    cls._otp_key(phone),
                    cls._attempt_key(phone),
                    request_key,
                ]
            )

            raise OTPRequestLimitExceededException()

        otp = generate_otp()

        cache.set(
            cls._otp_key(phone),
            otp,
            timeout=settings.OTP_TTL_SECONDS,
        )

        cache.delete(cls._attempt_key(phone))

        send_otp_task.delay(phone, otp)

    @classmethod
    def verify_otp(cls, phone: str, otp: str) -> bool:
        real = cache.get(cls._otp_key(phone))

        if real is None:
            raise OTPExpiredException()

        if otp != real:
            attempts = cache.get(cls._attempt_key(phone), 0) + 1

            cache.set(
                cls._attempt_key(phone),
                attempts,
                timeout=settings.OTP_TTL_SECONDS,
            )

            if attempts >= settings.OTP_MAX_ATTEMPTS:
                cache.delete_many(
                    [
                        cls._otp_key(phone),
                        cls._attempt_key(phone),
                    ]
                )

                raise OTPInvalidatedException()

            raise OTPInvalidException()

        cache.delete_many(
            [
                cls._otp_key(phone),
                cls._attempt_key(phone),
                cls._request_key(phone),
                cls._block_key(phone),
            ]
        )

        return True
