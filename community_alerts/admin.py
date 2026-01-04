from django.contrib import admin
from .models import Alert, AlertCategory, AlertReceipt

@admin.register(AlertCategory)
class AlertCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'severity', 'created_at', 'expires_at', 'is_approved', 'is_sent')
    list_filter = ('category', 'severity', 'is_approved', 'is_sent', 'created_at')
    search_fields = ('title', 'content', 'location')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'sent_at', 'created_by', 'approved_by')
    
    fieldsets = (
        ('Alert Content', {
            'fields': ('title', 'content', 'category', 'severity')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at', 'sent_at')
        }),
        ('Targeting', {
            'fields': ('location', 'latitude', 'longitude', 'radius')
        }),
        ('Notification Methods', {
            'fields': ('send_sms', 'send_email', 'send_push')
        }),
        ('Status', {
            'fields': ('is_approved', 'approved_by', 'is_sent', 'created_by')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        if obj.is_approved and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(AlertReceipt)
class AlertReceiptAdmin(admin.ModelAdmin):
    list_display = ('alert', 'user', 'sent_via_email', 'sent_via_sms', 'sent_via_push', 'viewed', 'viewed_at')
    list_filter = ('sent_via_email', 'sent_via_sms', 'sent_via_push', 'viewed')
    search_fields = ('alert__title', 'user__username', 'user__email')
    date_hierarchy = 'viewed_at'
