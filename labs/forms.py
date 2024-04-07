from django import forms
from .models import LabTestBooking

class LabTestBookingForm(forms.ModelForm):
    class Meta:
        model = LabTestBooking
        fields = ['lab_test', 'appointment_date', 'appointment_time', 'full_name', 'phone_number', 'address', 'city', 'zip_code']

    def __init__(self, *args, **kwargs):
        super(LabTestBookingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'