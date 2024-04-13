from django import forms
from .models import LabTestBooking, LabTest
from django.utils import timezone

class LabTestBookingForm(forms.ModelForm):
    appointment_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date", "class": "form-control", "min": timezone.now().date()}))
    appointment_time = forms.TimeField(widget=forms.TextInput(attrs={"type": "time", "class": "form-control",}))
    class Meta:
        model = LabTestBooking
        fields = ['lab_test', 'appointment_date', 'appointment_time', 'full_name', 'phone_number', 'address', 'city', 'zip_code']

    def __init__(self, *args, **kwargs):
        super(LabTestBookingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['name', 'description', 'image', 'price']

    def __init__(self, *args, **kwargs):
        super(LabTestForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'