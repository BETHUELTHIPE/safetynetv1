from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class BuyRequest(models.Model):
    """Model for buy requests posted by users"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('FULFILLED', 'Fulfilled'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    URGENCY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    # Basic request information
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='MEDIUM')
    
    # Contact information
    location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    show_email = models.BooleanField(default=False, help_text="Show your email to potential sellers")
    
    # Media uploads - for reference images
    reference_image = models.ImageField(upload_to='iwanttobuy/images/', blank=True, null=True)
    pdf_document = models.FileField(upload_to='iwanttobuy/documents/', blank=True, null=True)
    
    # Categorization
    category = models.CharField(max_length=100, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated tags")
    
    # Metadata
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buy_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Buy Request'
        verbose_name_plural = 'Buy Requests'
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def is_active(self):
        return self.status == 'ACTIVE'
    
    def is_new(self):
        """Returns True if the request is less than 3 days old"""
        return (timezone.now() - self.created_at).days < 3
    
    def get_absolute_url(self):
        return reverse('iwanttobuy:request_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Set expiry date to 30 days from now if not provided
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)


class BuyRequestResponse(models.Model):
    """Model for responses to buy requests"""
    buy_request = models.ForeignKey(BuyRequest, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buy_request_responses')
    message = models.TextField()
    price_offer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contact_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    # Optional image of the item being offered
    item_image = models.ImageField(upload_to='iwanttobuy/responses/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Response to {self.buy_request.title} from {self.responder.username}"
