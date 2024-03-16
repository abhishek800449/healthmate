from django import forms
from .models import User, PatientProfile, Country, State, City, MedicalRecord
from appointment.models import TimeSlot
import re

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
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'dob', 'gender', 'address_line_1', 'city', 'state', 'country')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['dob'].widget.attrs['class'] = 'form-control datetimepicker'
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
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = PatientProfile
        fields = ('profile_picture','blood_group')

    def __init__(self, *args, **kwargs):
        super(PatientProfileForm, self).__init__(*args, **kwargs)
        self.fields['blood_group'].widget.attrs['class'] = 'form-control'
        self.fields['profile_picture'].widget.attrs['class'] = 'upload'

        
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['title', 'description', 'file_path']

    def __init__(self, *args, **kwargs):
        super(MedicalRecordForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['file_path'].widget.attrs['class'] = 'form-control'