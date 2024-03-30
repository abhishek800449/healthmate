from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Specialization, DoctorProfile, PatientProfile, Clinic, ClinicGallery, ReviewRating
from .models import TimeSlot, PendingAppointment, Appointment
from .forms import ReviewForm
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib import messages
# Create your views here.

def doctors_list(request, specialization_slug=None):
    specialization = None
    doctors = None

    if specialization_slug != None:
        specialization = get_object_or_404(Specialization, slug=specialization_slug)
        doctors = DoctorProfile.objects.filter(specialization=specialization)
        doctors_count = doctors.count()
    else:
        doctors = DoctorProfile.objects.all()
        doctors_count = doctors.count()
        
    context ={
        'doctors':doctors,
        'doctors_count': doctors_count,
    }
    return render(request, 'appointments/doctors_list.html', context)


def view_doctor(request,specialization_slug=None, doctor_slug=None):
    single_doctor = DoctorProfile.objects.get(specialization__slug=specialization_slug, slug=doctor_slug)
    clinic = Clinic.objects.get(doctor=single_doctor)
    clinic_images = ClinicGallery.objects.filter(clinic = clinic)
    reviews = ReviewRating.objects.filter(doctor=single_doctor)
    context = {
        'single_doctor': single_doctor,
        'clinic': clinic,
        'clinic_images': clinic_images,
        'reviews': reviews,
    }
    return  render(request, 'appointments/view_doctor.html', context)


@login_required(login_url='login')
def book_appointment(request,specialization_slug=None, doctor_slug=None):
    single_doctor = DoctorProfile.objects.get(specialization__slug=specialization_slug, slug=doctor_slug)
    timeslots = TimeSlot.objects.filter(doctor=single_doctor, is_available=True)
    today = datetime.now().date()
    date_list = [today + timedelta(days=x) for x in range(7)]
    context = {
        'single_doctor': single_doctor,
        'date_list': date_list,
        'timeslots': timeslots,
    }
    return  render(request, 'appointments/book_appointment.html', context)


@login_required(login_url='login')
def checkout(request, doctor_slug=None):
    single_doctor = get_object_or_404(DoctorProfile, slug=doctor_slug)
    patientprofile = get_object_or_404(PatientProfile, user_id=request.user.id)
    if request.method == 'POST':
        #user_form = UserForm(request.POST, instance=request.user)
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
    }
    return  render(request, 'appointments/checkout.html', context)


@login_required(login_url='login')
def booking_success(request):
    patientprofile = get_object_or_404(PatientProfile, user_id=request.user.id)
    pending_appointment = get_object_or_404(PendingAppointment, patient=patientprofile)
    appointment = Appointment(
        patient=patientprofile,
        doctor=pending_appointment.doctor,
        date=pending_appointment.date,
        time=pending_appointment.time
    )
    appointment.save()
    pending_appointment.delete()
    appointment_date = appointment.date.strftime("%a")
    timeslot = TimeSlot.objects.get(doctor=appointment.doctor, day=appointment_date, start_time=appointment.time)
    timeslot.is_available = False
    timeslot.save()
    context={
        'appointment': appointment,
    }
    return render(request, 'appointments/booking_success.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
             # Filter doctors based on name, specialization, city, and clinic name
            name_filter = Q(user__first_name__icontains=keyword) | Q(user__last_name__icontains=keyword)
            specialization_filter = Q(specialization__name__icontains=keyword)
            city_filter = Q(user__city__name__icontains=keyword)
            #clinic_name_filter = Q(clinic_name__icontains=keyword)
            # Combine all filters using OR operation
            combined_filter = name_filter | specialization_filter | city_filter #| clinic_name_filter
            # Filter DoctorProfile objects based on the combined filter
            doctors = DoctorProfile.objects.filter(combined_filter).distinct()
            doctors_count = doctors.count()
            
    context ={
        'doctors':doctors,
        'doctors_count': doctors_count,
    }
    return render(request, 'appointments/doctors_list.html', context)


def submit_review(request, doctor_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        patient = PatientProfile.objects.get(user=request.user)
        try:
            # if review already exists then we update the existing review.
            reviews = ReviewRating.objects.get(patient__id=patient.id, doctor__id=doctor_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.title = form.cleaned_data['title']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.doctor_id = doctor_id
                data.patient_id = patient.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)