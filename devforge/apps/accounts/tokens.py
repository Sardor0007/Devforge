from django.contrib.auth.tokens import PasswordResetTokenGenerator
import hashlib


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Email tasdiqlash uchun token"""
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active) + str(user.email)
        )


class PasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """Parol tiklash uchun token"""
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.password) + str(user.email)
        )


email_verification_token = EmailVerificationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()
