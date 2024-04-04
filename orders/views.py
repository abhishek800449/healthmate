from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import DoctorProfile, PatientProfile, Clinic, ReviewRating, Specialization
from appointment.models import PendingAppointment, TimeSlot, Appointment
from videoapp.models import RoomDetails
from .models import Order
from django.utils import timezone
from datetime import datetime

# Create your views here.

@login_required(login_url='login')
def checkout(request, doctor_slug=None):
    single_doctor = get_object_or_404(DoctorProfile, slug=doctor_slug)
    patientprofile = get_object_or_404(PatientProfile, user_id=request.user.id)
    clinic = Clinic.objects.get(doctor=single_doctor)
    reviews = ReviewRating.objects.filter(doctor=single_doctor)
    if request.method == 'POST':
        #user_form = UserForm(request.POST, instance=request.user)
        fee = single_doctor.price
        tax = 0.02*single_doctor.price
        total = tax+single_doctor.price
        selected_date = request.POST['selected_date']
        selected_timeslot = request.POST['selected_timeslot']
        # Get or create the PendingAppointment for the current user
        pending_appointment, created = PendingAppointment.objects.get_or_create(
            patient=patientprofile,
            defaults={
                'doctor': single_doctor,
                'date': selected_date,
                'time': selected_timeslot,
            }
        )
        # If the pending appointment already exists, update its details
        if not created:
            pending_appointment.doctor = single_doctor
            pending_appointment.date = selected_date
            pending_appointment.time = selected_timeslot
            pending_appointment.save()
        context = {
        'single_doctor': single_doctor,
        'selected_date': selected_date,
        'selected_timeslot': selected_timeslot,
        'clinic': clinic,
        'reviews': reviews,
        'tax': tax,
        'total': total,
        'fee': fee,
    }
    return  render(request, 'orders/checkout.html', context)


@login_required(login_url='login')
def booking_success(request):
    if request.method == 'POST':
        patientprofile = get_object_or_404(PatientProfile, user_id=request.user.id)
        pending_appointment = get_object_or_404(PendingAppointment, patient=patientprofile)
        appointment = Appointment(
            patient=patientprofile,
            doctor=pending_appointment.doctor,
            date=pending_appointment.date,
            time=pending_appointment.time,
            type='Offline'
        )
        appointment.save()
        pending_appointment.delete()
        appointment_date = appointment.date.strftime("%a")
        timeslot = TimeSlot.objects.get(doctor=appointment.doctor, day=appointment_date, start_time=appointment.time)
        timeslot.is_available = False
        timeslot.save()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        billing_address = request.POST.get('billing_address')
        payment_method = request.POST.get('payment_method')
        tax = float(request.POST.get('tax'))
        total_amount = float(request.POST.get('total_amount'))
        order = Order(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            billing_address=billing_address,
            payment_method=payment_method,
            doctor_profile=appointment.doctor,
            patient_profile=appointment.patient,
            tax=tax,
            total_amount=total_amount,
            description='Offline Appointment'
        )
        order.save()
        context={
            'appointment': appointment,
            'order':order,
        }
    return render(request, 'orders/booking_success.html', context)


@login_required(login_url='login')
def view_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    amount = order.total_amount-order.tax
    context = {
        'order': order,
        'amount': amount,
    }
    return  render(request, 'orders/invoice.html', context)


@login_required(login_url='login')
def book_consultation(request, specialization_slug=None):
    selected_date = datetime.now().date()
    selected_timeslot = datetime.now().time()
    fee = 500
    tax = 0.02*fee
    total = tax+fee
    specialization = Specialization.objects.get(slug=specialization_slug)
    context = {
        'specialization': specialization,
        'fee': fee,
        'tax': tax,
        'total': total,
        'selected_date': selected_date,
        'selected_timeslot': selected_timeslot,
    }
    return  render(request, 'orders/checkout.html', context)


@login_required(login_url='login')
def booking(request, specialization_slug=None):
    if request.method == 'POST':
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

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        billing_address = request.POST.get('billing_address')
        payment_method = request.POST.get('payment_method')
        tax = float(request.POST.get('tax'))
        total_amount = float(request.POST.get('total_amount'))
        order = Order(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            billing_address=billing_address,
            payment_method=payment_method,
            patient_profile=patient,
            tax=tax,
            total_amount=total_amount,
            description='Online Appointment'
        )
        order.save()
        return render(request, 'orders/booking_success.html')