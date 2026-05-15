from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',          views.home,     name='index'),
    path('vehicle/',  views.vehicle,  name='vehicle'),
    path('location/', views.location, name='location'),
    path('upgrade/',  views.upgrade,  name='upgrade'),
    path('profile/',  views.profile,  name='profile'),
]
