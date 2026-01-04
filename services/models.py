from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class ServiceCategory(models.Model):
    """Model for service categories"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome icon class")
    
    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ServiceListing(models.Model):
    """Model for service listings offered by users"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('DISCONTINUED', 'Discontinued'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('ANYTIME', 'Anytime'),
        ('WEEKDAYS', 'Weekdays Only'),
        ('WEEKENDS', 'Weekends Only'),
        ('EVENINGS', 'Evenings Only'),
        ('LIMITED', 'Limited Availability'),
    ]
    
    # Basic service information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='services')
    subcategories = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated subcategories")
    
    # Pricing information
    price_type = models.CharField(max_length=20, choices=[
        ('FIXED', 'Fixed Price'),
        ('HOURLY', 'Hourly Rate'),
        ('VARIABLE', 'Variable/Quote Based'),
        ('FREE', 'Free')
    ], default='VARIABLE')
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_description = models.CharField(max_length=200, blank=True, null=True, help_text="E.g., 'Starting from' or 'Per hour'")
    
    # Service details
    experience_years = models.PositiveIntegerField(default=0)
    qualifications = models.TextField(blank=True, null=True)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='ANYTIME')
    service_areas = models.CharField(max_length=255, help_text="Areas where service is provided")
    
    # Contact information
    contact_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    show_email = models.BooleanField(default=False, help_text="Show your email to potential clients")
    website = models.URLField(blank=True, null=True)
    
    # Media uploads
    profile_image = models.ImageField(upload_to='services/profiles/', blank=True, null=True)
    gallery_image1 = models.ImageField(upload_to='services/gallery/', blank=True, null=True)
    gallery_image2 = models.ImageField(upload_to='services/gallery/', blank=True, null=True)
    gallery_image3 = models.ImageField(upload_to='services/gallery/', blank=True, null=True)
    portfolio_pdf = models.FileField(upload_to='services/portfolios/', blank=True, null=True)
    
    # Tags for better search
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated tags")
    
    # Metadata
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    featured = models.BooleanField(default=False)
    verified = models.BooleanField(default=False, help_text="Verified by admin")
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-featured', '-created_at']
        verbose_name = 'Service Listing'
        verbose_name_plural = 'Service Listings'
    
    def __str__(self):
        return f"{self.title} by {self.provider.username}"
    
    def is_active(self):
        return self.status == 'ACTIVE'
    
    def is_new(self):
        """Returns True if the listing is less than 7 days old"""
        return (timezone.now() - self.created_at).days < 7
    
    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'pk': self.pk})


class ServiceReview(models.Model):
    """Model for reviews of services"""
    service = models.ForeignKey(ServiceListing, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['service', 'reviewer']  # One review per service per user
    
    def __str__(self):
        return f"{self.get_rating_display()} review for {self.service.title}"


class ServiceInquiry(models.Model):
    """Model for inquiries about services"""
    service = models.ForeignKey(ServiceListing, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='service_inquiries')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Inquiry'
        verbose_name_plural = 'Service Inquiries'
    
    def __str__(self):
        return f"Inquiry about {self.service.title} from {self.name}"
