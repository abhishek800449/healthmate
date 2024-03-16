from django.shortcuts import render
from accounts.models import Specialization

# Create your views here.
def home(request):
    specializations = Specialization.objects.all()
    context ={
        'specializations':specializations,
    }
    return render(request, 'index.html', context)