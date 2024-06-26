from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, PatientProfileForm, DoctorProfileForm, MedicalRecordForm, ClinicForm, ClinicGalleryForm
from .models import User, PatientProfile, DoctorProfile, MedicalRecord, Country, State, City, ClinicGallery, Clinic, ReviewRating, Prescription, PrescriptionItem
from appointment.models import Appointment
from orders.models import Order
from videoapp.models import RoomDetails
from labs.models import LabTestBooking
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from appointment.models import TimeSlot
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, JsonResponse
from datetime import date
from django.db.models import Case, When, Value
from django.db import models
# importing files for verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

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
    medicals = MedicalRecord.objects.filter(patient=patientprofile).order_by('-date_created')
    prescriptions = Prescription.objects.filter(patient=patientprofile).order_by('-date_created')
    orders = Order.objects.filter(patient_profile=patientprofile).order_by('-issue_date')
    try:
        appointments = Appointment.objects.filter(patient=patientprofile)       
    except (Appointment.DoesNotExist):
        appointments = None
    context = {
        'patientprofile': patientprofile,
        'appointments': appointments,
        'medicals': medicals,
        'form': form,
        'prescriptions': prescriptions,
        'orders': orders,
    }
    return render(request, 'accounts/patient_dashboard.html', context)


@login_required(login_url='login')
def my_appointments(request):
    patientprofile = PatientProfile.objects.get(user_id=request.user.id)

    status_order = Case(
        When(status='confirmed', then=Value(1)),
        When(status='pending', then=Value(2)),
        When(status='cancelled', then=Value(3)),
        When(status='complete', then=Value(4)),
        default=Value(5),  # Fallback for any other status
        output_field=models.IntegerField()
    )
    
    try:
        appointments = Appointment.objects.filter(patient=patientprofile).order_by('date', 'time', status_order)    
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
        'doctorprofile': doctorprofile,
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
        today = date.today()
        for appointment in appointments:
            if appointment.status == 'pending' and appointment.date<today:
                appointment.status = 'cancelled'
            elif appointment.status == 'confirmed' and appointment.date<today:
                appointment.status = 'complete'
            appointment.save()
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
    medicals = MedicalRecord.objects.filter(patient=patientprofile).order_by('-date_created')
    prescriptions = Prescription.objects.filter(patient=patientprofile)
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
        'prescriptions': prescriptions,
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

                updated_user = auth.authenticate(email=user.email, password=new_password)
                if updated_user is not None:
                    auth.login(request, updated_user)  # Keep the user logged in
                    messages.success(request, 'Password updated successfully.')
                    return redirect('change_password')
                else:
                    messages.error(request, 'Failed to re-authenticate after password change.')
                
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
    doctorprofile = DoctorProfile.objects.get(user=request.user)
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

                updated_user = auth.authenticate(email=user.email, password=new_password)
                if updated_user is not None:
                    auth.login(request, updated_user)  # Keep the user logged in
                    messages.success(request, 'Password updated successfully.')
                    return redirect('change_doctor_password')
                else:
                    messages.error(request, 'Failed to re-authenticate after password change.')

                messages.success(request, 'Password updated successfully.')
                return redirect('change_doctor_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_doctor_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_doctor_password')
    context = {
        'doctorprofile': doctorprofile,
    }
    return render(request, 'accounts/change_doctor_password.html', context)


@login_required
def save_record(request):
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        user = request.user 
        if form.is_valid():
            patient_id = request.POST['patient_id']
            patient = PatientProfile.objects.get(id=patient_id)
            creator = user

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
        description = request.POST.get('description')
        prescription = Prescription(
            doctor=doctor,
            patient=patientprofile,
            signature=sign,
            description=description,
        )
        prescription.save()
        for item, quantity, day, m, a, e, n in zip(prescription_items, quantities, days, mornings, afternoons, evenings, nights):
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
        messages.success(request, 'Prescription saved successfully.')
    context = {
        'patientprofile': patientprofile,
        'doctor': doctor,
        'clinic': clinic,
        'today': today,
    }
    return render(request, 'medical/add_prescription.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def delete_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    patient = prescription.patient
    if request.method == 'POST':
        prescription.delete()
        messages.success(request, 'Prescription has been deleted.')
    return redirect('view_patient', patient_username=patient.user.username)


@login_required(login_url='login')
def view_prescription(request, id):
    prescription = Prescription.objects.get(id=id)
    prescription_items = PrescriptionItem.objects.filter(prescription=prescription)
    clinic = Clinic.objects.get(doctor=prescription.doctor)
    context = {
        'prescription': prescription,
        'prescription_items': prescription_items,
        'clinic': clinic,
    }
    return render(request, 'medical/view_prescription.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def invoices(request):
    doctorprofile = DoctorProfile.objects.get(user_id=request.user.id)
    orders = Order.objects.filter(doctor_profile=doctorprofile).order_by('issue_date')
    context = {
        'doctorprofile': doctorprofile,
        'orders': orders,
    }
    return render(request, 'accounts/invoices.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def my_patients(request):
    doctorprofile = DoctorProfile.objects.get(user_id=request.user.id)
    patients = PatientProfile.objects.filter(appointment__doctor=doctorprofile).distinct()
    context = {
        'doctorprofile': doctorprofile,
        'patients': patients,
    }
    return render(request, 'accounts/my_patients.html', context)


@login_required(login_url='login')
def view_labs(request):
    patient = PatientProfile.objects.get(user=request.user)
    labs = LabTestBooking.objects.filter(patient=patient)
    context = {
        'labs': labs,
    }
    return render(request, 'labs/my_labs.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            # sending reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), # we are encoding the primary key of user
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email,])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exists')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request, 'Please reset your password.')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Invalid Link')
        return redirect('login')
    

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password==confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password) # this is build in function in django normal save() does not work for paswords.
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match.')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')