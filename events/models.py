from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Event(models.Model):
    """Model for community events in Kingsapark."""

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    EVENT_TYPES = [
        ('community', 'Community Event'),
        ('sports', 'Sports & Recreation'),
        ('cultural', 'Cultural Celebration'),
        ('educational', 'Educational Workshop'),
        ('religious', 'Religious Gathering'),
        ('charity', 'Charity & Fundraiser'),
        ('meeting', 'Community Meeting'),
        ('other', 'Other'),
    ]

    # Basic Event Information
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(help_text="Detailed description of the event")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='community')

    # Date and Time
    start_date = models.DateField(help_text="Event start date")
    start_time = models.TimeField(help_text="Event start time")
    end_date = models.DateField(help_text="Event end date")
    end_time = models.TimeField(help_text="Event end time")

    # Location
    venue = models.CharField(max_length=200, help_text="Event venue/location")
    address = models.TextField(blank=True, help_text="Full address details")

    # Contact Information
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    contact_phone = models.CharField(max_length=20, help_text="Contact phone number")
    contact_email = models.EmailField(help_text="Contact email address")

    # Event Details
    max_attendees = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum number of attendees")
    registration_required = models.BooleanField(default=False, help_text="Does this event require registration?")
    registration_deadline = models.DateTimeField(blank=True, null=True, help_text="Registration deadline")

    # Media
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True, help_text="Event poster image")
    additional_images = models.ImageField(upload_to='event_images/', blank=True, null=True)

    # Approval and Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_events')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True, help_text="Notes from the approver")

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False, help_text="Feature this event on homepage")

    class Meta:
        ordering = ['-start_date', '-start_time']
        verbose_name = 'Kingsapark Event'
        verbose_name_plural = 'Kingsapark Events'

    def __str__(self):
        return f"{self.title} - {self.start_date}"

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    @property
    def is_upcoming(self):
        """Check if event is in the future."""
        event_datetime = timezone.datetime.combine(self.start_date, self.start_time)
        return event_datetime > timezone.now()

    @property
    def is_ongoing(self):
        """Check if event is currently happening."""
        now = timezone.now()
        start_datetime = timezone.datetime.combine(self.start_date, self.start_time)
        end_datetime = timezone.datetime.combine(self.end_date, self.end_time)
        return start_datetime <= now <= end_datetime

    @property
    def is_past(self):
        """Check if event has already occurred."""
        end_datetime = timezone.datetime.combine(self.end_date, self.end_time)
        return end_datetime < timezone.now()

    def can_user_edit(self, user):
        """Check if user can edit this event."""
        return user == self.organizer or user.is_staff

    def approve(self, user):
        """Approve the event."""
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def reject(self, user, notes=""):
        """Reject the event."""
        self.status = 'rejected'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save()


class EventRegistration(models.Model):
    """Model for event registrations."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    attendee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(default=timezone.now)
    attendance_confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="Additional notes or special requirements")

    class Meta:
        unique_together = ['event', 'attendee']
        ordering = ['registered_at']
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'

    def __str__(self):
        return f"{self.attendee.get_full_name()} - {self.event.title}"