import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .models import OTPToken


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Please enter your email.")
            return redirect("login:login")

        user, _created = User.objects.get_or_create(
            username=email,
            defaults={"email": email},
        )

        if not user.email:
            user.email = email
            user.save(update_fields=["email"])

        otp = f"{secrets.randbelow(1_000_000):06d}"

        OTPToken.objects.filter(user=user, is_used=False).update(is_used=True)
        OTPToken.create_for_user(user, otp)

        send_mail(
            subject="Your AutoCareX login code",
            message=f"Your AutoCareX OTP is {otp}. It expires in 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session["otp_user_id"] = user.id
        messages.success(request, "OTP sent. Check your email or terminal console.")
        return redirect("login:verify")

    return render(request, "login/login.html")


def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    user_id = request.session.get("otp_user_id")

    if not user_id:
        messages.error(request, "Please request a new OTP.")
        return redirect("login:login")

    if request.method == "POST":
        otp = request.POST.get("otp", "").strip()

        token = (
            OTPToken.objects.filter(user_id=user_id, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not token or not token.is_valid(otp):
            messages.error(request, "Invalid or expired OTP.")
            return redirect("login:verify")

        token.mark_used()
        auth_login(request, token.user)
        request.session.pop("otp_user_id", None)

        messages.success(request, "Logged in successfully.")
        return redirect("dashboard:index")

    return render(request, "login/verify_otp.html")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out.")
    return redirect("login:login")
