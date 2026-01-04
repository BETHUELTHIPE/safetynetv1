from django import forms
from .models import Alert, AlertCategory

class AlertForm(forms.ModelForm):
    """Form for creating and editing community alerts"""
    # Add a field for immediate sending
    send_now = forms.BooleanField(
        required=False, 
        initial=False,
        label="Send immediately after creation",
        help_text="If checked, the alert will be sent to all eligible users right away."
    )
    
    class Meta:
        model = Alert
        fields = ['title', 'content', 'category', 'severity', 'expires_at', 
                  'location', 'latitude', 'longitude', 'radius',
                  'send_sms', 'send_email', 'send_push']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alert title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Alert details'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location description'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'radius': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields not required
        self.fields['expires_at'].required = False
        self.fields['location'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        
        # Add help texts
        self.fields['severity'].help_text = "Higher severity alerts may be displayed more prominently."
        self.fields['expires_at'].help_text = "When this alert should expire. Leave blank for no expiration."
        self.fields['radius'].help_text = "Distance in meters. Set to 0 to notify everyone regardless of location."
        self.fields['send_sms'].help_text = "Send this alert via SMS to users who have opted in."
        self.fields['send_email'].help_text = "Send this alert via email to users who have opted in."
        self.fields['send_push'].help_text = "Send this alert as a push notification (requires mobile app)."
