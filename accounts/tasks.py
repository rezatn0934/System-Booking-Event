from celery import shared_task


@shared_task(bind=True, name="auth.send_otp")
def send_otp_task(self, phone: str, otp: str):
    print(f"[OTP] Sending OTP {otp} to {phone}")

    # TODO:
    # SMS Provider
