from django.db import models
from django.contrib.auth.models import User

#if login only when user login is settle, otherwise just use if not login to test

if login:
    class Vehicle(models.Model):
        owner = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name="vehicles"
        )
        name = models.CharField(max_length=100)
        make = models.CharField(max_length=100)
        model = models.CharField(max_length=100)
        year = models.PositiveIntegerField()
        plate_number = models.CharField(max_length=20, unique=True)
        current_mileage = models.PositiveIntegerField(default=0)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.name} - {self.plate_number}"
        
if not login:
    class Vehicle(models.Model):
        name = models.CharField(max_length=100)
        make = models.CharField(max_length=100)
        model = models.CharField(max_length=100)
        year = models.PositiveIntegerField()
        plate_number = models.CharField(max_length=20, unique=True)
        current_mileage = models.PositiveIntegerField(default=0)

        def __str__(self):
            return f"{self.name} - {self.plate_number}"