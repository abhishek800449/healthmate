from django.contrib import admin
from .models import User, DoctorProfile, PatientProfile, Specialization, MedicalRecord
# Register your models here.

class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'clinic_name','experience', 'registration_number', 'slug']
    prepopulated_fields = {'slug': ('registration_number',)}

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'created_by', 'date_created', 'date_updated']

admin.site.register(User)
admin.site.register(DoctorProfile, DoctorAdmin)
admin.site.register(PatientProfile)
admin.site.register(Specialization, SpecializationAdmin)
admin.site.register(MedicalRecord, MedicalRecordAdmin)


