from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile
from django.utils import timezone

class ProfileInline(admin.StackedInline):
    model = Profile
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Personal Information', {'fields': ('phone_number', 'id_number', 'address', 'bio', 'profile_image')}),
        ('Role and Verification', {'fields': ('role', 'is_verified', 'verification_status', 'verification_code', 'verification_expiry')}),
        ('Security', {'fields': ('last_login_ip', 'two_factor_enabled', 'failed_login_attempts', 'account_locked_until')}),
        ('Communication Preferences', {'fields': ('email_notifications', 'sms_notifications')}),
        ('Approvals', {'fields': ('is_approved', 'approved_by', 'approved_date', 'restriction_reason')}),
    )
    readonly_fields = ('verification_code', 'account_created', 'last_updated', 'last_login_ip')

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_verification_status')
    list_filter = BaseUserAdmin.list_filter + ('profile__role', 'profile__verification_status', 'profile__is_verified')
    search_fields = BaseUserAdmin.search_fields + ('profile__phone_number', 'profile__id_number')
    actions = ['approve_users', 'reject_users', 'verify_users', 'reset_failed_logins']
    
    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Role'
    
    def get_verification_status(self, obj):
        return obj.profile.get_verification_status_display()
    get_verification_status.short_description = 'Verification'
    
    def approve_users(self, request, queryset):
        for user in queryset:
            user.profile.is_approved = True
            user.profile.approved_by = request.user
            user.profile.approved_date = timezone.now()
            user.profile.save()
        self.message_user(request, f"{queryset.count()} user(s) were approved.")
    approve_users.short_description = "Approve selected users"
    
    def reject_users(self, request, queryset):
        for user in queryset:
            user.profile.is_approved = False
            user.profile.save()
        self.message_user(request, f"{queryset.count()} user(s) were rejected.")
    reject_users.short_description = "Reject selected users"
    
    def verify_users(self, request, queryset):
        for user in queryset:
            user.profile.is_verified = True
            user.profile.verification_status = 'VERIFIED'
            user.profile.save()
        self.message_user(request, f"{queryset.count()} user(s) were verified.")
    verify_users.short_description = "Verify selected users"
    
    def reset_failed_logins(self, request, queryset):
        for user in queryset:
            user.profile.failed_login_attempts = 0
            user.profile.account_locked_until = None
            user.profile.save()
        self.message_user(request, f"Reset failed login attempts for {queryset.count()} user(s).")
    reset_failed_logins.short_description = "Reset failed login attempts"

# Re-register UserAdmin with our custom admin class
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
