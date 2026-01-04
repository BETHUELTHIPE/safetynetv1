from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import SaleItem, ItemMessage

class SaleItemForm(forms.ModelForm):
    """Form for creating and editing sale items"""
    
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
            'placeholder': 'What are you selling?'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe your item in detail (condition, features, etc.)',
            'rows': 5
        })
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Price in ZAR',
            'min': '0',
            'step': '0.01'
        })
    )
    negotiable = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Where is the item located?'
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
    main_image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    additional_image1 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    additional_image2 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*'
        })
    )
    pdf_document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf'
        })
    )
    category = forms.ChoiceField(
        choices=[
            ('', 'Select Category'),
            ('Electronics', 'Electronics'),
            ('Furniture', 'Furniture'),
            ('Clothing', 'Clothing'),
            ('Vehicles', 'Vehicles'),
            ('Property', 'Property'),
            ('Services', 'Services'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    tags = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., used, good condition, delivery available'
        })
    )
    
    class Meta:
        model = SaleItem
        fields = [
            'title', 'description', 'price', 'negotiable',
            'location', 'contact_number', 'whatsapp_number', 'show_email',
            'main_image', 'additional_image1', 'additional_image2', 'video', 'pdf_document',
            'category', 'tags'
        ]
        
    def clean_main_image(self):
        """Validate that the main image is not too large"""
        main_image = self.cleaned_data.get('main_image')
        if main_image and main_image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return main_image
    
    def clean_additional_image1(self):
        """Validate that additional image 1 is not too large"""
        image = self.cleaned_data.get('additional_image1')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image
    
    def clean_additional_image2(self):
        """Validate that additional image 2 is not too large"""
        image = self.cleaned_data.get('additional_image2')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image
    
    def clean_video(self):
        """Validate that the video is not too large"""
        video = self.cleaned_data.get('video')
        if video and video.size > 50 * 1024 * 1024:  # 50MB
            raise ValidationError("Video file too large. Maximum size is 50MB.")
        return video
    
    def clean_pdf_document(self):
        """Validate that the PDF is not too large and is a PDF file"""
        pdf = self.cleaned_data.get('pdf_document')
        if pdf:
            if pdf.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError("PDF file too large. Maximum size is 10MB.")
            if not pdf.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
        return pdf
        
    def clean(self):
        """Make sure at least one contact method is provided"""
        cleaned_data = super().clean()
        contact_number = cleaned_data.get('contact_number')
        whatsapp_number = cleaned_data.get('whatsapp_number')
        show_email = cleaned_data.get('show_email')
        
        if not contact_number and not whatsapp_number and not show_email:
            raise ValidationError(
                "You must provide at least one contact method (phone number, WhatsApp, or email)."
            )
        
        return cleaned_data


class ItemMessageForm(forms.ModelForm):
    """Form for sending messages about items"""
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your message to the seller',
            'rows': 4
        })
    )
    
    class Meta:
        model = ItemMessage
        fields = ['message']
