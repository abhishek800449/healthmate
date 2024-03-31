from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, PatientProfileForm, DoctorProfileForm, MedicalRecordForm, ClinicForm, ClinicGalleryForm
from .models import User, PatientProfile, DoctorProfile, MedicalRecord, Country, State, City, ClinicGallery, Clinic, ReviewRating, Prescription, PrescriptionItem
from appointment.models import Appointment
from videoapp.models import RoomDetails
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from appointment.models import TimeSlot
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, JsonResponse
from datetime import date
import re

# Create your views here.

def patient_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            # creating user account
            user = User.objects.create_patient(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            # Now activating user's account
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been created successfully.')
            return redirect('/accounts/login')
        else:
            messages.error(request, 'Invalid data.')
            return redirect('/accounts/patient_register')
    else:       
        form = RegistrationForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/patient_register.html', context)


def doctor_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            # creating user account
            user = User.objects.create_doctor(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            # Now activating user's account
            user.is_active = True
            user.is_staff = True
            user.save()
            messages.success(request, 'Your account has been created successfully.')
            return redirect('/accounts/login')
        else:
            messages.error(request, 'Invalid data.')
            return redirect('/accounts/doctor_register')
    else:       
        form = RegistrationForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/doctor_register.html', context)


def is_doctor(user):
    return user.is_authenticated and user.is_staff


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            if user.is_staff:
                return redirect('/accounts/doctor_dashboard')
            else:
                return redirect('/accounts/patient_dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('/accounts/login')


@login_required(login_url='login')
def patient_dashboard(request):
    patientprofile = PatientProfile.objects.get(user_id=request.user.id)
    form = MedicalRecordForm()
    medicals = MedicalRecord.objects.filter(patient=patientprofile)
    try:
        appointments = Appointment.objects.filter(patient=patientprofile)       
    except (Appointment.DoesNotExist):
        appointments = None
    context = {
        'patientprofile': patientprofile,
        'appointments': appointments,
        'medicals': medicals,
        'form': form,
    }
    return render(request, 'accounts/patient_dashboard.html', context)


@login_required(login_url='login')
def my_appointments(request):
    patientprofile = PatientProfile.objects.get(user_id=request.user.id)
    try:
        appointments = Appointment.objects.filter(patient=patientprofile)       
    except (Appointment.DoesNotExist):
        appointments = None
    context = {
        'patientprofile': patientprofile,
        'appointments': appointments,
    }
    return render(request, 'accounts/my_appointments.html', context)


# to edit patient profile
@login_required(login_url='login')
def patient_profile(request):
    patientprofile = get_object_or_404(PatientProfile, user=request.user)
    countries = Country.objects.all()
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = PatientProfileForm(request.POST, instance=patientprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('patient_profile')
        else:
            messages.error(request, 'Please enter valid data in the form!!')
            return redirect('patient_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = PatientProfileForm(instance=patientprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'patientprofile': patientprofile,
        'countries': countries,
    }
    return render(request, 'accounts/patient_profile.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def doctor_profile(request):
    if request.method == 'POST':
        doctorprofile = DoctorProfile.objects.get(user=request.user)
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        doctor_profile_form = DoctorProfileForm(request.POST, instance=doctorprofile)
        clinic_form = ClinicForm(request.POST)
        gallery = ClinicGalleryForm(request.POST, request.FILES)
        if user_form.is_valid() and doctor_profile_form.is_valid() and clinic_form.is_valid():
            user_instance = user_form.save()
            
            doctor_profile_instance = doctor_profile_form.save(commit=False)
            doctor_profile_instance.user = user_instance
            doctor_profile_instance.save()

            clinic_instance = clinic_form.save(commit=False)
            clinic_instance.doctor = doctor_profile_instance
            clinic_instance.save()
            
            images = request.FILES.getlist('images')
            for image in images:
                ClinicGallery.objects.create(clinic=clinic_instance, images=image)

            messages.success(request, 'Your profile has been updated.')
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Please enter valid data in the form!!')
            return redirect('doctor_profile')

    clinic_form = ClinicForm()
    gallery = ClinicGalleryForm()
    doctor_profile_form = DoctorProfileForm()
    user_form = UserForm(instance=request.user)
    context = {
        'clinic_form': clinic_form,
        'gallery': gallery,
        'doctor_profile_form': doctor_profile_form,
        'user_form': user_form,
    }
    return render(request, 'accounts/doctor_profile.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def doctor_profile_settings(request):
    doctorprofile = DoctorProfile.objects.get(user=request.user)
    clinic = Clinic.objects.get(doctor=doctorprofile)
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        doctor_profile_form = DoctorProfileForm(request.POST, instance=doctorprofile)
        clinic_form = ClinicForm(request.POST, instance=clinic)
        gallery = ClinicGalleryForm(request.POST, request.FILES)
        if user_form.is_valid() and doctor_profile_form.is_valid() and clinic_form.is_valid():
            user_instance = user_form.save()
            
            doctor_profile_instance = doctor_profile_form.save(commit=False)
            doctor_profile_instance.user = user_instance
            doctor_profile_instance.save()

            clinic_instance = clinic_form.save(commit=False)
            clinic_instance.doctor = doctor_profile_instance
            clinic_instance.save()
            
            images = request.FILES.getlist('images')
            for image in images:
                ClinicGallery.objects.create(clinic=clinic_instance, images=image)

            messages.success(request, 'Your profile has been updated.')
            return redirect('doctor_profile_settings')
        
        else:
            messages.error(request, 'Please enter valid data in the form!!')
            return redirect('doctor_profile_settings')
    else:
        clinic_form = ClinicForm(instance=clinic)
        gallery = ClinicGalleryForm()
        doctor_profile_form = DoctorProfileForm(instance=doctorprofile)
        user_form = UserForm(instance=request.user)
    context = {
        'clinic_form': clinic_form,
        'gallery': gallery,
        'doctor_profile_form': doctor_profile_form,
        'user_form': user_form,
    }
    return render(request, 'accounts/doctor_profile_settings.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    doctorprofile = DoctorProfile.objects.get(user_id=request.user.id)
    if doctorprofile.registration_number is None:
        return redirect('doctor_profile')
    try:
        appointments = Appointment.objects.filter(doctor=doctorprofile).order_by('date', 'time')
    except Appointment.DoesNotExist:
        appointments = None
    context = {
        'doctorprofile': doctorprofile,
        'appointments': appointments,
    }
    return render(request, 'accounts/doctor_dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def schedule_time(request):
    doctorprofile = get_object_or_404(DoctorProfile, user=request.user)
    timeslots = TimeSlot.objects.filter(doctor=doctorprofile)
    if request.method == 'POST':
        #user_form = UserForm(request.POST, instance=request.user)
        selected_day = request.POST['selected_day']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        time_slot = TimeSlot(
                doctor=doctorprofile,
                day=selected_day,
                start_time=start_time,
                end_time=end_time,
            )
        time_slot.save()
        messages.success(request, 'New schedule has been added.')
        return redirect('schedule_time')
    
    context = {
        'doctorprofile': doctorprofile,
        'timeslots': timeslots,
        'days_of_week': TimeSlot.DAYS_OF_WEEK,
    }
    return render(request, 'accounts/schedule_time.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def delete_timeslot(request, timeslot_id):
    doctorprofile = get_object_or_404(DoctorProfile, user=request.user)
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id, doctor=doctorprofile)
    if request.method == 'POST':
        timeslot.delete()
        messages.success(request, 'Billing Address has been deleted.')
    return redirect('schedule_time')


@login_required(login_url='login')
@user_passes_test(is_doctor)
def view_appointments(request):
    doctorprofile = DoctorProfile.objects.get(user_id=request.user.id)
    today = timezone.now().date()
    try:
        appointments = Appointment.objects.filter(doctor=doctorprofile).order_by('date', 'time')
        todays_appointments = appointments.filter(date=today)
    except Appointment.DoesNotExist:
        appointments = None
        todays_appointments = None
    context = {
        'doctorprofile': doctorprofile,
        'appointments': appointments,
        'todays_appointments': todays_appointments,
    }
    return render(request, 'accounts/view_appointments.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def view_patient(request, patient_username=None):
    patient = User.objects.get(username=patient_username)
    patientprofile = PatientProfile.objects.get(user=patient)
    doctorprofile = DoctorProfile.objects.get(user_id=request.user.id)
    medicals = MedicalRecord.objects.filter(patient=patientprofile)
    form = MedicalRecordForm()
    try:
        appointments = Appointment.objects.filter(patient=patientprofile, doctor=doctorprofile).order_by('date', 'time')
    except Appointment.DoesNotExist:
        appointments = None
    context = {
        'patientprofile': patientprofile,
        'appointments': appointments,
        'form': form,
        'medicals': medicals,
    }
    return render(request, 'accounts/view_patient.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = User.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                '''
                if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', new_password):
                    messages.error(request, "Password should be at least 8 characters and contain a combination of uppercase, lowercase, digits, and special symbols!")
                    return redirect('change_password')
                    '''
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def change_doctor_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = User.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                '''
                if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', new_password):
                    messages.error(request, "Password should be at least 8 characters and contain a combination of uppercase, lowercase, digits, and special symbols!")
                    return redirect('change_doctor_password')
                    '''
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_doctor_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_doctor_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_doctor_password')
    return render(request, 'accounts/change_doctor_password.html')


@login_required
def save_record(request):
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid():
            patient_id = request.POST['patient_id']
            patient = PatientProfile.objects.get(id=patient_id)
            if user.is_staff:
                creator = DoctorProfile.objects.get(user=user)
            else:
                creator = None
            medical_record = MedicalRecord(
                patient=patient,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                file_path=form.cleaned_data['file_path'],
                created_by=creator
            )
            medical_record.save()
            messages.success(request, 'Medical record saved successfully.')
            if user.is_staff:
                return redirect('view_patient', patient_username=patient.user.username)
            else:
                return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid form data. Please check the fields.')
            if user.is_staff:
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        return redirect('patient_dashboard')


@login_required(login_url='login')
def delete_record(request, medical_id):
    user = request.user
    medical = get_object_or_404(MedicalRecord, id=medical_id)
    patient = medical.patient
    if request.method == 'POST':
        medical.delete()
        messages.success(request, 'Medical record has been deleted.')
    if is_doctor(user):
        return redirect('view_patient', patient_username=patient.user.username)
    return redirect('patient_dashboard')


@login_required
def view_file(request, id):
    medical = get_object_or_404(MedicalRecord, id=id)
    with open(medical.file_path.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
    return response

def get_states(request):
    country_id = request.GET.get('country_id')
    if country_id:
        states = State.objects.filter(country_id=country_id)
        state_list = [{'id': state.id, 'name': state.name} for state in states]
        return JsonResponse({'states': state_list})
    return JsonResponse({'error': 'Invalid country ID'})

def get_cities(request):
    state_id = request.GET.get('state_id')
    if state_id:
        cities = City.objects.filter(state_id=state_id)
        city_list = [{'id': city.id, 'name': city.name} for city in cities]
        return JsonResponse({'cities': city_list})
    return JsonResponse({'error': 'Invalid state ID'})


@login_required(login_url='login')
@user_passes_test(is_doctor)
def accept(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, 'Appointment accepted.')
    return redirect('doctor_dashboard')

@login_required(login_url='login')
@user_passes_test(is_doctor)
def cancel(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
    return redirect('doctor_dashboard')


@login_required(login_url='login')
@user_passes_test(is_doctor)
def view_rooms(request):
    doctorprofile = DoctorProfile.objects.get(user_id=request.user.id)
    rooms = RoomDetails.objects.filter(specialization=doctorprofile.specialization)
    context = {
        'doctorprofile': doctorprofile,
        'rooms': rooms,
    }
    return render(request, 'accounts/view_rooms.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def reviews(request):
    doctorprofile = DoctorProfile.objects.get(user_id=request.user.id)
    reviews = ReviewRating.objects.filter(doctor=doctorprofile)
    context = {
        'doctorprofile': doctorprofile,
        'reviews': reviews,
    }
    return render(request, 'accounts/reviews.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def add_prescription(request, patient_username=None):  
    patient = User.objects.get(username=patient_username)
    patientprofile = PatientProfile.objects.get(user=patient)
    doctor = DoctorProfile.objects.get(user_id=request.user.id)
    clinic = Clinic.objects.get(doctor=doctor)
    today = date.today()
    if request.method == 'POST':
        prescription_items = request.POST.getlist('item_name')
        quantities = request.POST.getlist('quantity')
        days = request.POST.getlist('days')
        mornings = request.POST.getlist('morning')
        afternoons = request.POST.getlist('afternoon')
        evenings = request.POST.getlist('evening')
        nights = request.POST.getlist('night')
        sign = request.FILES.get('signature_image')
        prescription = Prescription(
            doctor=doctor,
            patient=patientprofile,
            signature=sign,
        )
        prescription.save()
        print(prescription_items)
        print(quantities)
        print(days)
        print(mornings)
        print(afternoons)
        print(evenings)
        print(nights)
        print(request.POST.get('description'))
        for item, quantity, day, m, a, e, n in zip(prescription_items, quantities, days, mornings, afternoons, evenings, nights):
            print(item, quantity, day, m, a, e, n)
            PrescriptionItem.objects.create(
                prescription=prescription,
                name=item,
                quantity=quantity,
                days=day,
                morning=m,
                afternoon=a,
                evening=e,
                night=n,
            )
    context = {
        'patientprofile': patientprofile,
        'doctor': doctor,
        'clinic': clinic,
        'today': today,
    }
    return render(request, 'medical/add_prescription.html', context)