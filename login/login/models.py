from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class OTPToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otp_tokens",
    )
    token_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def create_for_user(cls, user, otp):
        return cls.objects.create(
            user=user,
            token_hash=make_password(otp),
            expires_at=timezone.now() + timedelta(minutes=5),
        )

    def is_valid(self, otp):
        return (
            not self.is_used
            and timezone.now() <= self.expires_at
            and check_password(otp, self.token_hash)
        )

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"OTP for {self.user} created at {self.created_at}"
