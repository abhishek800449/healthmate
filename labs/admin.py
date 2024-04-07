from django.contrib import admin
from .models import LabTest, LabTestBooking, PendingLabBooking

# Register your models here.

admin.site.register(LabTest)
admin.site.register(LabTestBooking)
admin.site.register(PendingLabBooking)