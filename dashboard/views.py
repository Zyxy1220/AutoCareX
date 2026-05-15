from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404

from ev_data.models import Vehicle


def home(request):
    return render(request, 'Home.html')


@login_required(login_url='/login/')
def vehicle(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_car':
            nickname = request.POST.get('nickname', '').strip()
            year     = request.POST.get('year', 2024)
            mileage  = request.POST.get('mileage', 0)
            model    = request.POST.get('model', 'EMAS 5')

            if not nickname:
                messages.error(request, 'Car nickname is required.')
            else:
                Vehicle.objects.create(
                    owner=request.user,
                    nickname=nickname,
                    year=int(year),
                    mileage=int(mileage),
                    model=model,
                )
                messages.success(request, f'"{nickname}" added to your garage.')

        elif action == 'delete_car':
            car_id = request.POST.get('car_id')
            car = get_object_or_404(Vehicle, id=car_id, owner=request.user)
            car.delete()
            messages.success(request, 'Car removed from your garage.')

        elif action == 'update_mileage':
            car_id          = request.POST.get('car_id')
            new_mileage     = request.POST.get('mileage', 0)
            new_battery     = request.POST.get('battery_percent', 100)
            car = get_object_or_404(Vehicle, id=car_id, owner=request.user)
            car.mileage         = max(int(new_mileage), car.mileage)
            car.battery_percent = min(max(int(new_battery), 0), 100)
            car.save()
            messages.success(request, 'Vehicle updated.')

        elif action == 'update_component':
            car_id = request.POST.get('car_id')
            car = get_object_or_404(Vehicle, id=car_id, owner=request.user)
            messages.success(request, 'Component status noted.')

        return redirect('dashboard:vehicle')

    cars = Vehicle.objects.filter(owner=request.user)
    selected_id = request.GET.get('car')
    selected_car = None

    if selected_id:
        selected_car = cars.filter(id=selected_id).first()

    if not selected_car and cars.exists():
        selected_car = cars.first()

    return render(request, 'vehicle.html', {
        'cars': cars,
        'car_count': cars.count(),
        'selected_car': selected_car,
    })


@login_required(login_url='/login/')
def location(request):
    return render(request, 'location.html')


@login_required(login_url='/login/')
def upgrade(request):
    return render(request, 'upgrade.html')


@login_required(login_url='/login/')
def profile(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_info':
            new_username = request.POST.get('username', '').strip()
            new_email    = request.POST.get('email', '').strip().lower()

            if new_username and new_username != request.user.username:
                if User.objects.filter(username__iexact=new_username).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'That username is already taken.')
                else:
                    request.user.username = new_username
                    request.user.save()
                    messages.success(request, 'Username updated.')

            if new_email and new_email != request.user.email:
                if User.objects.filter(email__iexact=new_email).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'That email is already in use.')
                else:
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, 'Email updated.')

        elif action == 'change_password':
            current = request.POST.get('current_password', '')
            new_pw  = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')

            if not request.user.check_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif len(new_pw) < 8:
                messages.error(request, 'New password must be at least 8 characters.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')

        return redirect('dashboard:profile')

    return render(request, 'profile.html')
