from django import forms
from .models import CrimeReport

class CrimeReportForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = ['title', 'description', 'location', 'category', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title of the incident'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed description of the crime'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location of the incident'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude (e.g., -33.9249)', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude (e.g., 18.4241)', 'step': 'any'}),
        }

class CrimeReportUpdateForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = ['title', 'description', 'location', 'category', 'status', 'latitude', 'longitude', 'reporter']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title of the incident'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed description of the crime'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location of the incident'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude', 'step': 'any'}),
            'reporter': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Get the user from kwargs
        super().__init__(*args, **kwargs)

        # Disable fields for non-staff/non-admin users
        if user and hasattr(user, 'profile') and user.profile.role == 'CITIZEN':
            for field_name in ['status', 'category', 'latitude', 'longitude', 'title', 'description', 'location']:
                self.fields[field_name].widget.attrs['disabled'] = 'disabled'
