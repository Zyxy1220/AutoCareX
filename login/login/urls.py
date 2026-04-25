from django.urls import path

from . import views

app_name = "login"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("verify/", views.verify_otp_view, name="verify"),
    path("logout/", views.logout_view, name="logout"),
]
