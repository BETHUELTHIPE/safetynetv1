from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import ServiceListing, ServiceReview, ServiceInquiry, ServiceCategory

class ServiceListingForm(forms.ModelForm):
    """Form for creating and editing service listings"""
    
    # Custom validators
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+27812345678'. Up to 15 digits allowed."
    )
    
    # Override fields for better UI
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Service Title (e.g., "Professional Plumbing Services")'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe your service in detail, including what you offer, benefits, etc.',
            'rows': 5
        })
    )
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    subcategories = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., "Residential, Commercial, Emergency"'
        })
    )
    price_type = forms.ChoiceField(
        choices=ServiceListing._meta.get_field('price_type').choices,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    price_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Amount in ZAR',
            'min': '0',
            'step': '0.01'
        })
    )
    price_description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., "Starting from" or "Per hour"'
        })
    )
    experience_years = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Years of experience'
        })
    )
    qualifications = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'List your qualifications, certifications, or credentials',
            'rows': 3
        })
    )
    availability = forms.ChoiceField(
        choices=ServiceListing._meta.get_field('availability').choices,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    service_areas = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Areas where you provide your service (e.g., "Kings Park, Kwamhlanga, etc.")'
        })
    )
    contact_number = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+27812345678'
        })
    )
    whatsapp_number = forms.CharField(
        validators=[phone_regex],
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+27812345678'
        })
    )
    show_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com'
        })
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    gallery_image1 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    gallery_image2 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    gallery_image3 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    portfolio_pdf = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf'
        })
    )
    tags = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., "plumbing, repairs, 24/7"'
        })
    )
    
    class Meta:
        model = ServiceListing
        fields = [
            'title', 'description', 'category', 'subcategories',
            'price_type', 'price_amount', 'price_description',
            'experience_years', 'qualifications', 'availability', 'service_areas',
            'contact_number', 'whatsapp_number', 'show_email', 'website',
            'profile_image', 'gallery_image1', 'gallery_image2', 'gallery_image3', 'portfolio_pdf',
            'tags'
        ]
    
    def clean(self):
        """Validate price fields based on price type and ensure at least one contact method is provided"""
        cleaned_data = super().clean()
        price_type = cleaned_data.get('price_type')
        price_amount = cleaned_data.get('price_amount')
        
        # Validate price fields
        if price_type in ['FIXED', 'HOURLY'] and not price_amount:
            raise ValidationError({
                'price_amount': "Price amount is required for fixed price or hourly rate services."
            })
        
        # Check contact methods
        contact_number = cleaned_data.get('contact_number')
        whatsapp_number = cleaned_data.get('whatsapp_number')
        show_email = cleaned_data.get('show_email')
        
        if not contact_number and not whatsapp_number and not show_email:
            raise ValidationError(
                "You must provide at least one contact method (phone number, WhatsApp, or email)."
            )
        
        return cleaned_data
    
    def clean_portfolio_pdf(self):
        """Validate the portfolio PDF"""
        pdf = self.cleaned_data.get('portfolio_pdf')
        if pdf:
            if pdf.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError("PDF file too large. Maximum size is 10MB.")
            if not pdf.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
        return pdf
    
    def clean_profile_image(self):
        """Validate profile image size"""
        image = self.cleaned_data.get('profile_image')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image
    
    def clean_gallery_image1(self):
        """Validate gallery image 1 size"""
        image = self.cleaned_data.get('gallery_image1')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image
    
    def clean_gallery_image2(self):
        """Validate gallery image 2 size"""
        image = self.cleaned_data.get('gallery_image2')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image
    
    def clean_gallery_image3(self):
        """Validate gallery image 3 size"""
        image = self.cleaned_data.get('gallery_image3')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image


class ServiceReviewForm(forms.ModelForm):
    """Form for submitting service reviews"""
    
    rating = forms.ChoiceField(
        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
        widget=forms.RadioSelect(attrs={
            'class': 'rating-input'
        })
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share your experience with this service',
            'rows': 4
        })
    )
    
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment']


class ServiceInquiryForm(forms.ModelForm):
    """Form for sending inquiries about services"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your contact number'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your message or inquiry',
            'rows': 4
        })
    )
    
    class Meta:
        model = ServiceInquiry
        fields = ['name', 'email', 'phone', 'message']
