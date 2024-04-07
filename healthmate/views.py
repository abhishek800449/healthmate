from django.shortcuts import render
from accounts.models import Specialization, DoctorProfile
from labs.models import LabTest

# Create your views here.
def home(request):
    specializations = Specialization.objects.all()
    doctors = DoctorProfile.objects.all()
    lab_tests = LabTest.objects.all()
    context ={
        'specializations':specializations,
        'doctors': doctors,
        'lab_tests':lab_tests,
    }
    return render(request, 'index.html', context)