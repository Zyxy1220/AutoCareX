from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .models import EmailVerificationToken


# ── Sign Up ────────────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email    = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not all([username, email, password]):
            messages.error(request, "All fields are required.")
            return render(request, "login/signup.html")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "login/signup.html")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "That username is already taken.")
            return render(request, "login/signup.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with that email already exists.")
            return render(request, "login/signup.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_active = False
        user.save()

        token_obj = EmailVerificationToken.create_for_user(user)
        verify_url = f"{settings.SITE_URL}/login/verify-email/{token_obj.token}/"

        send_mail(
            subject="Verify your AutoCareX account",
            message=(
                f"Hi {username},\n\n"
                f"Click the link below to verify your account:\n\n"
                f"{verify_url}\n\n"
                f"This link expires in 24 hours.\n\n"
                f"— The AutoCareX Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Account created! Check your email to verify.")
        return redirect("login:login")

    return render(request, "login/signup.html")

# ── Email Verification ─────────────────────────────────────────────────────────

def verify_email_view(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)

    if not token_obj.is_valid():
        token_obj.delete()
        messages.error(request, "This verification link has expired. Please sign up again.")
        return redirect("login:signup")

    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.delete()

    messages.success(request, "Email verified! You can now log in.")
    return redirect("login:login")


# ── Login ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()  # username or email
        password   = request.POST.get("password", "")

        if not identifier or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "login/login.html")

        # Allow login with either username or email
        user = None

        # Try username first
        user = authenticate(request, username=identifier, password=password)

        # If that failed, try looking up by email
        if user is None:
            try:
                matched = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=matched.username, password=password)
            except User.DoesNotExist:
                pass

        if user is None:
            messages.error(request, "Invalid username/email or password.")
            return render(request, "login/login.html")

        if not user.is_active:
            messages.error(request, "Please verify your email before logging in.")
            return render(request, "login/login.html")

        auth_login(request, user)
        return redirect("dashboard:index")

    return render(request, "login/login.html")


# ── Logout ─────────────────────────────────────────────────────────────────────

def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login:login")
