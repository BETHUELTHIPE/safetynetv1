from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Event(models.Model):
    """Model for community events that require admin approval."""

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    CATEGORY_CHOICES = [
        ('community', 'Community Meeting'),
        ('sports', 'Sports & Recreation'),
        ('education', 'Education & Training'),
        ('cultural', 'Cultural Event'),
        ('charity', 'Charity & Fundraising'),
        ('religious', 'Religious Event'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]

    # Basic event information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='community')

    # Event organizer
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')

    # Date and time
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    # Location
    venue = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    # Contact information
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # Additional details
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)

    # Media
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    flyer = models.FileField(upload_to='event_flyers/', null=True, blank=True)

    # Approval and status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_events')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date', '-start_time']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title} - {self.start_date}"

    def is_upcoming(self):
        """Check if the event is upcoming."""
        now = timezone.now()
        event_datetime = timezone.datetime.combine(self.start_date, self.start_time)
        event_datetime = timezone.make_aware(event_datetime)
        return event_datetime > now

    def is_ongoing(self):
        """Check if the event is currently ongoing."""
        now = timezone.now()
        start_datetime = timezone.make_aware(timezone.datetime.combine(self.start_date, self.start_time))

        if self.end_date and self.end_time:
            end_datetime = timezone.make_aware(timezone.datetime.combine(self.end_date, self.end_time))
        else:
            end_datetime = start_datetime

        return start_datetime <= now <= end_datetime

    def get_duration(self):
        """Get event duration in hours."""
        if self.end_date and self.end_time:
            start = timezone.datetime.combine(self.start_date, self.start_time)
            end = timezone.datetime.combine(self.end_date, self.end_time)
            duration = end - start
            return duration.total_seconds() / 3600  # Convert to hours
        return None

    @property
    def is_free(self):
        """Check if the event is free."""
        return self.ticket_price is None or self.ticket_price == 0


class EventRegistration(models.Model):
    """Model for event registrations."""

    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    attendee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    special_requirements = models.TextField(blank=True, null=True)
    number_of_attendees = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['event', 'attendee']
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'

    def __str__(self):
        return f"{self.attendee.username} - {self.event.title}"