from django.db import models
from accounts.models import DoctorProfile, PatientProfile
from appointment.models import Appointment
from labs.models import LabTestBooking

# Create your models here.

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    billing_address = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20)
    doctor_profile = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, null=True, blank=True)
    patient_profile = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100)
    issue_date = models.DateField(auto_now_add=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    lab = models.ForeignKey(LabTestBooking, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Order #{self.id}'