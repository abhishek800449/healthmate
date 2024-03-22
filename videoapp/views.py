from django.shortcuts import render, redirect
from datetime import datetime
from accounts.models import Specialization, PatientProfile, User, DoctorProfile
from appointment.models import Appointment
from django.contrib.auth.decorators import login_required
from .models import RoomDetails
from django.utils import timezone

# Create your views here.

def book_consultation(request, specialization_slug=None):
    today = datetime.now().date()
    time = datetime.now().time()
    specialization = Specialization.objects.get(slug=specialization_slug)
    context = {
        'today': today,
        'time': time,
        'specialization': specialization,
    }
    return  render(request, 'videoapp/checkout.html', context)


@login_required(login_url='login')
def booking(request, specialization_slug=None):
    specialization = Specialization.objects.get(slug=specialization_slug)
    patient = PatientProfile.objects.get(user=request.user)
    room, created = RoomDetails.objects.get_or_create(
        patient=patient,
        specialization=specialization,
        defaults={'date': timezone.now().date(), 'time': timezone.now().time()}
    )
    if not created:
        room.date = timezone.now().date()
        room.time = timezone.now().time()
        room.save()
    return render(request, 'videoapp/booking.html')


@login_required
def videocall(request):
    user = request.user
    name = user.first_name + " " + user.last_name
    context = {
        'name': name,
        'user': user,
    }
    return render(request, 'videoapp/videocall.html', context)


@login_required
def join_room(request):
    if request.method == 'POST':
        roomID = request.POST['roomID']
        user = User.objects.get(username=roomID)
        patient = PatientProfile.objects.get(user=user)
        room = RoomDetails.objects.get(patient=patient)
        doctor = DoctorProfile.objects.get(user=request.user)
        appointment = Appointment(
            patient=patient,
            doctor=doctor,
            date=room.date,
            time=room.time,
            status='complete',
            type='online'
        )
        appointment.save()
        room.delete()
        return redirect("/consult/meeting?roomID=" + roomID)
    return render(request, 'videoapp/joinroom.html')