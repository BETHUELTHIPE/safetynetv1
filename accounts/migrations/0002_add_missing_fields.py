# Generated manually to fix missing fields

from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add id_number field
        migrations.AddField(
            model_name='profile',
            name='id_number',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        # Add address field
        migrations.AddField(
            model_name='profile',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        # Add profile_image field
        migrations.AddField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images/'),
        ),
        # Add bio field
        migrations.AddField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        # Add is_verified field
        migrations.AddField(
            model_name='profile',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        # Add verification_status field
        migrations.AddField(
            model_name='profile',
            name='verification_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10),
        ),
        # Add verification_code field
        migrations.AddField(
            model_name='profile',
            name='verification_code',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        # Add verification_expiry field
        migrations.AddField(
            model_name='profile',
            name='verification_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add last_login_ip field
        migrations.AddField(
            model_name='profile',
            name='last_login_ip',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        # Add account_created field
        migrations.AddField(
            model_name='profile',
            name='account_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Add last_updated field
        migrations.AddField(
            model_name='profile',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add two_factor_enabled field
        migrations.AddField(
            model_name='profile',
            name='two_factor_enabled',
            field=models.BooleanField(default=False),
        ),
        # Add failed_login_attempts field
        migrations.AddField(
            model_name='profile',
            name='failed_login_attempts',
            field=models.IntegerField(default=0),
        ),
        # Add account_locked_until field
        migrations.AddField(
            model_name='profile',
            name='account_locked_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add email_notifications field
        migrations.AddField(
            model_name='profile',
            name='email_notifications',
            field=models.BooleanField(default=True),
        ),
        # Add sms_notifications field
        migrations.AddField(
            model_name='profile',
            name='sms_notifications',
            field=models.BooleanField(default=True),
        ),
        # Add is_approved field
        migrations.AddField(
            model_name='profile',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        # Add approved_by field
        migrations.AddField(
            model_name='profile',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_profiles', to=settings.AUTH_USER_MODEL),
        ),
        # Add approved_date field
        migrations.AddField(
            model_name='profile',
            name='approved_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add restriction_reason field
        migrations.AddField(
            model_name='profile',
            name='restriction_reason',
            field=models.TextField(blank=True, null=True),
        ),
        # Update role choices to include all options
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('CITIZEN', 'Citizen'), ('POLICE_OFFICER', 'Police Officer'), ('ADMIN', 'Admin'), ('CPF_MEMBER', 'CPF Member'), ('COMMUNITY_LEADER', 'Community Leader')], default='CITIZEN', max_length=20),
        ),
    ]
