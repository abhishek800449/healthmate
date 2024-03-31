from django.db import models
from accounts.models import PatientProfile, DoctorProfile
# Create your models here.
from django.db import models

class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='pending')
    type = models.CharField(max_length=20, null=True)


class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)


class PendingAppointment(models.Model):
    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    billing_address = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20)
    doctor_profile = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient_profile = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100)
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id}'