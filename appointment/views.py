from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Specialization, DoctorProfile, PatientProfile, Clinic, ClinicGallery, ReviewRating
from .models import TimeSlot
from .forms import ReviewForm
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib import messages
# Create your views here.

def doctors_list(request, specialization_slug=None):
    specialization = None
    doctors = None
    specialization_list = Specialization.objects.all()

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
        'specialization_list': specialization_list,
    }
    return render(request, 'appointments/doctors_list.html', context)


def filter_results(request):
    gender_type = request.GET.getlist('gender_type')
    select_specialist = request.GET.getlist('select_specialist')
    specialization_list = Specialization.objects.all()

    doctors = DoctorProfile.objects.all()
    if gender_type:
        doctors = doctors.filter(user__gender__in=gender_type)
    if select_specialist:
        doctors = doctors.filter(specialization__in=select_specialist)
    doctors_count = doctors.count()
    context = {
        'doctors': doctors,
        'doctors_count': doctors_count,
        'specialization_list': specialization_list,
        'last_gender_type': gender_type,
        'last_specialist': select_specialist,
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
    clinic = Clinic.objects.get(doctor=single_doctor)
    reviews = ReviewRating.objects.filter(doctor=single_doctor)
    timeslots = TimeSlot.objects.filter(doctor=single_doctor, is_available=True)
    today = datetime.now().date()
    date_list = [today + timedelta(days=x) for x in range(7)]
    context = {
        'single_doctor': single_doctor,
        'date_list': date_list,
        'timeslots': timeslots,
        'clinic': clinic,
        'reviews': reviews,
    }
    return  render(request, 'appointments/book_appointment.html', context)


def search(request):
    specialization_list = Specialization.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
             # Filter doctors based on name, specialization, city, and clinic name
            name_filter = Q(user__first_name__icontains=keyword) | Q(user__last_name__icontains=keyword)
            specialization_filter = Q(specialization__name__icontains=keyword)
            city_filter = Q(clinic__clinic_city__name__icontains=keyword)
            #clinic_name_filter = Q(clinic_name__icontains=keyword)
            # Combine all filters using OR operation
            combined_filter = name_filter | specialization_filter | city_filter #| clinic_name_filter
            # Filter DoctorProfile objects based on the combined filter
            doctors = DoctorProfile.objects.filter(combined_filter).distinct()
            doctors_count = doctors.count()
            
    context ={
        'doctors':doctors,
        'doctors_count': doctors_count,
        'specialization_list': specialization_list,
    }
    return render(request, 'appointments/doctors_list.html', context)


@login_required(login_url='login')
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