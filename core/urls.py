from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('login/',      include('login.login.urls')),
    path('ev/',         include('ev_calculation.urls')),
]