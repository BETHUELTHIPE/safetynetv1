from django import forms
from django.core.validators import RegexValidator, MinValueValidator
from .models import BusinessService

class BusinessServiceForm(forms.ModelForm):
    """Form for creating and editing business services."""
    
    # Custom validators
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+27812345678'. Up to 15 digits allowed."
    )
    
    # Override fields for better UI
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Title'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Detailed service description', 'rows': 5})
    )
    duration = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2 days, 1 week, 3 hours'})
    )
    people_needed = forms.IntegerField(
        initial=1,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    offer_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in ZAR', 'step': '0.01'})
    )
    whatsapp_number = forms.CharField(
        max_length=20,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+27812345678'})
    )
    contact_number = forms.CharField(
        max_length=20,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+27812345678'})
    )
    location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address or area'})
    )
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    pdf_document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'})
    )
    video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'})
    )
    category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Construction, Gardening, Cleaning'})
    )
    
    class Meta:
        model = BusinessService
        fields = [
            'title', 'description', 'duration', 'people_needed', 
            'offer_price', 'whatsapp_number', 'contact_number', 
            'location', 'photo', 'pdf_document', 'video', 'category'
        ]
        
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure at least one contact method is provided
        whatsapp = cleaned_data.get('whatsapp_number')
        contact = cleaned_data.get('contact_number')
        if not (whatsapp or contact):
            raise forms.ValidationError("At least one contact method (WhatsApp or phone number) is required.")
            
        return cleaned_data
        
    def clean_pdf_document(self):
        pdf = self.cleaned_data.get('pdf_document')
        if pdf and not pdf.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        # 5MB file size limit
        if pdf and pdf.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 5MB.")
        return pdf
        
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # 2MB file size limit
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image size must be under 2MB.")
        return photo
        
    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            # 50MB file size limit
            if video.size > 50 * 1024 * 1024:
                raise forms.ValidationError("Video size must be under 50MB.")
        return video
