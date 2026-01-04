from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AlertCategory(models.Model):
    """Categories for community alerts"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fa-exclamation-triangle')  # FontAwesome icon name
    color = models.CharField(max_length=20, default='danger')  # Bootstrap color class
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Alert Categories'


class Alert(models.Model):
    """Community alert model for emergency notifications"""
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical - Immediate Action Required'),
        ('HIGH', 'High - Urgent Situation'),
        ('MEDIUM', 'Medium - Important Information'),
        ('LOW', 'Low - General Notification'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(AlertCategory, on_delete=models.CASCADE, related_name='alerts')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Area targeting
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    radius = models.IntegerField(help_text="Radius in meters", default=0) # 0 means broadcast to all
    
    # Alert options
    send_sms = models.BooleanField(default=False)
    send_email = models.BooleanField(default=True)
    send_push = models.BooleanField(default=False)
    
    # Creator and approval
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_alerts')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_alerts')
    is_approved = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        """Check if the alert is currently active"""
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return self.is_approved and not self.is_expired
    
    @property
    def is_expired(self):
        """Check if the alert has expired"""
        if self.expires_at and self.expires_at < timezone.now():
            return True
        return False
    
    class Meta:
        ordering = ['-created_at']


class AlertReceipt(models.Model):
    """Track which users have received alerts"""
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_receipts')
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    sent_via_push = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.alert} - {self.user}"
    
    class Meta:
        unique_together = ('alert', 'user')
        verbose_name_plural = 'Alert Receipts'
