from django.contrib import admin
from .models import Appointment, TimeSlot, PendingAppointment

# Register your models here.

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day', 'start_time', 'end_time', 'is_available']

admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(Appointment)
admin.site.register(PendingAppointment)