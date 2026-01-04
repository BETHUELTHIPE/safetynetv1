from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CrimeReport
from accounts.models import Profile # Assuming Profile is in accounts app
from .tasks import send_sms_alert
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

@receiver(post_save, sender=CrimeReport)
def crime_report_post_save(sender, instance, created, **kwargs):
    if created:
        message = f"New Crime Alert: {instance.title} at {instance.location} on {instance.date_reported.strftime('%Y-%m-%d %H:%M')}"
        # Send SMS to all users with a phone number
        for user in User.objects.all():
            if hasattr(user, 'profile') and user.profile.phone_number:
                send_sms_alert.delay(user.profile.phone_number, message)
        
        # Trigger dashboard alerts via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "crime_alerts",
            {
                "type": "send_alert",
                "message": message,
            }
        )
