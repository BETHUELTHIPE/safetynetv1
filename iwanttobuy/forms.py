from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import BuyRequest, BuyRequestResponse

class BuyRequestForm(forms.ModelForm):
    """Form for creating and editing buy requests"""
    
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
            'placeholder': 'What are you looking to buy?'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe what you\'re looking for in detail (brand, features, condition, etc.)',
            'rows': 5
        })
    )
    price_range_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum price (optional)',
            'min': '0',
            'step': '0.01'
        })
    )
    price_range_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum price (optional)',
            'min': '0',
            'step': '0.01'
        })
    )
    urgency = forms.ChoiceField(
        choices=BuyRequest.URGENCY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your location'
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
    reference_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
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
            'placeholder': 'e.g., used, good condition, specific brand'
        })
    )
    
    class Meta:
        model = BuyRequest
        fields = [
            'title', 'description', 'price_range_min', 'price_range_max', 'urgency',
            'location', 'contact_number', 'whatsapp_number', 'show_email',
            'reference_image', 'pdf_document', 'category', 'tags'
        ]
    
    def clean(self):
        """Make sure at least one contact method is provided and price range is valid"""
        cleaned_data = super().clean()
        contact_number = cleaned_data.get('contact_number')
        whatsapp_number = cleaned_data.get('whatsapp_number')
        show_email = cleaned_data.get('show_email')
        
        # Check contact methods
        if not contact_number and not whatsapp_number and not show_email:
            raise ValidationError(
                "You must provide at least one contact method (phone number, WhatsApp, or email)."
            )
        
        # Check price range
        min_price = cleaned_data.get('price_range_min')
        max_price = cleaned_data.get('price_range_max')
        
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError(
                "Minimum price cannot be greater than maximum price."
            )
        
        return cleaned_data
    
    def clean_reference_image(self):
        """Validate that the reference image is not too large"""
        image = self.cleaned_data.get('reference_image')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image
    
    def clean_pdf_document(self):
        """Validate that the PDF is not too large and is a PDF file"""
        pdf = self.cleaned_data.get('pdf_document')
        if pdf:
            if pdf.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError("PDF file too large. Maximum size is 10MB.")
            if not pdf.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
        return pdf


class BuyRequestResponseForm(forms.ModelForm):
    """Form for responding to buy requests"""
    
    # Custom validators
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+27812345678'. Up to 15 digits allowed."
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe what you have to offer',
            'rows': 4
        })
    )
    price_offer = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your asking price (optional)',
            'min': '0',
            'step': '0.01'
        })
    )
    contact_number = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+27812345678'
        })
    )
    item_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    class Meta:
        model = BuyRequestResponse
        fields = ['message', 'price_offer', 'contact_number', 'item_image']
    
    def clean_item_image(self):
        """Validate that the item image is not too large"""
        image = self.cleaned_data.get('item_image')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Image file too large. Maximum size is 5MB.")
        return image
