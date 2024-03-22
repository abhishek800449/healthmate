from django.db import models
from accounts.models import PatientProfile, Specialization
# Create your models here.

class RoomDetails(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)