from itertools import chain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from fuel.services import calculate_fuel_stats
from maintenance.services import get_schedule_status
from notifications.models import Notification
from vehicles.utils import get_accessible_vehicles


@login_required
def home_view(request):
    vehicles = get_accessible_vehicles(request.user)
    alerts = []
    for vehicle in vehicles:
        for schedule in vehicle.schedules.filter(is_active=True):
            status = get_schedule_status(schedule, vehicle.current_odometer)
            if status != 'green':
                alerts.append({'vehicle': vehicle, 'schedule': schedule, 'status': status})

    activity = sorted(
        chain(
            *[vehicle.maintenance_logs.all()[:5] for vehicle in vehicles],
            *[vehicle.fuel_logs.all()[:5] for vehicle in vehicles],
        ),
        key=lambda item: getattr(item, 'timestamp', None) or getattr(item, 'date', None),
        reverse=True,
    )[:10]

    summary = None
    first_vehicle = vehicles.first()
    if first_vehicle:
        summary = calculate_fuel_stats(first_vehicle)

    notifications = Notification.objects.filter(user=request.user).order_by('-sent_at')[:10]
    return render(request, 'dashboard/home.html', {
        'vehicles': vehicles,
        'alerts': alerts,
        'activity': activity,
        'summary': summary,
        'notifications': notifications,
    })
