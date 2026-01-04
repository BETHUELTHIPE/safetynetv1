from django import forms
from django.utils import timezone
from .models import Event, EventRegistration

class EventForm(forms.ModelForm):
    """Form for creating and editing events."""

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'start_date', 'start_time',
            'end_date', 'end_time', 'venue', 'address', 'contact_person',
            'contact_email', 'contact_phone', 'max_attendees', 'ticket_price',
            'registration_required', 'registration_deadline', 'image', 'flyer'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your event...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Venue name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Full address'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact person name'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+27 XX XXX XXXX'
            }),
            'max_attendees': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'ticket_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'registration_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'registration_deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'flyer': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_required = cleaned_data.get('registration_required')
        registration_deadline = cleaned_data.get('registration_deadline')

        # Validate dates
        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError('Event start date cannot be in the past.')

        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError('Event end date cannot be before start date.')

        # Validate registration deadline
        if registration_required and not registration_deadline:
            raise forms.ValidationError('Registration deadline is required when registration is required.')

        if registration_deadline and start_date:
            deadline_date = registration_deadline.date()
            if deadline_date > start_date:
                raise forms.ValidationError('Registration deadline cannot be after the event start date.')

        return cleaned_data


class EventRegistrationForm(forms.ModelForm):
    """Form for registering for events."""

    class Meta:
        model = EventRegistration
        fields = ['number_of_attendees', 'special_requirements']
        widgets = {
            'number_of_attendees': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or notes...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

    def clean_number_of_attendees(self):
        number_of_attendees = self.cleaned_data.get('number_of_attendees')
        if self.event and self.event.max_attendees:
            current_registrations = self.event.registrations.filter(status='registered').count()
            if current_registrations + number_of_attendees > self.event.max_attendees:
                raise forms.ValidationError(
                    f'Only {self.event.max_attendees - current_registrations} spots remaining.'
                )
        return number_of_attendees
