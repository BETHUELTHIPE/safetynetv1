from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class BusinessService(models.Model):
    """Model for business service listings."""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Basic service information
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.CharField(max_length=100, help_text="e.g., '2 days', '1 week', '3 hours'")
    people_needed = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Contact information
    whatsapp_number = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=20)
    
    # Location information
    location = models.CharField(max_length=255)
    
    # Media uploads
    photo = models.ImageField(upload_to='piecejobs/photos/', blank=True, null=True)
    pdf_document = models.FileField(upload_to='piecejobs/pdfs/', blank=True, null=True)
    video = models.FileField(upload_to='piecejobs/videos/', blank=True, null=True)
    
    # Metadata
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    # Job category (for filtering)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Business Service'
        verbose_name_plural = 'Business Services'
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def is_active(self):
        return self.status == 'OPEN'
    
    def days_since_posted(self):
        days = (timezone.now() - self.created_at).days
        return days


class ServiceApplication(models.Model):
    """Model for business service applications submitted by users."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    service = models.ForeignKey(BusinessService, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_applications')
    message = models.TextField()
    contact_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Application'
        verbose_name_plural = 'Service Applications'
        
    def __str__(self):
        return f"{self.applicant.username} - {self.service.title} ({self.get_status_display()})"
