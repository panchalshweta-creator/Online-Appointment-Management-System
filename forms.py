from django import forms
from .models import Appointment, Profile, CustomUser, Service, ContactMessage

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        # Exclude client, service and status as they will be set by the view
        fields = ['availability_slot', 'notes']
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['business_name', 'category', 'description', 'address', 'phone', 'email', 'business_hours', 'profile_image'] 

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration']

class CustomUserForm(forms.ModelForm): # This form is currently not used in views, but good to have for profile management
    class Meta:
        model = CustomUser
        fields = ['username', 'email'] # Exclude password and role for this generic user form

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
