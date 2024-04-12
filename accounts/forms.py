from django import forms
from .models import User, PatientProfile, DoctorProfile, Country, State, City, MedicalRecord, Clinic, ClinicGallery
from appointment.models import TimeSlot
import re
from django.utils.text import slugify

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control floating'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control floating'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control floating'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        phone_number = self.cleaned_data.get('phone_number')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if not first_name.isalpha():
            raise forms.ValidationError("First name should contain only letters!")

        if not last_name.isalpha():
            raise forms.ValidationError("Last name should contain only letters!")
        
        if not re.match(r'^\d{10}$', phone_number):
            raise forms.ValidationError("Phone number must be in a valid format (10 digits).")
        
        if password != confirm_password:
            raise forms.ValidationError("Password does not match!")
        
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise forms.ValidationError("Password should be at least 8 characters and contain a combination of uppercase, lowercase, digits, and special symbols!")


class UserForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    dob = forms.DateField(required=False, widget=forms.TextInput(attrs={"type": "date", "class": "form-control",}))
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'dob', 'gender', 'profile_picture', 'address_line_1', 'city', 'state', 'country')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        self.fields['profile_picture'].widget.attrs['class'] = 'upload'
        # Adjust foreign key fields
        self.fields['country'].queryset = Country.objects.all()
        self.fields['state'].queryset = State.objects.none()  # Initially no states
        self.fields['city'].queryset = City.objects.none()    # Initially no cities

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id)
            except (ValueError, TypeError):
                pass
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        phone_number = self.cleaned_data.get('phone_number')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if not first_name.isalpha():
            raise forms.ValidationError("First name should contain only letters!")

        if not last_name.isalpha():
            raise forms.ValidationError("Last name should contain only letters!")
        
        if not re.match(r'^\d{10}$', phone_number):
            raise forms.ValidationError("Phone number must be in a valid format (10 digits).")


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ('blood_group',)

    def __init__(self, *args, **kwargs):
        super(PatientProfileForm, self).__init__(*args, **kwargs)
        self.fields['blood_group'].widget.attrs['class'] = 'form-control'

        
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['title', 'description', 'file_path']

    def __init__(self, *args, **kwargs):
        super(MedicalRecordForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = '4'
        self.fields['file_path'].widget.attrs['class'] = 'form-control'


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ('clinic_name', 'address', 'clinic_country', 'clinic_state', 'clinic_city')
        
    def __init__(self, *args, **kwargs):
        super(ClinicForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        # Adjust foreign key fields
        self.fields['clinic_country'].queryset = Country.objects.all()
        self.fields['clinic_state'].queryset = State.objects.none()  # Initially no states
        self.fields['clinic_city'].queryset = City.objects.none()    # Initially no cities

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('clinic_country'))
                self.fields['clinic_state'].queryset = State.objects.filter(country_id=country_id)
            except (ValueError, TypeError):
                pass
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('clinic_state'))
                self.fields['clinic_city'].queryset = City.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                pass


class ClinicGalleryForm(forms.ModelForm):
    images = forms.FileField(required=False, widget = forms.TextInput(attrs={
            "type": "File",
            "class": "form-control",
            "multiple": "True",
        }))
    
    class Meta:
        model = ClinicGallery
        fields = ['images']


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ('specialization', 'experience', 'registration_number', 'about_me', 'price')

    def __init__(self, *args, **kwargs):
        super(DoctorProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        instance = super(DoctorProfileForm, self).save(commit=False)
        instance.slug = slugify(instance.registration_number)  # Set slug based on registration_number
        if commit:
            instance.save()
        return instance