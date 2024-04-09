from django.shortcuts import render, redirect
from accounts.models import PatientProfile, User, DoctorProfile
from appointment.models import Appointment
from django.contrib.auth.decorators import login_required
from .models import RoomDetails
from orders.models import Order
# Create your views here.

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
        order = Order.objects.get(patient_profile=patient, doctor_profile__isnull=True, description='Online Appointment')
        order.doctor_profile= doctor
        order.appointment = appointment
        order.save()
        room.delete()
        return redirect("/consult/meeting?roomID=" + roomID)
    return render(request, 'videoapp/joinroom.html')