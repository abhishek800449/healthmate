from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, PatientProfileForm, MedicalRecordForm
from .models import User, PatientProfile, DoctorProfile, MedicalRecord
from appointment.models import Appointment
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from appointment.models import TimeSlot
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
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
            return redirect('/accounts/login')
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
            return redirect('/accounts/login')
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


# to edit patient profile
@login_required(login_url='login')
def patient_profile(request):
    patientprofile = get_object_or_404(PatientProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = PatientProfileForm(request.POST, request.FILES, instance=patientprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = PatientProfileForm(instance=patientprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'patientprofile': patientprofile,
    }
    return render(request, 'accounts/patient_profile.html', context)


@login_required(login_url='login')
@user_passes_test(is_doctor)
def doctor_dashboard(request):
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


@login_required
def delete_post(request):
    resp = {'status':'failed', 'msg':''}
    if request.method == 'POST':
        try:
            post = Post.objects.get(id = request.POST['id'])
            post.delete()
            resp['status'] = 'success'
            messages.success(request, 'Post has been deleted successfully')
        except:
           resp['msg'] = "Undefined Post ID"
    return HttpResponse(json.dumps(resp),content_type="application/json")


@login_required
def view_file(request, id):
    medical = get_object_or_404(MedicalRecord, id=id)
    print("inside view!!!!!!!!!!!!!!!!!!!")
    with open(medical.file_path.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        print("opened!!!!!!!!!!!!!!!!!!!")
    return response
    context ={  
        'medical': medical,
    }
    return render(request, 'medical/view_file.html', context)