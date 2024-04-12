from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.contrib.auth.decorators import user_passes_test
from accounts.forms import RegistrationForm, UserForm, MedicalRecordForm
from accounts.models import User, PatientProfile, DoctorProfile, Specialization, ReviewRating, MedicalRecord
from django.http import JsonResponse
from django.utils.text import slugify
from orders.models import Order
from labs.models import LabTestBooking

# Create your views here.

def is_admin(user):
    return user.is_authenticated and user.is_admin


def adminapp_register(request):
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
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            # Now activating user's account
            user.is_active = True
            user.is_admin = True
            user.profile_picture = 'userprofile/Admin_Profile.png'
            user.save()
            messages.success(request, 'Your account has been created successfully.')
            return redirect('adminapp_login')
        else:
            messages.error(request, 'Invalid data.')
            return redirect('adminapp_register')
    else:       
        form = RegistrationForm()
    context = {
        'form':form,
    }
    return render(request, 'adminapp/register.html', context)


@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def index(request):
    return render(request, 'adminapp/index.html')


def adminapp_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None and user.is_admin:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('/adminapp')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('adminapp_login')
    return render(request, 'adminapp/login.html')


@login_required(login_url='adminapp_login')
def adminapp_logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('adminapp_login')


@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('adminapp_profile')
        else:
            messages.error(request, 'Please enter valid data in the form!!')
            return redirect('adminapp_profile')
    else:
        user_form = UserForm(instance=request.user)
    context = {
        'user_form': user_form,
    }  
    return render(request, 'adminapp/profile.html', context)


@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_change_password(request):
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
                    return redirect('adminapp_change_password')
                    '''
                user.set_password(new_password)
                user.save()
                
                updated_user = auth.authenticate(email=user.email, password=new_password)
                if updated_user is not None:
                    auth.login(request, updated_user)  # Keep the user logged in
                    messages.success(request, 'Password updated successfully.')
                    return redirect('adminapp_profile')
                else:
                    messages.error(request, 'Failed to re-authenticate after password change.')

                messages.success(request, 'Password updated successfully.')
                return redirect('adminapp_profile')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('adminapp_profile')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('adminapp_profile')
        

@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_doctor_list(request):
    doctors = DoctorProfile.objects.all()
    context = {
        'doctors': doctors,
    }
    return render(request, 'adminapp/doctor-list.html', context)


@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_patient_list(request):
    patients = PatientProfile.objects.all()
    context = {
        'patients': patients,
    }
    return render(request, 'adminapp/patient-list.html', context)


def change_status(request):
    doc_id = request.GET.get('doctor_id')
    status = request.GET.get('is_active')
    try:
        doctor = User.objects.get(id=doc_id)
        if doctor:
            if status=='true':
                doctor.is_active = True
            elif status=='false':
                doctor.is_active = False
            doctor.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Doctor not found'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Doctor not found'})
    

@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_specialities(request):
    if request.method == 'POST':
        name = request.POST['specialization']
        image = request.FILES['image']
        slug = slugify(name)
        try:
            specialization = Specialization(
                name=name,
                slug=slug,
                image=image,                
            )
            specialization.save()
            messages.success(request, 'Specialization saved successfully.')
        except Exception as e:
            messages.error(request, f'Error saving specialization: {e}')
    specializations = Specialization.objects.all()
    context = {
        'specializations': specializations,
    }
    return render(request, 'adminapp/specialities.html', context)


def delete_specialization(request):
    if request.method == 'POST':
        spz_id = request.POST['specialization_id']
        try:
            specialization = Specialization.objects.get(id=spz_id)
            specialization.delete()
            messages.success(request, 'Specialization deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting specialization: {e}')
        return redirect('adminapp_specialities')


@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def edit_specialization(request):
    if request.method == 'POST':
        spz_id = request.POST['specialization_id']
        name = None
        image = None
        if 'specialization' in request.POST:
            name = request.POST['specialization']
        if 'image' in request.FILES:
            image = request.FILES['image']

        try:
            specialization = Specialization.objects.get(id=spz_id)
            if name:
                specialization.name = name
            if image:
                specialization.image = image
            specialization.save()
            messages.success(request, 'Specialization updated successfully.')
        except Exception as e:
            messages.error(request, f'Error editing specialization: {e}')
        return redirect('adminapp_specialities')
    

@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_reviews(request):
    reviews = ReviewRating.objects.all().order_by('-updated_at')
    context = {
        'reviews': reviews,
    }
    return render(request, 'adminapp/reviews.html', context)


def delete_review(request):
    if request.method == 'POST':
        r_id = request.POST['review_id']
        try:
            review = ReviewRating.objects.get(id=r_id)
            review.delete()
            messages.success(request, 'Review deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting review: {e}')
        return redirect('adminapp_reviews')
    

@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_transactions(request):
    orders = Order.objects.all()
    context = {
        'orders': orders,
    }
    return render(request, 'adminapp/transactions.html', context)


def delete_order(request):
    if request.method == 'POST':
        o_id = request.POST['order_id']
        try:
            order = Order.objects.get(id=o_id)
            order.delete()
            messages.success(request, 'Transaction deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting transaction: {e}')
        return redirect('adminapp_transactions')
    

@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def adminapp_lab_appointments(request):
    bookings = LabTestBooking.objects.all().order_by('appointment_date', 'appointment_time', 'booking_date')
    context = {
        'bookings': bookings,
    }
    return render(request, 'adminapp/lab_appointments.html', context)


@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def edit_lab_appointments(request, id):
    try:
        booking = LabTestBooking.objects.get(id=id)        
        if request.method == 'POST':
            status = None
            remarks = None
            if 'status' in request.POST:
                status = request.POST['status']
            if 'remarks' in request.POST:
                remarks = request.POST['remarks']
            try:
                if status:
                    booking.status = status
                if remarks:
                    booking.remarks = remarks
                booking.save()
                messages.success(request, 'Status updated successfully.')
            except Exception as e:
                messages.error(request, f'Error updating status: {e}')

        form = MedicalRecordForm()
        context = {
        'booking': booking,
        'form': form,
        }
        return render(request, 'adminapp/edit_appointments.html', context)
    except Exception as e:
        messages.error(request, f'Error in loading appointment details.{e}')
        return redirect('adminapp_lab_appointments')
    

@login_required(login_url='adminapp_login')
@user_passes_test(is_admin)
def add_lab_results(request, id):        
    if request.method == 'POST':
        try:
            booking = LabTestBooking.objects.get(id=id)
            patient = booking.patient
            form = MedicalRecordForm(request.POST, request.FILES)
            if form.is_valid():                
                medical_record = MedicalRecord(
                patient=patient,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                file_path=form.cleaned_data['file_path'],
                created_by=None
            )
                medical_record.save()
                messages.success(request, 'Lab result saved successfully.')
                return redirect('edit_lab_appointments', id)
            else:
                messages.error(request, 'Invalid form data. Please check the fields.')
                return redirect('edit_lab_appointments', id)
        except Exception as e:
            messages.error(request, f'Error in uploading results.{e}')
            return redirect('edit_lab_appointments', id)                   
    else:
        messages.error(request, 'Invalid request.')
        return redirect('adminapp_lab_appointments')