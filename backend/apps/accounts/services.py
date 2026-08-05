import random
import string
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

OTP_EXPIRY_MINUTES = 10


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP string."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(user: User, subject: str = 'Your FINOVO Verification Code') -> str:
    """
    Generate and store a new OTP for the user, then send it via email.
    Returns the generated OTP (useful for testing).
    """
    otp = generate_otp()
    user.email_otp = otp
    user.email_otp_expiry = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    user.save(update_fields=['email_otp', 'email_otp_expiry'])

    send_mail(
        subject=subject,
        message=f"Your FINOVO verification code is: {otp}\n\nThis code expires in {OTP_EXPIRY_MINUTES} minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return otp


def verify_otp(user: User, otp: str) -> bool:
    """
    Verify the given OTP against the stored value.
    Returns True if valid and not expired, False otherwise.
    Clears the OTP on successful verification.
    """
    if not user.email_otp or not user.email_otp_expiry:
        return False
    if user.email_otp != otp:
        return False
    if timezone.now() > user.email_otp_expiry:
        return False

    # Clear OTP after successful use
    user.email_otp = None
    user.email_otp_expiry = None
    user.save(update_fields=['email_otp', 'email_otp_expiry'])
    return True
