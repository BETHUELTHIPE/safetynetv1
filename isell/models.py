from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class SaleItem(models.Model):
    """Model for items listed for sale"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SOLD', 'Sold'),
        ('EXPIRED', 'Expired'),
        ('REMOVED', 'Removed'),
    ]
    
    # Basic item information
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    negotiable = models.BooleanField(default=True)
    
    # Location and contact
    location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    show_email = models.BooleanField(default=False, help_text="Show your email to potential buyers")
    
    # Media uploads
    main_image = models.ImageField(upload_to='isell/images/', blank=True, null=True)
    additional_image1 = models.ImageField(upload_to='isell/images/', blank=True, null=True)
    additional_image2 = models.ImageField(upload_to='isell/images/', blank=True, null=True)
    video = models.FileField(upload_to='isell/videos/', blank=True, null=True)
    pdf_document = models.FileField(upload_to='isell/documents/', blank=True, null=True)
    
    # Categorization
    category = models.CharField(max_length=100, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated tags")
    
    # Metadata
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sale_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    featured = models.BooleanField(default=False)
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'
    
    def __str__(self):
        return f"{self.title} - R{self.price}"
    
    def is_active(self):
        return self.status == 'ACTIVE'
    
    def is_new(self):
        """Returns True if the listing is less than 3 days old"""
        return (timezone.now() - self.created_at).days < 3
    
    def get_absolute_url(self):
        return reverse('isell:item_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Set expiry date to 30 days from now if not provided
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)


class SavedItem(models.Model):
    """Model for items saved by users for later viewing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    item = models.ForeignKey(SaleItem, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-saved_at']
        
    def __str__(self):
        return f"{self.user.username} saved {self.item.title}"


class ItemMessage(models.Model):
    """Model for messages between buyers and sellers"""
    item = models.ForeignKey(SaleItem, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_item_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_item_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Message about {self.item.title} from {self.sender.username} to {self.recipient.username}"
