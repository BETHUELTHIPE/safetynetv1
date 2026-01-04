from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

class Profile(models.Model):
    """Extended user profile model with additional information."""
    
    USER_ROLES = [
        ('CITIZEN', 'Citizen'),
        ('POLICE_OFFICER', 'Police Officer'),
        ('ADMIN', 'Admin'),
        ('CPF_MEMBER', 'CPF Member'),
        ('COMMUNITY_LEADER', 'Community Leader'),
    ]
    
    VERIFICATION_STATUS = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Basic profile fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='CITIZEN')
    
    # Additional identity information
    id_number = models.CharField(max_length=13, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Account verification
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS, default='PENDING')
    verification_code = models.UUIDField(default=uuid.uuid4, editable=False)
    verification_expiry = models.DateTimeField(blank=True, null=True)
    
    # Security and tracking
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    account_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    two_factor_enabled = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    
    # Communications preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    # Permissions and restrictions
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_profiles')
    approved_date = models.DateTimeField(blank=True, null=True)
    restriction_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def lock_account(self, minutes=30):
        """Lock account for specified minutes due to suspicious activity."""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save()
    
    def unlock_account(self):
        """Unlock a previously locked account."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save()
    
    def is_locked(self):
        """Check if account is currently locked."""
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        elif self.account_locked_until:
            self.unlock_account()
            return False
        return False
    
    def record_login_attempt(self, successful, ip_address=None):
        """Record login attempt and take appropriate action."""
        if successful:
            self.failed_login_attempts = 0
            self.last_login_ip = ip_address
            self.save()
        else:
            self.failed_login_attempts += 1
            # Lock account after 5 failed attempts
            if self.failed_login_attempts >= 5:
                self.lock_account()
            self.save()
    
    def create_verification_code(self):
        """Create a new verification code and set expiry."""
        self.verification_code = uuid.uuid4()
        self.verification_expiry = timezone.now() + timezone.timedelta(days=3)
        self.save()
        return self.verification_code


# Signal to create/update user profile automatically
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
    instance.profile.save()
