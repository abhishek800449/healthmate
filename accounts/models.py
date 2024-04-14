from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.urls import reverse
from django.utils import timezone
import os
from django.dispatch import receiver
from django.db.models import Avg, Count
from datetime import date
# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must enter Email Address')
        if not username:
            raise ValueError('Username must be entered')
        
        user =self.model(
            email=self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,  
            )
        
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_doctor(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
        user.profile_picture = 'userprofile/doctor_profile.png'
        user.save()
        # Creating doctor profile
        doctor_profile = DoctorProfile(user=user)
        doctor_profile.save()
        return user

    def create_patient(self, first_name, last_name, username, email, password=None, blood_group=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
        user.profile_picture = 'userprofile/patient_profile.png'
        user.save()
        # Creating patient profile
        patient_profile = PatientProfile(user=user, blood_group=blood_group)
        patient_profile.save()
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using = self._db)
        return user


class Country(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class User(AbstractBaseUser):
    GENDER = [("M", "Male"), ("F", "Female"), ("O", "Others")]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, blank=True, null=True)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')
    address_line_1 = models.CharField(blank=True, max_length=100)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
 
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_address(self):
        address_lines = [self.address_line_1,]
        address_lines = [line for line in address_lines if line]  # Remove empty lines
        address = ", ".join(address_lines)
        return f"{address}, {self.city}, {self.state}, {self.country}"
    
    def age(self):
        today = date.today()
        try:
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        except:
            return None
        
    def doc(self):
        try:
            doctor = DoctorProfile.objects.get(user=self)
            return doctor
        except:
            return None


class Specialization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True)
    image = models.ImageField(blank=True, upload_to='specialization')
    def __str__(self):
        return self.name
    def get_url(self):
        return reverse('doctors_by_specialization', args=[self.slug])

    
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    experience = models.PositiveIntegerField(null=True, blank=True, help_text="Years of experience")
    registration_number = models.CharField(max_length=20, null=True, blank=True, help_text="Doctor's registration number")
    about_me = models.TextField(blank=True, null=True)
    price = models.PositiveIntegerField(null=True)
    slug = models.SlugField(max_length=100, unique=True, null=True)

    def __str__(self):
        return self.user.first_name
    
    def get_url(self):
        return reverse('view_doctor', args=[self.specialization.slug, self.slug])
    
    def get_appointment_url(self):
        return reverse('book_appointment', args=[self.specialization.slug, self.slug])
    
    def checkout_url(self):
        return reverse('checkout', args=[self.slug])
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(doctor=self).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(doctor=self).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
    def rating_percentage(self):
        average_rating = self.averageReview()
        percentage = (average_rating / 5) * 100
        return round(percentage, 2)

    def clinic_address(self):
        clinic = Clinic.objects.get(doctor=self)
        return f"{clinic.clinic_name}, {clinic.address}, {clinic.clinic_city}, {clinic.clinic_state}, {clinic.clinic_country}"


class Clinic(models.Model):
    doctor = models.OneToOneField(DoctorProfile, on_delete=models.CASCADE, null=True)
    clinic_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(blank=True, max_length=100)
    clinic_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    clinic_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    clinic_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.clinic_name   

    def get_clinic_address(self):
        address_parts = [self.clinic_name, self.address, self.clinic_city.name, self.clinic_state.name, self.clinic_country.name]
        return ', '.join(filter(None, address_parts))


class PatientProfile(models.Model):
    BLOOD_GROUPS = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True, null=True)

    def __str__(self):
        return self.user.first_name
    
    def get_url(self):
        return reverse('view_patient', args=[self.user.username])
    

class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    file_path = models.FileField(upload_to='uploads/',blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
@receiver(models.signals.post_delete, sender=MedicalRecord)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file_path:
        if os.path.isfile(instance.file_path.path):
            os.remove(instance.file_path.path)

@receiver(models.signals.pre_save, sender=MedicalRecord)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file_path
    except sender.DoesNotExist:
        return False

    new_file = instance.file_path
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class ReviewRating(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class ClinicGallery(models.Model):
    clinic = models.ForeignKey(Clinic, default=None, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='clinic_images/', null=True, blank=True)

    def __str__(self):
        return self.clinic.clinic_name
    

class Prescription(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    signature = models.ImageField(upload_to='signatures/')
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"Prescription#{self.id}"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    days = models.IntegerField()
    morning = models.BooleanField(default=False)
    afternoon = models.BooleanField(default=False)
    evening = models.BooleanField(default=False)
    night = models.BooleanField(default=False)