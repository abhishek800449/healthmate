from django import forms
from .models import Account
import re

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control floating'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control floating'}))
    
    class Meta:
        model = Account
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
