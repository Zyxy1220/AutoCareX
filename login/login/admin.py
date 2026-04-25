from django.contrib import admin

from .models import OTPToken


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "expires_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("token_hash", "created_at", "expires_at")
