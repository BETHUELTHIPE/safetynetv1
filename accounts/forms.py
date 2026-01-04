from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    """Enhanced user registration form with additional fields and validations."""
    
    # Custom field validations
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+123456789'. Up to 15 digits allowed."
    )
    
    # Form fields
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone_number = forms.CharField(
        validators=[phone_regex], 
        max_length=17, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (e.g., +27820001234)'})
    )
    id_number = forms.CharField(
        max_length=13, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Number'})
    )
    address = forms.CharField(
        max_length=255, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Physical Address'})
    )
    role = forms.ChoiceField(
        choices=Profile.USER_ROLES,
        required=True,
        initial='CITIZEN',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    terms_agreement = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms and Conditions and Privacy Policy',
        error_messages={'required': 'You must agree to the terms to register'}
    )
    
    # Override UserCreationForm fields to add custom widgets
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'id_number', 'role', 'password1', 'password2', 'terms_agreement']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        # Add South African ID validation logic
        if len(id_number) != 13 or not id_number.isdigit():
            raise forms.ValidationError("Please enter a valid 13-digit ID number.")
        return id_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create or update profile with additional fields
            user.profile.phone_number = self.cleaned_data['phone_number']
            user.profile.role = self.cleaned_data['role']
            
            # Add custom fields to profile
            if not hasattr(user.profile, 'address'):
                user.profile.address = self.cleaned_data['address']
            else:
                user.profile.address = self.cleaned_data['address']
                
            if not hasattr(user.profile, 'id_number'):
                user.profile.id_number = self.cleaned_data['id_number']
            else:
                user.profile.id_number = self.cleaned_data['id_number']
                
            user.profile.save()
        
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form with custom styling."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )

    error_messages = {
        'invalid_login': "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive. Please contact support for assistance.",
    }


class CustomPasswordResetForm(PasswordResetForm):
    """Enhanced password reset form with custom styling."""
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Enhanced set password form with custom styling."""
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        }),
    )
