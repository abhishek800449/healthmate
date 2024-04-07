from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LabTest
from .forms import LabTestBookingForm
from django.http import JsonResponse

# Create your views here.

@login_required(login_url='login')
def booking_test(request):
    lab_form = LabTestBookingForm()
    context = {
        'lab_form': lab_form,
    }
    return  render(request, 'labs/booking_test.html', context)


def get_test_details(request):
    lab_test_id = request.GET.get('lab_test_id')
    if lab_test_id:
        lab_test = LabTest.objects.get(id=lab_test_id)
        test_details = {'id': lab_test.id, 'name': lab_test.name, 'description': lab_test.description, 'image': lab_test.image.url, 'price':lab_test.price}
        return JsonResponse(test_details)
    return JsonResponse({'error': 'Invalid request'})